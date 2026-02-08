# Python Tutor - Exercise Platform

A simple web-based platform for teaching Python programming. Students can complete exercises and receive AI-powered feedback on their answers.

## Features

- 📝 Simple HTML interface that students can open in any browser
- 🤖 **AI grading** via a real API: **Groq free tier** (recommended) or optional OpenAI
- 📚 Support for learning materials (links and text)
- 📦 Import exercises from JSON files
- 🎯 Automatic pass/fail determination (70+ score = pass)

## Quick Start — Everything from this GitHub repo

Both the **website** and the **backend** live in this repo. Deploy the backend from GitHub (e.g. Render), host the site on GitHub Pages, then set the backend URL once in the code. **Users either** enter their own Groq API key **or** log in with a username/password you created. **All logged-in users use your API key** (one key on the server); you can add as many students as you want by hashing their credentials and adding them to `ALLOWED_USERS`.

### 1. Deploy the backend from this repo (e.g. Render)

1. Push this repo to GitHub.
2. Go to [Render](https://render.com) → **New** → **Web Service** → connect your GitHub repo.
3. Render can use the **`render.yaml`** in this repo, or set manually: **Build**: `pip install -r requirements.txt`, **Start**: `gunicorn app:app`.
4. In Render **Environment**: add **`GROQ_API_KEY`** (your key from [console.groq.com](https://console.groq.com)). Never commit the key.
5. Optional — let students use your key by logging in: add **`ALLOWED_USERS`** (JSON array of hashed users). Generate one with:
   ```bash
   python hash_password.py myuser mypassword
   ```
   Copy the output into `ALLOWED_USERS` (e.g. `[{"username_hash":"...","password_hash":"..."}]`). Only hashes are stored.
6. Note your backend URL (e.g. `https://python-tutor-xxx.onrender.com`).

### 2. Host the site (GitHub Pages)

1. In the repo: **Settings** → **Pages** → **Source**: Deploy from branch → **Branch**: main → **Folder**: /docs → Save.
2. Site URL: `https://<username>.github.io/<repo-name>/`

### 3. Set the backend URL once in the repo

In **`docs/index.html`**, near the top of the `<script>` block, set:

```javascript
const BACKEND_URL = 'https://your-backend.onrender.com';  // your real backend URL
```

Commit and push. After that, **users never see or enter the backend URL**. They only:

- **Use their own key**: Paste a Groq API key (link to get one is on the site), or  
- **Log in**: Enter a username/password **you** created for them → they use **your** Groq API key (no key needed on their side).

---

### Adding more students (future-proof)

Only **one** API key lives on the server: **yours** (`GROQ_API_KEY`). Every user you add to `ALLOWED_USERS` and who logs in with that username/password will use that same key.

To add a new student:

1. On your machine, run:
   ```bash
   python hash_password.py NewStudentName theirpassword
   ```
2. Copy the printed JSON object (e.g. `{"username_hash":"...","password_hash":"..."}`).
3. In Render → your Web Service → **Environment** → edit **`ALLOWED_USERS`**.
4. It should be a JSON **array**. Add the new object to the array (comma between entries). Example with two students:
   ```json
   [
     {"username_hash":"91a03364125862e76532c559c8cf191c328ea06fd098ecc3d2aa35adc7941148","password_hash":"$2b$12$U8fja8cmE..."},
     {"username_hash":"a1b2c3...","password_hash":"$2b$12$..."}
   ]
   ```
5. Save. Render will redeploy; the new student can log in with the username/password you used in step 1.

You never store plain passwords; only hashed username + password. Each new student = one more object in `ALLOWED_USERS`.

### Adding exercises

- Add a JSON file in **`docs/exercises/`** (e.g. `exercise_3.json`) with the same structure as `exercise_1.json`.
- Add an entry to **`docs/exercises/manifest.json`**:
  ```json
  {"id": "exercise_3", "title": "Your Title", "description": "Short description"}
  ```
- Commit and push; the new exercise appears after the next deploy.

---

## Optional: Run backend locally

To test the backend on your machine:

1. **Install:** `pip install -r requirements.txt`
2. **Env:** Copy `.env.example` to `.env` and set `GROQ_API_KEY` (and optionally `ALLOWED_USERS`).
3. **Run:** `python app.py` → backend at `http://localhost:5000`
4. On the GitHub Pages site, set **Backend URL** to `http://localhost:5000` (or use a tunnel like ngrok for HTTPS).

## Exercise JSON Format

Create exercise files in the **`docs/exercises/`** directory (used by both the local app and GitHub Pages). Each exercise should be a JSON file with the following structure:

```json
{
  "id": "unique_exercise_id",
  "title": "Exercise Title",
  "description": "Brief description",
  "question": "The exercise question or prompt",
  "materials": [
    {
      "type": "link",
      "title": "Link Title",
      "content": "https://example.com"
    },
    {
      "type": "text",
      "content": "Helpful text material"
    }
  ],
  "grading_instructions": "Detailed instructions for the AI on how to grade this exercise. Include what to check for, point allocation, and grading criteria."
}
```

### Example Exercise

See `docs/exercises/exercise_1.json` for a complete example.

## API Endpoints

### GET `/api/exercises`
Returns a list of all available exercises.

### GET `/api/exercises/<exercise_id>`
Returns a specific exercise (no grading instructions).

### POST `/api/exercises/<exercise_id>/grade`
Grades a student answer. Body: `{"answer": "..."}`. Uses Groq or OpenAI from server.

### POST `/api/exercises/import`
Import an exercise programmatically.

**Request Body:** Complete exercise JSON object.

## Usage

1. **For Teachers:**
   - Create exercise JSON files in the `docs/exercises/` directory
   - Start the server with `python app.py`
   - Share the URL (`http://localhost:5000`) with students

2. **For Students:**
   - Open the URL in a web browser
   - Select an exercise from the dropdown
   - Read the question and materials
   - Write your answer in the text area
   - Click "Submit Answer" to get AI feedback

## Customization

- Modify `templates/index.html` to change the UI appearance
- In `app.py`: change `GROQ_MODEL` (e.g. `llama-3.3-70b-versatile`) or `OPENAI_MODEL` for grading
- Change the pass threshold (70) in the grading prompt in `app.py`
- Add more exercise types by creating new JSON files in `docs/exercises/`

## Free API limits (summary)

| Provider | Free tier | Get key |
|----------|-----------|--------|
| **Groq** (default) | ~14,400 requests/day (llama-3.1-8b-instant) | [console.groq.com](https://console.groq.com) |
| **OpenAI** | Varies by account | [platform.openai.com](https://platform.openai.com/api-keys) |

## Notes

- The app loads all exercise `.json` files from `docs/exercises/` on startup (manifest.json is skipped); restart the server to reload
- Grading runs on the server; set either `GROQ_API_KEY` or `OPENAI_API_KEY` in `.env` (Groq is used first if both are set)
