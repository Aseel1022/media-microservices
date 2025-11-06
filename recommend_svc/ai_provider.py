import json
import httpx
from pathlib import Path
from fastapi import FastAPI, HTTPException

CATALOG_FILE = Path(__file__).parents[1] / "catalog-svc" / "media.json"
GEMINI_API_KEY = "ضع_مفتاحك_هنا"  # أو استخدمي متغير بيئة لاحقًا

def load_catalog():
    if not CATALOG_FILE.exists() or CATALOG_FILE.stat().st_size == 0:
        return [
            {"id": 1, "title": "Inception", "genre": "Sci-Fi"},
            {"id": 2, "title": "Interstellar", "genre": "Sci-Fi"},
            {"id": 3, "title": "The Dark Knight", "genre": "Action"},
        ]
    return json.loads(CATALOG_FILE.read_text())

def gemini_recommend(genre: str, titles: list[str]):
    """
    طلب بسيط من Gemini لإرجاع اقتراحات نصية.
    """
    if not GEMINI_API_KEY:
        # وضع افتراضي بدون API Key
        return titles[:3]

    prompt = (
        f"You are a movie recommendation system. Given genre '{genre}' "
        f"and these titles: {titles}, recommend 3 similar ones."
    )

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                params={"key": GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return text.split("\n")[:3]
    except Exception:
        return titles[:3]

def get_app() -> FastAPI:
    app = FastAPI(title="Recommendation Service with Gemini")

    @app.get("/")
    def home():
        return {"message": "Welcome to Recommendation Service!"}

    @app.get("/recommend/ai")
    def recommend_ai(genre: str):
        """
        توصية بسيطة تعتمد على Gemini أو على نتائج افتراضية في حال عدم وجود مفتاح.
        """
        data = load_catalog()
        titles = [m["title"] for m in data]
        suggestions = gemini_recommend(genre, titles)
        return {"genre": genre, "suggestions": suggestions}

    return app
