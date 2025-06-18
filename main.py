from flask import Flask, render_template_string, request, make_response
import os
from docx import Document

app = Flask(__name__)

# Folder containing .docx chapters
STORY_FOLDER = "downloaded_docs"

# Get all chapter filenames
chapters = sorted(f for f in os.listdir(STORY_FOLDER) if f.endswith(".docx"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Shadow Slave Reader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: sans-serif;
            padding: 1rem;
            max-width: 900px;
            margin: auto;
        }
        select, button {
            margin-bottom: 1rem;
        }
        #reader {
            white-space: pre-wrap;
            margin-top: 2rem;
        }
    </style>
</head>
<body>
    <h2>Shadow Slave Chapter Reader</h2>
    <form method="get">
        <label for="start">From:</label>
        <select name="start" id="start">
            {% for file in chapters %}
                <option value="{{ file }}" {% if file == start %}selected{% endif %}>{{ file.replace('.docx', '') }}</option>
            {% endfor %}
        </select>

        <label for="end">To:</label>
        <select name="end" id="end">
            {% for file in chapters %}
                <option value="{{ file }}" {% if file == end %}selected{% endif %}>{{ file.replace('.docx', '') }}</option>
            {% endfor %}
        </select>

        <button type="submit">Read</button>
    </form>

    {% if content %}
        <div id="reader">{{ content }}</div>
        <button onclick="speakText()">🔊 Read Aloud</button>
        <button onclick="stopSpeaking()">🛑 Stop</button>
    {% endif %}

    <script>
        function speakText() {
            try {
                const text = document.getElementById('reader').innerText;
                if (!text) throw new Error("No text to read");
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.onerror = (e) => {
                    alert("Speech failed: " + e.error);
                };
                window.speechSynthesis.speak(utterance);
            } catch (err) {
                alert("Text-to-speech not supported or failed.");
            }
        }

        function stopSpeaking() {
            try {
                window.speechSynthesis.cancel();
            } catch (err) {
                console.error("Stop speaking failed:", err);
            }
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
                content += f"\n\n\n----- {chapter.replace('.docx', '')} -----\n\n"
                content += "\n".join(p.text for p in doc.paragraphs)
        else:
            content = "⚠️ Invalid range: 'From' must come before 'To'."

    rendered = render_template_string(
        HTML_TEMPLATE,
        chapters=chapters,
        content=content,
        start=start,
        end=end
    )

    # Prevent caching issues in Edge
    response = make_response(rendered)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
