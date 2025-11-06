from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient
from catalog_svc.main import get_app as catalog_app
from user_svc.main import get_app as user_app
from recommend_svc.main import get_app as rec_app
from api_gateway.main import get_app as gateway_app

app = FastAPI(title="Microservices UI Panel")

clients = {
    "Catalog": TestClient(catalog_app()),
    "User": TestClient(user_app()),
    "Recommendation": TestClient(rec_app()),
    "Gateway": TestClient(gateway_app()),
}

def test_service(service: str):
    """يرجع الرد المناسب حسب الخدمة"""
    if service == "Catalog":
        return clients["Catalog"].get("/items").json()
    elif service == "User":
        return clients["User"].get("/").json()
    elif service == "Recommendation":
        return clients["Recommendation"].get("/recommend?genre=Sci-Fi").json()
    elif service == "Gateway":
        return clients["Gateway"].get("/summary").json()
    return {"error": "Service not found"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <html>
        <head>
            <title>Microservices Control Panel</title>
            <style>
                body { font-family: Arial; background-color:#f9fafb; text-align:center; }
                h1 { color:#0c4a6e; }
                button { margin:10px; padding:10px 20px; border:none; border-radius:8px; background:#2563eb; color:white; cursor:pointer; }
                button:hover { background:#1e40af; }
                pre { background:#f1f5f9; padding:10px; border-radius:8px; text-align:left; width:60%; margin:auto; }
            </style>
        </head>
        <body>
            <h1>🧩 Microservices UI Panel</h1>
            <p>Click any service below to test it:</p>
            <form action="/test" method="get">
                <button name="service" value="Catalog">Test Catalog</button>
                <button name="service" value="User">Test User</button>
                <button name="service" value="Recommendation">Test Recommendation</button>
                <button name="service" value="Gateway">Test Gateway</button>
            </form>
        </body>
    </html>
    """

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request, service: str):
    result = test_service(service)
    return f"""
    <html>
        <body style="font-family:Arial; text-align:center;">
            <h2>🔹 {service} Service Result</h2>
            <pre>{result}</pre>
            <a href="/" style="text-decoration:none; color:#2563eb;">⬅ Back</a>
        </body>
    </html>
    """
