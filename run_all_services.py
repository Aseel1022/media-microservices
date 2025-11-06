# run_all_services.py
import sys, os
from fastapi.testclient import TestClient

# تأكد أن المسار الحالي مضاف حتى يتعرف Python على الحزم
sys.path.append(os.getcwd())

# استيراد التطبيقات
from catalog_svc.main import get_app as catalog_app
from user_svc.main import get_app as user_app
from recommend_svc.main import get_app as rec_app
from api_gateway.main import get_app as gateway_app

def run_service_test(name, client, endpoint="/"):
    """تشغيل اختبار بسيط لأي خدمة"""
    print(f"\n🟦 Testing {name}")
    try:
        response = client.get(endpoint)
        print(f"✅ Success: {response.status_code}")
        print("Response:", response.json())
    except Exception as e:
        print(f"❌ Error in {name}: {e}")

def main():
    print("🚀 Running all service checks...\n")

    # 1️⃣ Catalog Service
    cat_client = TestClient(catalog_app())
    run_service_test("Catalog Service", cat_client, "/")

    # 2️⃣ User Service
    usr_client = TestClient(user_app())
    run_service_test("User Service", usr_client, "/")

    # 3️⃣ Recommendation Service
    rec_client = TestClient(rec_app())
    run_service_test("Recommendation Service", rec_client, "/recommend?genre=Sci-Fi")

    # 4️⃣ API Gateway
    gate_client = TestClient(gateway_app())
    run_service_test("API Gateway", gate_client, "/summary")

    print("\n🎉 All service checks completed!")

if __name__ == "__main__":
    main()
 