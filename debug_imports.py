
print("Importing os...")
import os
print("Importing fastapi...")
from fastapi import FastAPI
print("Importing torch...")
import torch
print("Importing whisper...")
import whisper
print("Importing google.generativeai...")
import google.generativeai as genai
print("Importing deep_translator...")
from deep_translator import GoogleTranslator
print("Importing edge_tts...")
import edge_tts
print("Importing yt_dlp...")
import yt_dlp

print("Importing backend.main...")
try:
    from backend.main import app
    print("Success! All dependencies loaded correctly.")
except Exception as e:
    print(f"Error importing app: {e}")
    exit(1)
