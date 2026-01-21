
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
print("Importing backend.main...")
try:
    from backend.main import app
    print("Success!")
except Exception as e:
    print(f"Error importing app: {e}")
