from flask import Flask, render_template_string, request, make_response
from markupsafe import escape
import os
from docx import Document

app = Flask(__name__)

# Directory containing your .docx chapter files
STORY_FOLDER = "downloaded_docs"

# List all .docx files in ascending order
chapters = sorted(f for f in os.listdir(STORY_FOLDER) if f.endswith(".docx"))

# The HTML template: semantic <article>, <h2> and <p>
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Shadow Slave Reader</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: sans-serif; padding: 1rem; max-width: 800px; margin: auto; }
    select, button { margin: .5rem 0; }
    article { margin-top: 2rem; }
    h2      { margin: 1.5rem 0 .5rem; font-size: 1.25rem; }
    p       { margin: .5rem 0; line-height: 1.4; }
  </style>
</head>
<body>
  <h1>Shadow Slave Reader</h1>
  <form method="get">
    <label for="start">From:</label>
    <select name="start" id="start">
      {% for file in chapters %}
        <option value="{{ file }}" {% if file==start %}selected{% endif %}>
          {{ file.replace('.docx','') }}
        </option>
      {% endfor %}
    </select>

    <label for="end">To:</label>
    <select name="end" id="end">
      {% for file in chapters %}
        <option value="{{ file }}" {% if file==end %}selected{% endif %}>
          {{ file.replace('.docx','') }}
        </option>
      {% endfor %}
    </select>

    <button type="submit">Read</button>
  </form>

  {% if content %}
    <article id="chapter-content">
      {{ content|safe }}
    </article>
    <button onclick="window.speechSynthesis.speak(new SpeechSynthesisUtterance(document.getElementById('chapter-content').innerText));">
      🔊 Read Aloud
    </button>
    <button onclick="window.speechSynthesis.cancel();">
      🛑 Stop
    </button>
  {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    start = request.args.get("start")
    end   = request.args.get("end")
    content = ""

    if start in chapters and end in chapters:
        si, ei = chapters.index(start), chapters.index(end)
        if si <= ei:
            for fname in chapters[si:ei+1]:
                # Use filename without .docx as the heading text
                title = os.path.splitext(fname)[0]
                content += f"<h2>{escape(title)}</h2>\n"
                doc = Document(os.path.join(STORY_FOLDER, fname))
                for p in doc.paragraphs:
                    txt = p.text.strip()
                    if txt:
                        content += f"<p>{escape(txt)}</p>\n"
        else:
            content = "<p>⚠️ Invalid range: 'From' must come before 'To'.</p>"

    rendered = render_template_string(
        HTML_TEMPLATE,
        chapters=chapters,
        content=content,
        start=start,
        end=end
    )

    # Prevent caching so Edge always loads the newest content
    resp = make_response(rendered)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"]        = "no-cache"
    resp.headers["Expires"]       = "0"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
