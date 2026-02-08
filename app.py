from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess
import sys
import tempfile
import bcrypt
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# AI: Groq (free tier) or OpenAI. Key can come from env, request body (api_key), or login (ALLOWED_USERS → env key).
GROQ_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.1-8b-instant"
OPENAI_MODEL = "gpt-4o-mini"

def get_ai_client(api_key=None):
    """Return (OpenAI client, model). Prefer given api_key, then GROQ_API_KEY, then OPENAI_API_KEY."""
    if api_key and api_key.strip():
        return OpenAI(api_key=api_key.strip(), base_url=GROQ_BASE), GROQ_MODEL
    if os.getenv("GROQ_API_KEY"):
        return OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url=GROQ_BASE), GROQ_MODEL
    if os.getenv("OPENAI_API_KEY"):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY")), OPENAI_MODEL
    return None, None

def get_allowed_users():
    """Parse ALLOWED_USERS env: JSON array of {username_hash, password_hash} or legacy {username, password_hash}."""
    raw = os.getenv("ALLOWED_USERS")
    if not raw or not raw.strip():
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []

def verify_login(username, password):
    """Return True if username/password match an entry. Supports username_hash (SHA-256) or plain username."""
    import hashlib
    users = get_allowed_users()
    username_hash = hashlib.sha256(username.encode("utf-8")).hexdigest() if username else ""
    for u in users:
        match = False
        if u.get("username_hash"):
            match = u.get("username_hash") == username_hash
        else:
            match = (u.get("username") or u.get("user")) == username
        if match:
            ph = u.get("password_hash") or u.get("passwordHash")
            if ph and password:
                try:
                    return bcrypt.checkpw(password.encode("utf-8"), ph.encode("utf-8"))
                except Exception:
                    return False
    return False

# Store loaded exercises
exercises = {}

def load_exercise(file_path):
    """Load an exercise from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            exercise_data = json.load(f)
            exercise_id = exercise_data.get('id', os.path.basename(file_path).replace('.json', ''))
            exercises[exercise_id] = exercise_data
            return exercise_id
    except Exception as e:
        print(f"Error loading exercise from {file_path}: {e}")
        return None

def load_exercises_from_directory(directory='docs/exercises'):
    """Load all exercises from a directory (shared with GitHub Pages static site)."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return []
    loaded = []
    for filename in os.listdir(directory):
        if filename.endswith('.json') and filename != 'manifest.json':
            exercise_id = load_exercise(os.path.join(directory, filename))
            if exercise_id:
                loaded.append(exercise_id)
    return loaded

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/exercises', methods=['GET'])
def get_exercises():
    """Get list of all available exercises"""
    exercise_list = []
    for exercise_id, exercise_data in exercises.items():
        exercise_list.append({
            'id': exercise_id,
            'title': exercise_data.get('title', 'Untitled Exercise'),
            'description': exercise_data.get('description', '')
        })
    return jsonify(exercise_list)

@app.route('/api/exercises/<exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """Get a specific exercise (no grading_instructions sent to frontend)"""
    if exercise_id not in exercises:
        return jsonify({'error': 'Exercise not found'}), 404
    ex = exercises[exercise_id].copy()
    ex.pop("grading_instructions", None)
    return jsonify(ex)


@app.route('/api/exercises/<exercise_id>/grade', methods=['POST'])
def grade_exercise(exercise_id):
    """Grade a student's answer using AI. Auth: request body can send api_key, or username+password (uses server GROQ key)."""
    if exercise_id not in exercises:
        return jsonify({'error': 'Exercise not found'}), 404

    data = request.get_json() or {}
    student_answer = (data.get('answer') or '').strip()
    if not student_answer:
        return jsonify({'error': 'No answer provided'}), 400

    # Resolve which API key to use: (1) body api_key (user's own), (2) username+password → server GROQ key for all logged-in students, (3) server env key
    api_key = (data.get('api_key') or data.get('apiKey') or '').strip()
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '')

    if username and password:
        if not verify_login(username, password):
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
        api_key = None  # all logged-in users (ALLOWED_USERS) use server's GROQ_API_KEY

    client, model = get_ai_client(api_key)
    if not client:
        return jsonify({
            'success': False,
            'error': 'No API key. Enter your Groq API key below, or log in with a teacher account.'
        }), 503

    ex = exercises[exercise_id]
    question = ex.get('question', '')
    grading_instructions = ex.get('grading_instructions', '')

    # First, check if code compiles and runs
    execution_result = None
    syntax_error = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(student_answer)
            temp_path = f.name
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', temp_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                syntax_error = result.stderr or "Syntax error detected"
            else:
                # Code compiles, try running it to see output
                run_result = subprocess.run(
                    [sys.executable, temp_path],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
                )
                execution_result = {
                    'stdout': run_result.stdout or '',
                    'stderr': run_result.stderr or '',
                    'exit_code': run_result.returncode,
                }
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    except Exception as e:
        syntax_error = f"Error checking code: {str(e)}"

    # Build improved prompt with execution context
    execution_context = ""
    if syntax_error:
        execution_context = f"\n⚠️ SYNTAX ERROR DETECTED:\n{syntax_error}\n\nThis code has syntax errors and will not run. Score should be 0-20."
    elif execution_result:
        has_output = bool(execution_result.get('stdout', '').strip())
        execution_context = f"\n✅ CODE EXECUTION RESULT:\nExit Code: {execution_result['exit_code']}\n"
        if execution_result.get('stdout'):
            execution_context += f"Output:\n{execution_result['stdout']}\n"
            if not has_output:
                execution_context += "\n⚠️ WARNING: Code ran but produced NO output. If the exercise requires print statements, this is a problem.\n"
        if execution_result.get('stderr'):
            execution_context += f"Errors:\n{execution_result['stderr']}\n"
        # Check if print statements exist in code
        if 'print' not in student_answer.lower():
            execution_context += "\n⚠️ WARNING: No 'print' statements found in the code. If the exercise requires printing, this requirement is MISSING.\n"

    prompt = f"""You are a Python programming tutor grading a student's answer. Grade based ONLY on the code below. Apply general programming semantics to ANY exercise.

STUDENT'S CODE:
---
{student_answer}
---
{execution_context}

EXERCISE QUESTION:
{question}

GRADING INSTRUCTIONS:
{grading_instructions}

---
UNIVERSAL PRINCIPLE (apply to every exercise):
When a requirement says to "print" or "use" variables with "descriptive labels", two things must be true:
(1) The variable NAME must appear in the print (e.g. {{name}}, {{age}}, {{height}}) — not a literal like "Merlin" or 16.
(2) "Descriptive label" means ANY surrounding text that gives context — e.g. "My name is", "I am", "years old", "stand", "m tall". The student does NOT need one specific phrase. All of these COUNT as descriptive and MET: print(f"My name is {{name}},"), print(f"I am {{age}} years old"), print(f"and I stand {{height}}m tall.").

DO NOT claim "age" or "height" are "missing descriptive labels" when the code has print(f"I am {{age}} years old") or print(f"and I stand {{height}}m tall."). That is FALSE — those lines clearly have descriptive text. Only mark NOT MET when the variable is missing (literal used instead) or there is no context at all (e.g. just print(age)).
---

BEFORE GRADING:
1. List which variables the exercise asks to create/use.
2. For each, check: is that variable name actually used later (e.g. in print, in expressions), or did the student write literal values instead? If literals are used where the variable should be, mark that requirement NOT MET.
3. Only then assign score and write feedback.

RULES:
- If variables are defined but output uses literals instead of those variables (e.g. print(f"My name is Merlin") instead of {{name}}), the requirement is NOT met. Score below 70.
- If the code uses the variables ({{name}}, {{age}}, {{height}}) in print with ANY descriptive text (e.g. "I am {{age}} years old", "stand {{height}}m tall"), that requirement IS MET. Do NOT say it is missing or "not fully met".
- Do NOT invent missing requirements. Do NOT say "age and height are missing descriptive labels" when the code has print(f"I am {{age}} years old") and print(f"and I stand {{height}}m tall") — that is incorrect. Only mark missing what is actually wrong.
- Do not suggest adding something that is already there.

SCORING (apply strictly — do not be lenient):
- PERFECT (all requirements fully met, no issues): Give 95–100. Prefer 100 for clearly perfect code. Do NOT cap at 90.
- ANY requirement missing or wrong: Score MUST be at most 65. Never give 70 or above when a requirement is not met. passed MUST be false.
- One critical requirement missing (e.g. not using variables in output): 45–65 max.
- Two or more requirements missing: 20–40 max.
- Syntax errors: 0–20.
So: missing requirement ⇒ score ≤ 65 ⇒ FAIL. Perfect code ⇒ score 95–100.

FEEDBACK: Friendly, specific. For critical mistakes (e.g. literals instead of variables), say clearly that this is why they did not pass and what to fix.

SUGGESTIONS: Only for what is actually missing. Empty string if all met.

Respond with ONLY a valid JSON object:
{{"score": <number>, "passed": <true ONLY if score >= 70 AND all requirements met — if any requirement missing, passed MUST be false and score ≤ 65>, "feedback": "<personalized feedback>", "suggestions": "<only what is actually missing or empty string>"}}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Python tutor who grades code accurately. You apply general programming semantics: e.g. if a task asks to 'print the variables', you check that the code actually uses those variable names in the print (e.g. {name}) — not hardcoded literal values. You are friendly and specific. You only mark requirements missing when they are actually missing. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,  # Slightly higher for more natural, varied feedback while staying accurate
        )
        raw = (resp.choices[0].message.content or "").strip()
        # Extract JSON from response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(raw[start:end])
        else:
            result = {"score": 0, "passed": False, "feedback": raw or "No feedback.", "suggestions": ""}

        score = result.get("score", 0)
        passed = result.get("passed", score >= 70)
        # Enforce: score < 70 is always a fail, no matter what the AI returned
        if score < 70:
            passed = False
        return jsonify({
            "success": True,
            "score": score,
            "passed": passed,
            "feedback": result.get("feedback", ""),
            "suggestions": result.get("suggestions", ""),
        })
    except json.JSONDecodeError as e:
        return jsonify({"success": False, "error": f"Invalid AI response: {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/execute', methods=['POST'])
def execute_code():
    """Run Python code in a subprocess and return stdout, stderr, and exit code."""
    data = request.get_json() or {}
    code = (data.get('code') or '').strip()
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    timeout_seconds = 10
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            path = f.name
        try:
            result = subprocess.run(
                [os.path.abspath(sys.executable), path],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=os.path.dirname(path),
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
            )
            return jsonify({
                'success': result.returncode == 0,
                'stdout': result.stdout or '',
                'stderr': result.stderr or '',
                'exit_code': result.returncode,
            })
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'stdout': '',
            'stderr': f'Execution timed out after {timeout_seconds} seconds.',
            'exit_code': -1,
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'exit_code': -1,
        }), 500


@app.route('/api/exercises/import', methods=['POST'])
def import_exercise():
    """Import an exercise from JSON data"""
    try:
        data = request.get_json()
        exercise_id = data.get('id')
        
        if not exercise_id:
            return jsonify({'error': 'Exercise ID is required'}), 400
        
        exercises[exercise_id] = data
        return jsonify({'success': True, 'exercise_id': exercise_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load exercises on startup
    load_exercises_from_directory()
    print(f"Loaded {len(exercises)} exercise(s)")
    app.run(debug=True, port=5000)
