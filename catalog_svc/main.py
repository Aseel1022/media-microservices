import json
from fastapi import FastAPI
from pathlib import Path
from threading import Lock

# -----------------------------
# Design Pattern: Singleton
# -----------------------------
class CatalogDatabase:
    """
    Singleton class to manage catalog data (media.json).
    Ensures only one instance handles file I/O.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.data_file = Path(__file__).parent / "media.json"
                cls._instance._init_data()
            return cls._instance

    def _init_data(self):
        """Initialize the data file if not found."""
        if not self.data_file.exists() or self.data_file.stat().st_size == 0:
            default_data = [
                {"id": 1, "title": "Inception", "genre": "Sci-Fi"},
                {"id": 2, "title": "Interstellar", "genre": "Sci-Fi"},
                {"id": 3, "title": "The Dark Knight", "genre": "Action"},
            ]
            self.data_file.write_text(json.dumps(default_data, indent=4))

    def load(self):
        return json.loads(self.data_file.read_text())

    def save(self, data):
        self.data_file.write_text(json.dumps(data, indent=4))


# -----------------------------
# FastAPI app using Singleton
# -----------------------------
def get_app() -> FastAPI:
    app = FastAPI(title="Catalog Service with Singleton")
    db = CatalogDatabase()  # نفس الكائن يُستخدم في كل مرة

    @app.get("/")
    def home():
        return {"message": "Welcome to Catalog Service (Singleton)!"}

    @app.get("/items")
    def get_items():
        return db.load()

    @app.post("/items")
    def add_item(item: dict):
        data = db.load()
        if "id" not in item or any(x["id"] == item["id"] for x in data):
            item["id"] = (max(x["id"] for x in data) + 1) if data else 1
        data.append(item)
        db.save(data)
        return {"status": "added", "total": len(data)}

    return app
