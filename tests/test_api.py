from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "Avani Albedo"
    assert data["cells_loaded"] == 12

def test_api_cells():
    response = client.get("/api/cells")
    assert response.status_code == 200
    cells = response.json()
    assert len(cells) == 12
    assert "hvi_score" in cells[0]

def test_api_optimize():
    response = client.post("/api/optimize", json={
        "city": "Bengaluru",
        "budget_inr": 10000000.0,
        "scenario_type": "optimized"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["budget_spent_inr"] <= 10000000.0
    assert data["avg_temp_reduction_c"] > 0.0

def test_api_action_plan():
    response = client.post("/api/action-plan", json={
        "city": "Bengaluru",
        "budget_inr": 5000000.0,
        "scenario_type": "green_first"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["ward_priorities"]) > 0
    assert len(data["implementation_phases"]) == 3

def test_api_compare():
    response = client.get("/api/scenarios/compare?budget_inr=10000000.0")
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert "optimized" in data["scenarios"]
    assert "green_first" in data["scenarios"]
