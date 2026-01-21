import os
import uuid
import asyncio
import re
import subprocess
from backend.utils.text_normalizer import normalize_text

async def generate_dubbed_video(project_id: str, segments: list, original_video_path: str, output_dir: str, progress_callback=None):
    """
    Generates video with HARDCODED subtitles (burned in).
    original audio is kept. Tracks progress.
    """
    
    srt_filename = f"{project_id}.srt"
    srt_path = os.path.join(output_dir, srt_filename)
    
    output_video_filename = f"{project_id}_subtitled.mp4"
    output_video_path = os.path.join(output_dir, output_video_filename)

    # 1. Generate SRT
    print(f"Generating SRT for {len(segments)} segments...")
    generate_srt(segments, srt_path)
    
    # Get duration for progress
    total_duration = get_video_duration(original_video_path)
    print(f"Video Duration: {total_duration}s")

    # 2. Burn Subtitles using FFmpeg with PROGRESS
    print("Burning subtitles into video...")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", original_video_path,
        "-vf", f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,BorderStyle=4,Outline=0,Shadow=0,MarginV=30'",
        "-c:a", "copy",
        output_video_path
    ]
    
    # Run async subprocess to read stderr
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Read stderr for progress
    # FFmpeg outputs to stderr: "frame=  235 fps=0.0 q=-1.0 size=    1536kB time=00:00:09.43 bitrate=1333.6kbits/s speed=18.6x"
    
    while True:
        line = await process.stderr.readline()
        if not line:
            break
            
        line_text = line.decode('utf-8').strip()
        # Parse time
        match = re.search(r"time=(\d{2}):(\d{2}):(\d{2}\.\d+)", line_text)
        if match and total_duration > 0:
            h, m, s = match.groups()
            current_seconds = int(h) * 3600 + int(m) * 60 + float(s)
            percent = min(int((current_seconds / total_duration) * 100), 99)
            
            if progress_callback:
                await progress_callback(percent)
    
    await process.wait()
    
    if progress_callback:
        await progress_callback(100)
    
    return {
        "video_url": f"/uploads/{output_video_filename}",
        "srt_url": f"/uploads/{srt_filename}"
    }

def get_video_duration(path):
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except:
        return 0

def generate_srt(segments, output_path):
    def format_time(seconds):
        # SRT format: HH:MM:SS,mmm
        millis = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        minutes = seconds // 60
        hours = minutes // 60
        minutes %= 60
        seconds %= 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments):
            start = format_time(seg['start'])
            end = format_time(seg['end'])
            text = seg.get('translated') or seg.get('text')
            # DEBUG LOG
            if i < 3: # Print first 3 for check
                 print(f"SRT Segment {i}: Using text='{text}' (Has translated: {bool(seg.get('translated'))})")

            
            f.write(f"{i+1}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
