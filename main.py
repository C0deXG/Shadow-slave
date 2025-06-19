from flask import Flask, render_template_string, request, make_response
from markupsafe import escape
import os
from docx import Document

app = Flask(__name__)

STORY_FOLDER = "downloaded_docs"
chapters = sorted(f for f in os.listdir(STORY_FOLDER) if f.endswith(".docx"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Shadow Slave Reader</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body    { font-family: sans-serif; padding: 1rem; max-width: 800px; margin: auto; }
    header  { margin-bottom: 1.5rem; }
    select, button { margin: 0.5rem 0; font-size: 1rem; }
    h1      { font-size: 1.5rem; margin-bottom: 1rem; }
    h2      { font-size: 1.25rem; margin-top: 2rem; }
    p       { margin: 0.5rem 0; line-height: 1.5; }
  </style>
</head>
<body>

  <header>
    <h1>Shadow Slave Reader</h1>
  </header>

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
    <!-- ONLY readable content inside article -->
    <article id="chapter-content">
      {{ content|safe }}
    </article>
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

    # Force Edge to fetch fresh version every time
    resp = make_response(rendered)
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"]        = "no-cache"
    resp.headers["Expires"]       = "0"
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
