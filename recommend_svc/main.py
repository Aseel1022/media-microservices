import json
import httpx
from pathlib import Path
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any

CATALOG_FILE = Path(__file__).parents[1] / "catalog-svc" / "media.json"
GEMINI_API_KEY = "ضع_مفتاحك_هنا"  # يمكن تركه فارغ مؤقتًا

# -----------------------------------
# Strategy Pattern (Single Strategy)
# -----------------------------------
class RecommendationStrategy:
    """واجهة مجردة (Base Strategy)."""
    def recommend(self, genre: str, data: List[Dict[str, Any]]) -> List[str]:
        raise NotImplementedError


class GeminiRecommendation(RecommendationStrategy):
    """استراتيجية توصية تعتمد على Gemini API فقط."""
    def recommend(self, genre: str, data: List[Dict[str, Any]]) -> List[str]:
        titles = [m["title"] for m in data]

        if not GEMINI_API_KEY:
            # بدون مفتاح، نرجع أول 3 أفلام كقائمة افتراضية
            return titles[:3]

        prompt = (
            f"You are a movie recommender. Given these movies: {titles}, "
            f"recommend 3 titles that best fit the genre '{genre}'. "
            "Return them as a simple list separated by newlines."
        )

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                    params={"key": GEMINI_API_KEY},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                )
                response.raise_for_status()
                text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                # نقسم الرد لأسطر وننظفها
                lines = [t.strip("-• ").strip() for t in text.split("\n") if t.strip()]
                return lines[:3]
        except Exception:
            # fallback بسيط في حال فشل الاتصال
            return titles[:3]


# -----------------------------------
# Context Class
# -----------------------------------
class Recommender:
    """الكلاس اللي يستخدم الاستراتيجية (GeminiRecommendation)."""
    def __init__(self, strategy: RecommendationStrategy):
        self._strategy = strategy

    def get_recommendations(self, genre: str, data: List[Dict[str, Any]]) -> List[str]:
        return self._strategy.recommend(genre, data)


# -----------------------------------
# FastAPI App
# -----------------------------------
def load_catalog():
    if not CATALOG_FILE.exists() or CATALOG_FILE.stat().st_size == 0:
        return [
            {"id": 1, "title": "Inception", "genre": "Sci-Fi"},
            {"id": 2, "title": "Interstellar", "genre": "Sci-Fi"},
            {"id": 3, "title": "The Dark Knight", "genre": "Action"},
        ]
    try:
        return json.loads(CATALOG_FILE.read_text())
    except json.JSONDecodeError:
        return []


def get_app() -> FastAPI:
    app = FastAPI(title="Recommendation Service (AI Strategy Only)")

    @app.get("/")
    def home():
        return {"message": "Welcome to AI Recommendation Service!"}

    @app.get("/recommend")
    def recommend(genre: str):
        """
        يقدم توصيات قائمة على الذكاء الاصطناعي (Gemini).
        """
        data = load_catalog()
        if not data:
            raise HTTPException(status_code=404, detail="Catalog is empty")

        recommender = Recommender(GeminiRecommendation())
        suggestions = recommender.get_recommendations(genre, data)
        return {"genre": genre, "suggestions": suggestions}

    return app
