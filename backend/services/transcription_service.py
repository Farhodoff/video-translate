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

def transcribe_file(file_path: str, output_path: str):
    model = get_model()
    result = model.transcribe(file_path)
    
    # MOCK RESULT REMOVED
    
    # Save JSON
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    return result['segments']
