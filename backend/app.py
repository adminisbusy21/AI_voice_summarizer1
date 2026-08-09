from flask import Flask, request
from dotenv import load_dotenv
import os
import whisper
import threading
from ollama import chat
from flask_cors import CORS
print("Whisper imported Successfully")
load_dotenv()
app = Flask(__name__)
CORS(app)
whisper_lock = threading.Lock()
qwen_lock = threading.Lock()
model = whisper.load_model("base")
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
def translate_text(text):
    try:
        response = chat(
            model="qwen3:8b",
            messages=[
                {
                    "role": "system",
                    "content": f"""
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
<Korean Hangul only>

Pronunciation:
<Romanized Korean only>
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
<Korean translation>

Pronunciation:
<Romanized Korean pronunciation>

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
@app.route("/")
def home():
    return "Backend Working Properly"
@app.route("/uploads", methods=["POST"])
def upload_file():
    if "audio" not in request.files:
        return {"message": "No file uploaded"}, 400
    file = request.files["audio"]
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
        return {"message": "Transcription failed", "error": str(e)}, 500
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
        translation = translation_raw.replace("Translation:", "").strip()
        pronunciation = "Not available"
    return {
        "transcript": transcript,
        "translation": translation,
        "pronunciation": pronunciation
    }
if __name__ == "__main__":
    app.run(debug=True)