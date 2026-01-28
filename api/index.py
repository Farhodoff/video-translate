from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

# Simple HTML homepage for testing
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Dublyaj Studiyasi - Vercel Test</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 { font-size: 3em; margin-bottom: 20px; }
            p { font-size: 1.2em; margin: 10px 0; opacity: 0.9; }
            .status { 
                display: inline-block;
                padding: 10px 20px;
                background: #10b981;
                border-radius: 25px;
                margin-top: 20px;
                font-weight: bold;
            }
            a {
                color: #60a5fa;
                text-decoration: none;
                font-weight: 500;
            }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 AI Dublyaj Studiyasi</h1>
            <p>Vercel test deployment muvaffaqiyatli!</p>
            <div class="status">✅ Serverless Function Ishlayapti</div>
            <p style="margin-top: 30px; font-size: 1em;">
                To'liq funksional loyiha uchun 
                <a href="https://render.com" target="_blank">Render.com</a> 
                platformasiga o'ting
            </p>
        </div>
    </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Vercel deployment successful",
        "platform": "Vercel Serverless",
        "note": "For full AI features, deploy to Render.com"
    }

# For Vercel
handler = app
