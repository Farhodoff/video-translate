
import pytest
from unittest.mock import patch, MagicMock

def test_health_check(test_client):
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("backend.services.video_service.analyze_youtube_url")
def test_analyze_url(mock_analyze, test_client):
    mock_analyze.return_value = {
        "title": "Test Video",
        "thumbnail": "http://example.com/thumb.jpg",
        "duration": 120
    }
    
    response = test_client.post("/api/analyze-url", data={"url": "http://youtube.com/watch?v=123"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["title"] == "Test Video"

@patch("backend.services.video_service.download_video")
@patch("backend.services.transcription_service.transcribe_file")
def test_process_video(mock_transcribe, mock_download, test_client):
    mock_download.return_value = "uploads/test.mp4"
    mock_transcribe.return_value = [
        {"start": 0, "end": 10, "text": "Hello world"}
    ]
    
    response = test_client.post("/api/process-video", data={
        "url": "http://youtube.com/watch?v=123",
        "original_title": "Test Video"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["segments"]) == 1

def test_get_nonexistent_project(test_client):
    response = test_client.get("/api/project/nonexistent_id")
    # Verify 404 behavior based on implementation
    assert response.status_code == 404
