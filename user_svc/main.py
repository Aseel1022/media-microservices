import json
from pathlib import Path
from fastapi import FastAPI, HTTPException

# -----------------------------
# Design Pattern: Factory
# -----------------------------
class UserFactory:
    """
    Factory class for creating User objects in a consistent way.
    """
    @staticmethod
    def create_user(username: str, password: str):
        return {"username": username, "password": password}


# -----------------------------
# Class to handle user storage
# -----------------------------
class UserDatabase:
    def __init__(self):
        self.file = Path(__file__).parent / "users.json"
        if not self.file.exists() or self.file.stat().st_size == 0:
            default_users = [{"username": "aseel", "password": "1234"}]
            self.file.write_text(json.dumps(default_users, indent=4))

    def load(self):
        try:
            return json.loads(self.file.read_text())
        except json.JSONDecodeError:
            return []

    def save(self, users):
        self.file.write_text(json.dumps(users, indent=4))


# -----------------------------
# FastAPI Application
# -----------------------------
def get_app() -> FastAPI:
    app = FastAPI(title="User Service with Factory Pattern")
    db = UserDatabase()

    @app.get("/")
    def home():
        return {"message": "Welcome to User Service (Factory)!"}

    @app.post("/register")
    def register(user: dict):
        username = user.get("username")
        password = user.get("password")
        if not username or not password:
            raise HTTPException(status_code=400, detail="username and password required")

        users = db.load()
        if any(u["username"].lower() == username.lower() for u in users):
            raise HTTPException(status_code=400, detail="User already exists")

        # استخدام الـ Factory لإنشاء المستخدم الجديد
        new_user = UserFactory.create_user(username, password)
        users.append(new_user)
        db.save(users)
        return {"status": "registered", "username": username}

    @app.post("/login")
    def login(user: dict):
        username = user.get("username")
        password = user.get("password")
        if not username or not password:
            raise HTTPException(status_code=400, detail="username and password required")

        users = db.load()
        match = any(
            u["username"].lower() == username.lower() and u["password"] == password
            for u in users
        )
        if not match:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {"status": "success"}

    # 🔹 هذا السطر مهم جدًا، بدونه راح يصير app = None
    return app
