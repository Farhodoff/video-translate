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
# Lokalda 127.0.0.1:9000 da ishga tushirish uchun (HOST va PORT o'zgaruvchilarini o'rnating)
export PYTHONPATH=$PYTHONPATH:$(pwd) && HOST=127.0.0.1 PORT=9000 python3 backend/main.py
```

Server ishga tushgach, brauzerda **http://127.0.0.1:9000** manziliga kiring.

Agar boshqa port yoki host kerak bo'lsa, `HOST` va `PORT` muhit o'zgaruvchilarini o'zgartiring. Masalan:

```bash
# Portni 8000 ga o'zgartirish
export PYTHONPATH=$PYTHONPATH:$(pwd) && HOST=127.0.0.1 PORT=8000 python3 backend/main.py
```

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

Loyiha **Render.com**, **Railway** yoki **Heroku** kabi platformalarda ishlashga tayyorlangan.

### Render.com orqali joylash (Tavsiya etiladi) ⭐

Render.com barcha AI funksiyalarni to'liq qo'llab-quvvatlaydi va deploy qilish juda oson.

**Tezkor yo'l:**

1. **GitHub** ga loyihani yuklang (allaqachon yuklangan)
2. [Render.com](https://render.com) da ro'yxatdan o'ting
3. **New + → Blueprint** ni tanlang
4. `Farhodoff/video-translate` repositoriyasini ulang
5. `GOOGLE_API_KEY` environment variable qo'shing
6. **Apply** tugmasini bosing

`render.yaml` fayli avtomatik aniqlaydi va barcha sozlamalarni bajaradi.

**To'liq qo'llanma**: [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) faylida batafsil ko'rsatmalar mavjud.

**Environment Variables:**
- `.env.example` faylini `.env` ga nusxalang
- Kerakli API kalitlarni to'ldiring

### Muhit o'zgaruvchilari (Environment Variables)

Loyiha ishlashi uchun quyidagi o'zgaruvchilar kerak:

```bash
# Google AI API key (Meeting Notes feature uchun)
GOOGLE_API_KEY=your_api_key_here
```


### Docker orqali ishga tushirish

Agar siz Docker ishlatmoqchi bo'lsangiz:

```bash
# Docker imageni yaratish
docker build -t video-translate .

# Konteynerni ishga tushirish
docker run -p 8000:8000 video-translate
```
