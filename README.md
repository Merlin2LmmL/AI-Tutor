# Python Tutor - Exercise Platform

A simple web-based platform for teaching Python programming. Students can complete exercises and receive AI-powered feedback on their answers.

## Features

- Simple HTML interface that students can open in any browser
- **AI grading** via the **Groq HTTP API** (called directly from the browser)
- Support for learning materials (links and text)
- Import exercises from JSON files
- Automatic pass/fail determination (70+ score = pass)

## Live site

The production site is hosted on GitHub Pages here:

- https://merlin2lmml.github.io/AI-Tutor/

## Architecture

This project is **fully frontend-driven**:

- All grading calls go **directly from the browser to Groq’s API**.
- The Python `app.py` file is only used as a **simple local static server** to host the `docs/` folder at `http://localhost:5000` while you develop.
- There is **no separate backend deployment** and **no server-side AI logic**.

Every user:

- Brings their own **Groq API key**.
- Has their key stored **only in their browser** (session storage).
- Talks directly from their browser to Groq; no shared server key and no login system.

## Running locally (recommended workflow)

Use this when you want to test the tutor on `http://localhost:5000` using your own Groq key.

1. **Create and activate a virtual environment**

   From the project root:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # On Windows:
   # .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Run the local static server**

   ```bash
   python app.py
   ```

   This starts a simple Flask server at `http://localhost:5000` and serves everything in the `docs/` folder (including the exercises JSON).

4. **Open the tutor in your browser**

   Go to:

   - `http://localhost:5000`

   Then:

   - Paste your **Groq API key** in the field at the top.
   - Select an exercise, write your solution, click **Submit Answer**.
   - The browser calls `https://api.groq.com/openai/v1/chat/completions` directly using your key.

---

### Students & access

There is no server-side user management in this version.

- Anyone who can open the page can paste a Groq key and start using the tutor.
- You never store any passwords or accounts; only the user’s API key lives in their browser session.

### Adding exercises

- Add a JSON file in **`docs/exercises/`** (e.g. `exercise_3.json`) with the same structure as `exercise_1.json`.
- Add an entry to **`docs/exercises/manifest.json`**:
  ```json
  {"id": "exercise_3", "title": "Your Title", "description": "Short description"}
  ```
- Commit and push; the new exercise appears after the next deploy.

---

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

## API (Groq, client-side)

The browser calls Groq directly using the user’s key:

- Endpoint: `https://api.groq.com/openai/v1/chat/completions`
- Default model: `qwen-3-32b` (32B, balanced default)
- Other options in the dropdown:
  - `llama-3.1-8b-instant` (8B, fast & cheap)
  - `llama-3.3-70b-versatile` (70B, higher quality)
  - `openai/gpt-oss-20b` (20B)
  - `openai/gpt-oss-120b` (120B, strongest reasoning)
- Auth header: `Authorization: Bearer gsk_...`
- Body: OpenAI-style `messages` array with a grading prompt (see `docs/index.html`).

## Usage

1. **For Teachers / Maintainers:**
   - Create exercise JSON files in the `docs/exercises/` directory.
   - Run `python app.py` for local testing, or push to GitHub to update `https://merlin2lmml.github.io/AI-Tutor/`.

2. **For Students:**
   - Open the live site or `http://localhost:5000` in a browser.
   - Paste a Groq API key.
   - Select an exercise, write your answer, and click **Submit Answer** to get AI feedback.

## Customization

- Modify `docs/index.html` to change the UI appearance or grading prompt text.
- Add more exercise types by creating new JSON files in `docs/exercises/`.

## Notes

- Exercises are simple JSON files in `docs/exercises/` (see `exercise_1.json` for a full example).
- Grading runs entirely in the browser and talks directly to Groq using the per-user API key.
