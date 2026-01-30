from fastapi import APIRouter, Form, UploadFile, File, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from backend import database
from backend.models import models
from backend.services import auth, video_service
import os
import shutil
import uuid
import shutil
import uuid
import json
import time
import traceback
from backend.services import video_service, transcription_service, translation_service, tts_service, dubbing_service, notes_service
from backend.utils.text_normalizer import normalize_text
from backend.models.schemas import TranslationRequest, ProjectUpdateRequest

router = APIRouter(prefix="/api")
UPLOAD_DIR = "uploads"

router = APIRouter(prefix="/api")
UPLOAD_DIR = "uploads"

def process_project_video(project_id: int, url: str, db: Session):
    try:
        # 1. Fetch project (re-query to ensure session is fresh)
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            return
            
        # 2. Analyze
        info = video_service.analyze_youtube_url(url)
        project.thumbnail = info.get("thumbnail")
        project.title = info.get("video_title") if not project.title else project.title
        db.commit()

        # 3. Download
        filename = f"{project_id}_{int(time.time())}.mp4"
        output_path = video_service.download_video(url, UPLOAD_DIR, filename)

        # 4. Update
        project.video_url = f"/uploads/{os.path.basename(output_path)}"
        project.status = "Ready"
        db.commit()
    except Exception as e:
        print(f"Error processing project {project_id}: {e}")
        project.status = "Error"
        project.error_message =str(e)
        db.commit()

@router.post("/projects")
async def create_project(
    background_tasks: BackgroundTasks,
    youtube_url: str = Form(...),
    title: str = Form(None),
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Create Project in DB
    new_project = models.Project(
        user_id=user.id,
        title=title or "New Project",
        status="Processing",
        video_url=None, # Will be set after download
        thumbnail=None
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Trigger background task
    background_tasks.add_task(process_project_video, new_project.id, youtube_url, db)
    
    return RedirectResponse(url="/dashboard", status_code=303)
@router.websocket("/ws/export/{project_id}")
async def export_websocket(websocket: WebSocket, project_id: str):
    await websocket.accept()
    try:
        # 1. Find Video
        video_filename = None
        for ext in ['.mp4', '.mov', '.avi', '.webm']:
            if os.path.exists(os.path.join(UPLOAD_DIR, project_id + ext)):
                video_filename = project_id + ext
                break

        if not video_filename:
             await websocket.send_json({"status": "error", "message": "Video unavailable"})
             await websocket.close()
             return

        video_path = os.path.join(UPLOAD_DIR, video_filename)

        # 2. Find Transcript
        json_path = os.path.join(UPLOAD_DIR, f"{project_id}.json")
        if not os.path.exists(json_path):
             await websocket.send_json({"status": "error", "message": "Transcript not found"})
             await websocket.close()
             return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            segments = data.get('segments', []) if isinstance(data, dict) else data

        # 3. Callback
        async def send_progress(percent):
            await websocket.send_json({"status": "progress", "percent": percent})

        # 4. Process
        result = await dubbing_service.generate_dubbed_video(
            project_id,
            segments,
            video_path,
            UPLOAD_DIR,
            progress_callback=send_progress
        )

        await websocket.send_json({
            "status": "complete",
            "data": result
        })
        await websocket.close()

    except Exception as e:
        traceback.print_exc()
        await websocket.send_json({"status": "error", "message": str(e)})
        # Check if open before closing
        try:
            await websocket.close()
        except:
            pass

# --- 5. Generate Audio (TTS) ---
@router.post("/generate-audio")
async def generate_audio(
    text: str = Form(...),
    voice: str = Form("uz-UZ-MadinaNeural"),
    rate: str = Form("+0%"),
    pitch: str = Form("+0Hz")
):
    try:
        filename = f"tts_{uuid.uuid4()}.mp3"
        output_path = os.path.join(UPLOAD_DIR, filename)

        # Normalize text for better pronounciation
        normalized_text = normalize_text(text)

        success = await tts_service.generate_speech(normalized_text, output_path, voice, rate, pitch)

        if success:
            return JSONResponse(content={
                "status": "success",
                "audio_url": f"/uploads/{filename}"
            })
        else:
            return JSONResponse(content={"status": "error", "message": "TTS failed"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


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

# --- 5. Get Project (READ) ---
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

# --- 6. Update Project (UPDATE) ---
@router.put("/project/{project_id}")
async def update_project(project_id: str, request: ProjectUpdateRequest):
    try:
        json_path = os.path.join(UPLOAD_DIR, f"{project_id}.json")
        if not os.path.exists(json_path):
             return JSONResponse(content={"status": "error", "message": "Project not found"}, status_code=404)

        # Convert Pydantic models to dict
        new_segments = [s.dict() for s in request.segments]

        # Save to file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"segments": new_segments}, f, ensure_ascii=False, indent=4)

        return JSONResponse(content={"status": "success", "message": "Project updated"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# --- 7. Delete Project (DELETE) ---
@router.delete("/project/{project_id}")
async def delete_project(project_id: str):
    try:
        # 1. Delete JSON
        json_path = os.path.join(UPLOAD_DIR, f"{project_id}.json")
        if os.path.exists(json_path):
            os.remove(json_path)

        # 2. Delete Video
        video_deleted = False
        for ext in ['.mp4', '.mov', '.avi', '.webm']:
            video_path = os.path.join(UPLOAD_DIR, project_id + ext)
            if os.path.exists(video_path):
                os.remove(video_path)
                video_deleted = True
                break

        return JSONResponse(content={"status": "success", "message": "Project deleted"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# --- 8. Meeting Notes (AI) ---
@router.post("/project/{project_id}/notes")
async def generate_notes(project_id: str):
    try:
        # 1. Load Transcript
        json_path = os.path.join(UPLOAD_DIR, f"{project_id}.json")
        if not os.path.exists(json_path):
             return JSONResponse(content={"status": "error", "message": "Transcript not found"}, status_code=404)

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            segments = data.get('segments', []) if isinstance(data, dict) else data

        # 2. Combine text
        full_text = " ".join([s.get('text', '') for s in segments])

        if not full_text.strip():
             return JSONResponse(content={"status": "error", "message": "Transcript is empty"}, status_code=400)

        # 3. Generate Notes
        # Defaulting to Uzbek as per context, but could be dynamic
        notes = notes_service.generate_meeting_notes(full_text, language="uz")

        if notes.get('error'):
            return JSONResponse(content={"status": "error", "message": notes['message']}, status_code=400)

        # 4. Save Notes
        notes_path = os.path.join(UPLOAD_DIR, f"notes_{project_id}.json")
        with open(notes_path, "w", encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=4)

        return JSONResponse(content={
            "status": "success",
            "data": notes
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@router.get("/project/{project_id}/notes")
async def get_notes(project_id: str):
    notes_path = os.path.join(UPLOAD_DIR, f"notes_{project_id}.json")
    if os.path.exists(notes_path):
        with open(notes_path, "r", encoding='utf-8') as f:
            notes = json.load(f)
        return JSONResponse(content={"status": "success", "data": notes})
    else:
        return JSONResponse(content={"status": "success", "data": None})



# Legacy Export (HTTP) - Optional, can keep or remove. Keeping for robust fallback if needed, but WS handles it now.
@router.post("/export/{project_id}")
async def export_video(project_id: str):
     return JSONResponse(content={"status": "error", "message": "Use WebSocket connection for export"}, status_code=400)

@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return RedirectResponse(url="/login?error=invalid", status_code=303)
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Create response with redirect
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        # secure=True, # Uncomment for HTTPS
        samesite="lax"
    )
    return response

@router.post("/register")
async def register(
    username: str = Form(...), # Email
    password: str = Form(...),
    full_name: str = Form(None),
    confirm_password: str = Form(None),
    db: Session = Depends(database.get_db)
):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == username).first()
    if db_user:
        return RedirectResponse(url="/login?error=exists", status_code=303)
    
    hashed_password = auth.get_password_hash(password)
    new_user = models.User(email=username, hashed_password=hashed_password, full_name=full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RedirectResponse(url="/login?success=registered", status_code=303)

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response
    return RedirectResponse(url="/login", status_code=303)
