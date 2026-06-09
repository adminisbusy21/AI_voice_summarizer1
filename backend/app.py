from flask import Flask, request
from dotenv import load_dotenv
import os
import whisper
print("Whsiper imported Successfully")
from flask_cors import CORS
load_dotenv()
app = Flask(__name__)
CORS(app)
model = whisper.load_model("base")
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
@app.route("/")
def home():
    return " Backend Working Properly"
@app.route("/uploads", methods=["POST"])
def upload_file():
    if "audio" not in request.files:
        return{"message": "No file uploaded"}, 400
    file = request.files["audio"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
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
    filepath = os.path.join(app.config["UPLOAD_FOLDER"],file.filename)
    file.save(filepath)
    print("File saved:", filepath)
    result = model.transcribe(filepath)
    print("Transcript:")
    print(result["text"])
    return {
        "transcript": result["text"]
    }
if __name__ == "__main__": 
    app.run(debug=True)