from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder="docs", template_folder="docs")


@app.route("/")
def index():
    """Serve the main HTML page (from docs/index.html)."""
    return send_from_directory(app.template_folder, "index.html")


@app.route("/exercises/<path:filename>")
def exercises_static(filename: str):
    """
    Serve exercise JSON files from docs/exercises/.

    The frontend loads exercises via relative paths (e.g. /exercises/manifest.json),
    so this keeps the same layout when running locally with Flask.
    """
    exercises_dir = os.path.join(app.static_folder, "exercises")
    return send_from_directory(exercises_dir, filename)


if __name__ == "__main__":
    # Simple local dev server: visit http://localhost:5000 in your browser.
    app.run(debug=True, port=5000)
