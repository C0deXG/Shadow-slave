from flask import Flask, render_template_string, request
import os
from docx import Document

app = Flask(__name__)

# Folder where the .docx stories are stored
STORY_FOLDER = "downloaded_docs"

# Read available chapters
chapters = sorted(f for f in os.listdir(STORY_FOLDER) if f.endswith(".docx"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Shadow Slave Reader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; padding: 2rem; max-width: 1000px; margin: auto; line-height: 1.6; }
        select, button { padding: 0.5rem; font-size: 1rem; margin-right: 1rem; }
        #reader { margin-top: 2rem; white-space: pre-wrap; border: 1px solid #ccc; padding: 1rem; background: #f9f9f9; }
        #controls { margin-top: 1rem; }
    </style>
</head>
<body>
    <h1>📖 Shadow Slave Chapter Reader</h1>
    <form method="get">
        <label>From:</label>
        <select name="start">
            {% for file in chapters %}
                <option value="{{ file }}" {% if file == start %}selected{% endif %}>{{ file.replace('.docx', '') }}</option>
            {% endfor %}
        </select>

        <label>To:</label>
        <select name="end">
            {% for file in chapters %}
                <option value="{{ file }}" {% if file == end %}selected{% endif %}>{{ file.replace('.docx', '') }}</option>
            {% endfor %}
        </select>

        <button type="submit">Read</button>
    </form>

    {% if content %}
        <h3>📚 Reading: {{ start.replace('.docx', '') }} to {{ end.replace('.docx', '') }}</h3>
        <div id="reader">{{ content }}</div>
        <div id="controls">
            <button onclick="speakText()">🔊 Read Aloud</button>
            <button onclick="stopSpeaking()">🛑 Stop</button>
        </div>
    {% endif %}

    <script>
        function speakText() {
            const text = document.getElementById('reader').innerText;
            const utterance = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.speak(utterance);
        }

        function stopSpeaking() {
            window.speechSynthesis.cancel();
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    start = request.args.get("start")
    end = request.args.get("end")
    content = ""

    if start and end and start in chapters and end in chapters:
        start_index = chapters.index(start)
        end_index = chapters.index(end)

        if start_index <= end_index:
            selected = chapters[start_index:end_index + 1]
            for chapter in selected:
                doc = Document(os.path.join(STORY_FOLDER, chapter))
                content += f"\n\n----- {chapter.replace('.docx', '')} -----\n\n"
                content += "\n".join(p.text for p in doc.paragraphs)
        else:
            content = "⚠️ Invalid range: 'From' must come before 'To'."

    return render_template_string(HTML_TEMPLATE, chapters=chapters, content=content, start=start, end=end)

if __name__ == "__main__":
    app.run(debug=True)