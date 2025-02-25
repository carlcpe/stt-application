import os
import whisper
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from moviepy.editor import AudioFileClip

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

model = whisper.load_model("base")  # Load Whisper model

def extract_audio(video_path, audio_path):
    """Extracts audio from video and saves it as a WAV file."""
    audio = AudioFileClip(video_path)
    audio.write_audiofile(audio_path, codec='pcm_s16le')

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)  
    return result['text']

@app.route('/templaces')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(video_path)
    
    audio_path = video_path.rsplit('.', 1)[0] + ".wav"
    extract_audio(video_path, audio_path)
    transcription = transcribe_audio(audio_path)
    
    os.remove(audio_path)  # Clean up audio file
    os.remove(video_path)  # Clean up video file
    
    return jsonify({"transcription": transcription})

if __name__ == '__main__':
    app.run(debug=True)
