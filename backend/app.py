from flask import Flask, request, send_from_directory
from dotenv import load_dotenv
import os
import whisper
import threading
from ollama import chat
from flask_cors import CORS

print("Whisper imported successfully")

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_FOLDER = os.path.join(BASE_DIR, "..", "frontend")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")

app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


whisper_lock = threading.Lock()
qwen_lock = threading.Lock()

print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully")

@app.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)

def translate_text(text):

    try:

        response = chat(
            model="qwen3:8b",
            messages=[
                {
                    "role": "system",
                    "content": """
/no_think

You are a professional translation engine.

STRICT RULES:

- Translate English ONLY into Korean.
- Use ONLY modern Korean Hangul characters.
- NEVER use Chinese characters.
- NEVER mix Korean with any other language.
- NEVER explain your answer.
- NEVER add notes, comments, or examples.
- NEVER think aloud.
- Pronunciation must use only English letters.
- Follow the required format exactly.

Required Output Format:

Translation:

Pronunciation:
"""
                },
                {
                    "role": "user",
                    "content": f"""
Translate the following English text into natural Korean.

Requirements:

1. Translation must contain ONLY Korean Hangul.
2. Do NOT use Chinese characters.
3. Do NOT use English words inside the translation.
4. Pronunciation must be written using English letters only.
5. Return EXACTLY in the format below.

Format:

Translation:

Pronunciation:

English Text:
{text}
"""
                }
            ]
        )

        print("RAW RESPONSE:")
        print(response)

        return response["message"]["content"]

    except Exception as e:

        print("QWEN ERROR:")
        print(repr(e))

        raise

@app.route("/uploads", methods=["POST"])
def upload_file():

    if "audio" not in request.files:
        return {"message": "No file uploaded"}, 400

    file = request.files["audio"]

    if file.filename == "":
        return {"message": "Empty filename"}, 400

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename
    }

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():

    if "audio" not in request.files:
        return {"message": "No file uploaded"}, 400

    file = request.files["audio"]

    if file.filename == "":
        return {"message": "Empty filename"}, 400

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    print("File saved:", filepath)
    try:

        with whisper_lock:
            result = model.transcribe(filepath)

    except Exception as e:

        print("WHISPER ERROR:")
        print(repr(e))

        return {
            "message": "Transcription failed",
            "error": str(e)
        }, 500

    print("Transcript:")
    print(result["text"])

    transcript = result["text"]

    if not transcript.strip():

        return {
            "transcript": "",
            "translation": "",
            "pronunciation": "",
            "message": "No speech detected in audio"
        }, 200
    print("Sending to Qwen...")
    try:

        with qwen_lock:
            translation_raw = translate_text(transcript)
    except Exception as e:

        return {
            "transcript": transcript,
            "translation": "",
            "pronunciation": "",
            "message": "Translation failed",
            "error": str(e)
        }, 500

    print("Translation received:")
    print(translation_raw)
    parts = translation_raw.split("Pronunciation:")

    if len(parts) == 2:

        translation = (
            parts[0]
            .replace("Translation:", "")
            .strip()
        )
        pronunciation = parts[1].strip()
    else:

        translation = (
            translation_raw
            .replace("Translation:", "")
            .strip()
        )
        pronunciation = "Not available"

    return {
        "transcript": transcript,
        "translation": translation,
        "pronunciation": pronunciation
    }
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )