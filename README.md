# Video Translate (AI Dublyaj Studiyasi)

Ushbu loyiha sun'iy intellekt (AI) yordamida videolarni tahlil qilish, audioni matnga aylantirish (transkripsiya) va O'zbek tiliga tarjima qilish uchun mo'ljallangan veb-lova.

## 🚀 Imkoniyatlar

*   **Video Tahlil:** YouTube yoki boshqa video platformalardan havolalar orqali videoni aniqlash (`yt-dlp`).
*   **Video Yuklash:** Mahalliy kompyuterdan video fayllarni (`.mp4`, `.mov`, `.avi`) yuklash.
*   **AI Transkripsiya:** **OpenAI Whisper** modeli yordamida videodagi nutqni matnga aylantirish (Speech-to-Text).
*   **Avtomatik Tarjima:** Matnlarni **Google Translate** orqali O'zbek tiliga o'girish.
*   **Zamonaviy Interfeys:** Dark mode va qulay foydalanuvchi tajribasi (UX).

## 🛠 Texnologiyalar

Loyiha quyidagi texnologiyalar asosida qurilgan:

*   **Backend:** Python (FastAPI)
*   **AI Model:** OpenAI Whisper (Mahalliy "base" model)
*   **Video Ishlovi:** FFmpeg, yt-dlp
*   **Tarjima:** deep-translator (Google Translate)
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla)

## 📦 O'rnatish va Ishga Tushirish

Loyihani o'z kompyuteringizda ishga tushirish uchun quyidagi qadamlarni bajaring:

### 1. Talablar
*   Python 3.8+
*   FFmpeg (Tizimga o'rnatilgan bo'lishi shart)

### 2. Loyihani yuklab olish
```bash
git clone https://github.com/Farhodoff/video-translate.git
cd video-translate
```

### 3. Kerakli kutubxonalarni o'rnatish
Virtual muhit yaratish tavsiya etiladi:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows uchun: .venv\Scripts\activate
```

Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

### 4. Dasturni ishga tushirish
Terminalda loyiha papkasida turib, quyidagi buyruqni bering:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd) && python3 backend/main.py
```

Server ishga tushgach, brauzerda **http://127.0.0.1:8000** manziliga kiring.

## 📂 Loyiha Tuzilmasi

```
video-translate/
├── main.py                # Asosiy Backend server
├── requirements.txt       # Kutubxonalar ro'yxati
├── static/                # Statik fayllar (CSS, JS, Images)
├── templates/             # HTML shablonlar
├── uploads/               # Yuklangan video va audio fayllar
└── README.md              # Loyiha hujjati
```

## 📝 Muallif

Farhodoff

## 🚀 Deploy (Serverga joylash)

Loyiha **Render**, **Railway** yoki **Heroku** kabi platformalarda ishlashga tayyorlangan.

### Render.com orqali joylash (Tavsiya etiladi)

1. **GitHub** ga loyihani yuklang.
2. **Render.com** da ro'yxatdan o'ting.
3. **Blueprints** bo'limiga o'ting va `New Blueprint Instance` tugmasini bosing.
4. GitHub repozitoriysingizni ulang.
5. `render.yaml` faylini avtomatik aniqlaydi va barcha sozlamalarni o'zi bajaradi.

### Docker orqali ishga tushirish

Agar siz Docker ishlatmoqchi bo'lsangiz:

```bash
# Docker imageni yaratish
docker build -t video-translate .

# Konteynerni ishga tushirish
docker run -p 8000:8000 video-translate
```
