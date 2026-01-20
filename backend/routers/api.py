from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse
import os
import shutil
from backend.services import video_service, transcription_service, translation_service
from backend.models.schemas import TranslationRequest

router = APIRouter(prefix="/api")
UPLOAD_DIR = "uploads"

@router.get("/health")
async def health_check():
    return {"status": "ok"}

# --- 1. Analyze ---
@router.post("/analyze-url")
async def analyze_url(url: str = Form(...)):
    try:
        data = video_service.analyze_youtube_url(url)
        return JSONResponse(content={"status": "success", "data": data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=400)

# --- 2. Process (Download + Transcribe) ---
@router.post("/process-video")
async def process_video(url: str = Form(...), original_title: str = Form(...)):
    try:
        clean_title = "".join([c for c in original_title if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{clean_title}.mp4"
        
        # Download
        video_path = video_service.download_video(url, UPLOAD_DIR, filename)
        
        # Transcribe
        json_filename = f"{clean_title}.json"
        json_path = os.path.join(UPLOAD_DIR, json_filename)
        segments = transcription_service.transcribe_file(video_path, json_path)
        
        formatted_segments = [{"start": s['start'], "end": s['end'], "text": s['text']} for s in segments]

        return JSONResponse(content={
            "status": "success",
            "message": "Video yuklandi!",
            "data": {
                "audio_path": video_path, # keep key for compatibility
                "segments": formatted_segments
            }
        })
    except Exception as e:
        print(e)
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# --- 3. Upload ---
@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Transcribe directly
        clean_title = os.path.splitext(file.filename)[0]
        json_path = os.path.join(UPLOAD_DIR, f"{clean_title}.json")
        segments = transcription_service.transcribe_file(file_path, json_path)
        
        formatted_segments = [{"start": s['start'], "end": s['end'], "text": s['text']} for s in segments]
        
        return JSONResponse(content={
            "status": "success",
            "message": "Yuklandi!",
            "data": {"segments": formatted_segments}
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# --- 4. Translate ---
@router.post("/translate")
async def translate_text(request: TranslationRequest):
    try:
        translated = translation_service.translate_segments(request.segments, request.target_lang)
        return JSONResponse(content={
            "status": "success", 
            "data": {"segments": translated}
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# --- 5. Get Project ---
@router.get("/project/{project_id}")
async def get_project(project_id: str):
    # Search for video
    video_filename = None
    for ext in ['.mp4', '.mov', '.avi', '.webm']:
        if os.path.exists(os.path.join(UPLOAD_DIR, project_id + ext)):
            video_filename = project_id + ext
            break
            
    if not video_filename:
        return JSONResponse(content={"status": "error", "message": "Video not found"}, status_code=404)
        
    # Load transcript
    transcript_path = os.path.join(UPLOAD_DIR, project_id + ".json")
    segments = []
    if os.path.exists(transcript_path):
        import json
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both raw whisper format and our cleaned format
            raw = data.get('segments', []) if isinstance(data, dict) else data
            for s in raw:
                segments.append({
                    "start": s['start'],
                    "end": s['end'],
                    "text": s['text'],
                    "translated": s.get('translated')
                })

    return JSONResponse(content={
        "status": "success",
        "data": {
            "project_id": project_id,
            "video_url": f"/uploads/{video_filename}",
            "segments": segments
        }
    })
