# Python Tutor - Exercise Platform

A simple web-based platform for teaching Python programming. Students can complete exercises and receive AI-powered feedback on their answers.

## Features

- 📝 Simple HTML interface that students can open in any browser
- 🤖 **AI grading** via a real API: **Groq free tier** (recommended) or optional OpenAI
- 📚 Support for learning materials (links and text)
- 📦 Import exercises from JSON files
- 🎯 Automatic pass/fail determination (70+ score = pass)

## Quick Start — Host on GitHub Pages

The app is meant to be used as a **static site on GitHub Pages**. No server or API keys required; students open the URL and get code execution (Pyodide) and AI grading (Puter) in the browser.

### Deploy steps

1. **Push the repo to GitHub** (create a repo and push this project).

2. **Turn on GitHub Pages**  
   - Repo → **Settings** → **Pages**  
   - **Source**: Deploy from a branch  
   - **Branch**: main (or master)  
   - **Folder**: /docs  
   - Save  

3. **Use the site**  
   - URL: `https://<your-username>.github.io/<repo-name>/`  
   - Example: `https://jane.github.io/Python-Tutor/`

### How it works

- **`docs/`** is the static site: **Run code** with [Pyodide](https://pyodide.org/) (Python in the browser), **AI grading** with [Puter AI](https://docs.puter.com/AI/chat/) (no API key; Puter’s user-pays model when students submit).
- Exercises live in **`docs/exercises/`** (manifest + JSON files).

### Adding exercises

- Add a JSON file in **`docs/exercises/`** (e.g. `exercise_3.json`) with the same structure as `exercise_1.json`.
- Add an entry to **`docs/exercises/manifest.json`**:
  ```json
  {"id": "exercise_3", "title": "Your Title", "description": "Short description"}
  ```
- Commit and push; the new exercise appears after the next deploy.

---

## Optional: Run locally (Flask + Groq/OpenAI)

If you want to run the app locally with server-side grading (Groq or OpenAI API):

1. **Install:** `pip install -r requirements.txt`
2. **API key:** Create a `.env` file with `GROQ_API_KEY=...` (from [console.groq.com](https://console.groq.com)) or `OPENAI_API_KEY=...`
3. **Run:** `python app.py` → open `http://localhost:5000`

Exercises are still loaded from **`docs/exercises/`** (same as GitHub Pages).

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
