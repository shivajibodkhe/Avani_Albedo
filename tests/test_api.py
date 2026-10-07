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

def test_firebase_auth_and_admin_portal():
    # 1. Unregistered user attempts Firebase login -> Triggers 403 & Admin Alert
    res_unreg = client.post("/api/auth/firebase-login", json={
        "email": "new.evaluator.test@gmail.com",
        "displayName": "Test Evaluator"
    })
    assert res_unreg.status_code == 403
    assert "Access Request Sent" in res_unreg.json()["detail"]

    # 2. Check Admin Dashboard sees the alert and the new user
    res_dash = client.get("/api/admin/dashboard")
    assert res_dash.status_code == 200
    dash = res_dash.json()
    assert "users" in dash
    assert "alerts" in dash
    assert "quotas" in dash
    assert any(u["email"] == "new.evaluator.test@gmail.com" for u in dash["users"])

    # 3. Admin approves the user
    res_act = client.post("/api/admin/users/action", json={
        "email": "new.evaluator.test@gmail.com",
        "action": "approve"
    })
    assert res_act.status_code == 200

    # 4. Approved user can now log in via Firebase
    res_login_ok = client.post("/api/auth/firebase-login", json={
        "email": "new.evaluator.test@gmail.com"
    })
    assert res_login_ok.status_code == 200
    assert "token" in res_login_ok.json()

    # 5. Admin suspends the user
    res_susp = client.post("/api/admin/users/action", json={
        "email": "new.evaluator.test@gmail.com",
        "action": "suspend"
    })
    assert res_susp.status_code == 200

    # 6. Suspended user login attempt is blocked
    res_login_blocked = client.post("/api/auth/firebase-login", json={
        "email": "new.evaluator.test@gmail.com"
    })
    assert res_login_blocked.status_code == 403
    assert "suspended" in res_login_blocked.json()["detail"].lower()

    # 7. Admin updates settings
    res_sett = client.post("/api/admin/settings", json={
        "gemini_api_key": "AIzaSyTestUpdatedKey999",
        "gcp_project_id": "genai-2026-custom"
    })
    assert res_sett.status_code == 200
    assert res_sett.json()["config"]["gcp_project_id"] == "genai-2026-custom"
