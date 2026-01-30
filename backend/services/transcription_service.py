import whisper
import os
import json
import time

# Lazy loading model
_model = None

def get_model():
    global _model
    if _model is None:
        print("Whisper modeli yuklanmoqda...")
        _model = whisper.load_model("base")
        print("Whisper tayyor!")
    return _model

def transcribe_video(video_path: str):
    """
    Transcribes a video file using OpenAI Whisper.
    Returns a list of segments with start, end, and text.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        model = get_model()
        result = model.transcribe(video_path)
        
        # We can also save it if needed, but for now just return
        # keys: text, segments, language
        return result["segments"]
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise e
