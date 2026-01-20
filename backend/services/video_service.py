import yt_dlp
import os
import time

def analyze_youtube_url(url: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "video_title": info.get('title', 'Noma\'lum'),
            "duration": time.strftime('%H:%M:%S', time.gmtime(info.get('duration', 0))),
            "thumbnail": info.get('thumbnail', ''),
            "original_url": url,
            "dubbing_status": "Ready to Download"
        }

def download_video(url: str, output_dir: str, filename: str):
    output_path = os.path.join(output_dir, filename)
    # Check if exists (simplification)
    if os.path.exists(output_path):
        return output_path

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.%(ext)s"),
        'quiet': True,
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return output_path
