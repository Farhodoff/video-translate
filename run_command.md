# Loyihani ishga tushirish bo'yicha qo'llanma

Loyihani to'liq ishga tushirish uchun quyidagi buyruqlarni terminalda ketma-ket bajaring.

### 1. Loyiha papkasiga o'tish
```bash
cd video-translate
```

### 2. Virtual muhitni faollashtirish
Agar `.venv` papkasi yo'q bo'lsa, avval uni yarating:
```bash
python3 -m venv .venv
```
Keyin faollashtiring:
```bash
source .venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish
Eng so'nggi versiyalar o'rnatilishi uchun quyidagi buyruqni ishlating:
```bash
pip install "fastapi[all]" uvicorn "yt-dlp[default]" openai-whisper deep-translator edge-tts google-generativeai python-multipart requests python-dotenv
```

### 4. Tizim dasturlarini o'rnatish (Mac OS)
YouTube himoyasini aylanib o'tish va audio/video bilan ishlash uchun `node` va `ffmpeg` kerak.
```bash
brew install ffmpeg node
```

### 5. API Kalitini sozlash
`.env` nomli fayl yarating (agar yo'q bo'lsa) va ichiga Google Gemini API kalitingizni yozing:
```env
GOOGLE_API_KEY=AIzaSy...SizningKalitingiz
```
*(Yaratish uchun terminalda: `echo "GOOGLE_API_KEY=AIzaSy..." > .env`)*

### 6. Serverni ishga tushirish
Serverni `host 0.0.0.0` bilan ishga tushirish tavsiya etiladi:
```bash
./.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Server ishga tushgach, brauzerda **http://localhost:8000** manziliga kiring.

---
**Serverni to'xtatish:** Terminalda `Ctrl + C` tugmasini bosing.
