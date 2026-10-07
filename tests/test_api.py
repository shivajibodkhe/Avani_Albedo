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

def test_api_auth():
    # 1. Config
    res_cfg = client.get("/api/auth/config")
    assert res_cfg.status_code == 200
    cfg = res_cfg.json()
    assert "auth_enabled" in cfg
    assert "default_judge_email" in cfg

    # 2. Valid Login for judge
    res_valid = client.post("/api/auth/login", json={
        "email": "judge@hackathon.com",
        "password": "avani2026"
    })
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["status"] == "success"
    assert "token" in data

    # 3. Invalid Login (wrong password)
    res_invalid_pw = client.post("/api/auth/login", json={
        "email": "judge@hackathon.com",
        "password": "wrongpassword"
    })
    assert res_invalid_pw.status_code == 401

    # 4. Invalid Login (unauthorized email)
    res_invalid_email = client.post("/api/auth/login", json={
        "email": "intruder@stranger.org",
        "password": "avani2026"
    })
    assert res_invalid_email.status_code == 401
