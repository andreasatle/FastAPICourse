from fastapicourse.tailwind.main import app
from fastapi.testclient import TestClient


client = TestClient(app)

def test_healthy():
    response = client.get("/healthy")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
