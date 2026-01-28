from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Dublyaj Studiyasi - Vercel Test</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: #1a1a1a;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #2d2d2d;
            padding: 2rem;
            border-radius: 1rem;
            text-align: center;
            max-width: 400px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { color: #10b981; margin-bottom: 0.5rem; }
        p { color: #a1a1aa; line-height: 1.5; }
        .b { font-weight: bold; color: #fff; }
        .btn {
            display: inline-block;
            margin-top: 1.5rem;
            padding: 0.75rem 1.5rem;
            background: #3b82f6;
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            transition: background 0.2s;
        }
        .btn:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="card">
        <h1>✅ Ishlayapti!</h1>
        <p>Vercel Serverless Function muvaffaqiyatli ishga tushdi.</p>
        <br>
        <p>Bu <span class="b">Test Versiya</span> bo'lib, faqat sayt ko'rinishini tekshirish uchun.</p>
        <p>To'liq AI funksiyalar (video, audio) <br>faqat Render.com da ishlaydi.</p>
        
        <a href="https://render.com" class="btn">Render.com ga o'tish</a>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return html_content

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "platform": "vercel-serverless"}

# Vercel entry point
handler = app
