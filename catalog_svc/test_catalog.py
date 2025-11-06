from fastapi.testclient import TestClient
from main import get_app, load_data
from pathlib import Path
import json

app = get_app()
client = TestClient(app)
DATA_FILE = Path(__file__).parent / "media.json"

def test_home():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Welcome to Catalog Service!"}

def test_items_read():
    r = client.get("/items")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_add_item():
    new_item = {"id": 4, "title": "Tenet", "genre": "Action"}
    r = client.post("/items", json=new_item)
    assert r.status_code == 200
    result = r.json()
    assert result["status"] == "added"

    # تحقق أن العنصر الجديد محفوظ فعلاً داخل الملف
    file_data = json.loads(DATA_FILE.read_text())
    assert any(item["title"] == "Tenet" for item in file_data)
