# Video Translate — Frontend

React + Vite + TypeScript asosida qurilgan AI dublyaj platformasining frontend ilovasi.

## 🛠 Texnologiyalar

- **React 18** + **TypeScript**
- **Vite 7** — Build tool
- **TailwindCSS v4** — Styling
- **React Router v6** — Routing
- **Axios** — API so'rovlar (Bearer Token)

## 🚀 Ishga tushirish

```bash
npm install
npm run dev
# http://localhost:5173
```

## 🔗 Backend

Backend API: [video-translate-back](https://github.com/Farhodoff/video-translate-back)

Dev rejimida `vite.config.ts` dagi proxy `/api` → `http://127.0.0.1:8000` ga yo'naltiradi.

Production uchun `.env` fayliga:
```
VITE_API_URL=https://your-backend.onrender.com
```

## 📋 Sahifalar

| Yo'l | Sahifa |
|------|--------|
| `/` | Landing |
| `/login` | Kirish |
| `/register` | Ro'yxatdan o'tish |
| `/dashboard` | Boshqaruv paneli (himoyalangan) |

## 👤 Muallif

[Farhodoff](https://github.com/Farhodoff)
