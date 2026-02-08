# Python Tutor - Exercise Platform

A simple web-based platform for teaching Python programming. Students can complete exercises and receive AI-powered feedback on their answers.

## Features

- 📝 Simple HTML interface that students can open in any browser
- 🤖 **AI grading** via a real API: **Groq free tier** (recommended) or optional OpenAI
- 📚 Support for learning materials (links and text)
- 📦 Import exercises from JSON files
- 🎯 Automatic pass/fail determination (70+ score = pass)

## Quick Start — GitHub Pages + Backend (Groq)

The **website** is the static site in **`docs/`** (hosted on GitHub Pages). **Grading** uses **Groq** and requires a small **backend** (this Flask app) deployed somewhere. Students either enter your **Groq API key** on the site or **log in** with a username/password you define (then the server uses your key).

### 1. Deploy the backend (Flask)

Deploy this repo’s Flask app to a host that supports Python (e.g. [Render](https://render.com), Railway, Fly.io):

- Set **one** env var: **`GROQ_API_KEY`** = your Groq API key (get one at [console.groq.com](https://console.groq.com)). **Never commit this key**; set it only in the host’s environment.
- Optional — allow students to use your key by logging in: set **`ALLOWED_USERS`** to a JSON array of `{"username":"...", "password_hash":"..."}`. Generate hashes with:
  ```bash
  python hash_password.py student1 theirpassword
  ```
  Then add that object to `ALLOWED_USERS` (e.g. one object per student). Passwords are stored as bcrypt hashes only.

Note your backend URL (e.g. `https://python-tutor-xxx.onrender.com`).

### 2. Deploy the site (GitHub Pages)

1. Push the repo to GitHub.
2. **Settings** → **Pages** → **Source**: Deploy from branch → **Branch**: main → **Folder**: /docs → Save.
3. Site URL: `https://<username>.github.io/<repo-name>/`

### 3. On the website

- **Backend URL**: Enter the URL of your deployed backend (e.g. `https://python-tutor-xxx.onrender.com`).
- **API key**: Optional. If you enter your Groq API key here, grading uses it (saved in the browser only).
- **Or login**: Enter a username/password you added to `ALLOWED_USERS`; grading then uses the server’s `GROQ_API_KEY`.

Code runs in the browser (Pyodide). Grading runs on your backend with Groq.

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
