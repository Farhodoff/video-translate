from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os
import time

app = FastAPI()

# Mount static files (css, js, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="templates")

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def read_root(request: Request):
    """Render the main page."""
    return templates.TemplateResponse("index.html", {"request": request})

import yt_dlp

# ... (existing imports)

@app.post("/api/analyze-url")
async def analyze_url(url: str = Form(...)):
    """
    Analyze a video via URL using yt-dlp to get real metadata.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # We just want metadata for now
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_title = info.get('title', 'Noma\'lum')
            duration_seconds = info.get('duration', 0)
            duration_formatted = time.strftime('%H:%M:%S', time.gmtime(duration_seconds))
            thumbnail = info.get('thumbnail', '')
            
        return JSONResponse(content={
            "status": "success",
            "message": "Video muvaffaqiyatli tahlil qilindi!",
            "data": {
                "video_title": video_title,
                "duration": duration_formatted,
                "thumbnail": thumbnail,
                "original_url": url,
                "dubbing_status": "Ready to Download"
            }
        })
        
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"Videoni tahlil qilishda xatolik: {str(e)}"
        }, status_code=400)

import os
import shutil
from pydub import AudioSegment

# ... imports

import whisper
import json

# Global model loading (lazy loading recommended for startup speed, but for demo we load here or inside function)
# Loading 'base' model which is a good balance of speed/accuracy for CPU.
print("Whisper modeli yuklanmoqda... (Biroz vaqt olishi mumkin)")
model = whisper.load_model("base")
print("Whisper modeli tayyor!")

@app.post("/api/process-video")
async def process_video(url: str = Form(...), original_title: str = Form(...)):
    """
    Step 2 & 3: Download Audio & Transcribe (Local Whisper)
    """
    try:
        clean_title = "".join([c for c in original_title if c.isalnum() or c in (' ', '-', '_')]).strip()
        audio_filename = f"{clean_title}.mp3"
        audio_path = os.path.join(UPLOAD_DIR, audio_filename)
        
        # 1. Download Audio
        if not os.path.exists(audio_path):
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(UPLOAD_DIR, f"{clean_title}.%(ext)s"),
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        # 2. Transcribe with Whisper (Local)
        # This runs on the server's CPU/GPU
        result = model.transcribe(audio_path)
        
        # Save transcript for debug/future use
        transcript_path = os.path.join(UPLOAD_DIR, f"{clean_title}.json")
        with open(transcript_path, "w", encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        # Prepare simple segments for frontend
        segments = []
        for segment in result['segments']:
            segments.append({
                "start": segment['start'],
                "end": segment['end'],
                "text": segment['text']
            })

        return JSONResponse(content={
            "status": "success",
            "message": "Audio yuklandi va matnga aylantirildi!",
            "data": {
                "audio_path": audio_path,
                "step": 3,
                "segments_count": len(segments),
                "segments": segments, 
                "full_transcript_path": transcript_path,
                "next_action": "Tarjima (O'zbek tiliga)"
            }
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={
            "status": "error",
            "message": f"Transkripsiya jarayonida xatolik: {str(e)}"
        }, status_code=500)

@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """
    Handle video file upload and immediately transcribe it.
    """
    try:
        # 1. Save File
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Transcribe (Directly from video file)
        # Whisper uses ffmpeg internally to extract audio
        print(f"Transcribing uploaded file: {file.filename}")
        result = model.transcribe(file_path)
        
        # 3. Save Transcript
        clean_title = os.path.splitext(file.filename)[0]
        transcript_path = os.path.join(UPLOAD_DIR, f"{clean_title}.json")
        with open(transcript_path, "w", encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        # 4. Prepare Response
        segments = []
        for segment in result['segments']:
            segments.append({
                "start": segment['start'],
                "end": segment['end'],
                "text": segment['text']
            })

        return JSONResponse(content={
            "status": "success",
            "message": f"'{file.filename}' video yuklandi va matnga aylantirildi!",
            "data": {
                "audio_path": file_path,
                "step": 3,
                "segments_count": len(segments),
                "segments": segments,
                "next_action": "Tarjima (O'zbek tiliga)"
            }
        })

    except Exception as e:
        print(f"Upload Error: {e}")
        return JSONResponse(content={
            "status": "error",
            "message": f"Yuklashda yoki tahlilda xatolik: {str(e)}"
        }, status_code=500)

from deep_translator import GoogleTranslator

class TranslationRequest(BaseModel):
    segments: list
    target_lang: str = "uz"

@app.post("/api/translate")
async def translate_text(request: TranslationRequest):
    """
    Step 4: Translate segments to Uzbek.
    """
    try:
        translator = GoogleTranslator(source='auto', target=request.target_lang)
        translated_segments = []
        
        # Translate batch or line by line (deep_translator is synchronous)
        # For better performance we could use batch, but let's keep it simple
        for seg in request.segments:
            translated_text = translator.translate(seg['text'])
            translated_segments.append({
                "start": seg['start'],
                "end": seg['end'],
                "text": translated_text,
                "original": seg['text']
            })
            
        return JSONResponse(content={
            "status": "success",
            "message": "Tarjima yakunlandi!",
            "data": {
                "segments": translated_segments,
                "step": 4,
                "next_action": "Dublyaj (Ovoz yozish)"
            }
        })
        
    except Exception as e:
        print(f"Translation Error: {e}")
        return JSONResponse(content={
            "status": "error",
            "message": f"Tarjimada xatolik: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("Server ishga tushmoqda: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
