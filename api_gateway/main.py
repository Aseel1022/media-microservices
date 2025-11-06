from fastapi import FastAPI
from fastapi.testclient import TestClient

# استيراد الخدمات الأخرى
from catalog_svc.main import get_app as catalog_app
from user_svc.main import get_app as user_app
from recommend_svc.main import get_app as rec_app


# -------------------------------------
# Design Pattern: Facade
# -------------------------------------
class ServiceFacade:
    """
    Facade class to simplify communication between multiple microservices.
    It hides complexity by providing a unified interface to access all services.
    """
    def __init__(self):
        self.user_client = TestClient(user_app())
        self.catalog_client = TestClient(catalog_app())
        self.recommend_client = TestClient(rec_app())

    def get_user_info(self):
        res = self.user_client.get("/")
        return res.json()

    def get_catalog_items(self):
        res = self.catalog_client.get("/items")
        return res.json()

    def get_recommendations(self, genre: str = "Sci-Fi"):
        res = self.recommend_client.get(f"/recommend?genre={genre}")
        return res.json()

    def get_system_summary(self):
        user_info = self.get_user_info()
        items = self.get_catalog_items()
        recs = self.get_recommendations()

        return {
            "UserService": user_info,
            "CatalogCount": len(items),
            "FirstItem": items[0] if items else None,
            "Recommendations": recs,
        }


# -------------------------------------
# FastAPI App (uses the Facade)
# -------------------------------------
def get_app() -> FastAPI:
    app = FastAPI(title="API Gateway with Facade Pattern")
    facade = ServiceFacade()

    @app.get("/")
    def home():
        return {"message": "Welcome to API Gateway (Facade)!"}

    @app.get("/summary")
    def summary():
        """
        Unified endpoint that aggregates info from all services
        using the Facade Pattern.
        """
        return facade.get_system_summary()

    return app
