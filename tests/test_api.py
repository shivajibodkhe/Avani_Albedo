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

def test_api_geographic_hierarchy():
    res = client.get("/api/geography/countries-and-cities")
    assert res.status_code == 200
    data = res.json()
    assert data["default_country"] == "India"
    assert data["default_city"] == "Bengaluru"
    
    country_names = [c["country"] for c in data["countries"]]
    assert "India" in country_names
    assert "United Arab Emirates" in country_names
    assert "United States" in country_names

    # Check India cities
    india = next(c for c in data["countries"] if c["country"] == "India")
    city_keys = [ct["key"] for ct in india["cities"]]
    assert "Bengaluru" in city_keys
    assert "Mumbai" in city_keys
    assert "Delhi" in city_keys
    assert "Hyderabad" in city_keys

def test_multi_city_climate_cells_and_optimization():
    # 1. Fetch Mumbai cells
    res_bom = client.get("/api/cells?city=Mumbai")
    assert res_bom.status_code == 200
    bom_cells = res_bom.json()
    assert len(bom_cells) == 6
    assert any("Dharavi" in c["name"] for c in bom_cells)

    # 2. Fetch Delhi cells
    res_del = client.get("/api/cells?city=Delhi")
    assert res_del.status_code == 200
    del_cells = res_del.json()
    assert len(del_cells) == 6
    assert any("Chandni Chowk" in c["name"] for c in del_cells)

    # 3. Optimize for Mumbai
    res_opt_bom = client.post("/api/optimize", json={
        "city": "Mumbai",
        "budget_inr": 20000000.0,
        "scenario_type": "optimized"
    })
    assert res_opt_bom.status_code == 200
    opt_bom = res_opt_bom.json()
    assert opt_bom["budget_spent_inr"] <= 20000000.0
    assert opt_bom["avg_temp_reduction_c"] > 0.0

    # 4. Compare for Delhi
    res_cmp_del = client.get("/api/scenarios/compare?budget_inr=15000000.0&city=Delhi")
    assert res_cmp_del.status_code == 200
    cmp_del = res_cmp_del.json()
    assert "scenarios" in cmp_del
    assert "green_first" in cmp_del["scenarios"]

def test_expanded_cities_and_wards():
    # Test Pune
    res_pun = client.get("/api/cells?city=Pune")
    assert res_pun.status_code == 200
    pun_cells = res_pun.json()
    assert len(pun_cells) == 5
    assert any("Shivajinagar" in c["name"] for c in pun_cells)

    # Test Chennai
    res_che = client.get("/api/cells?city=Chennai")
    assert res_che.status_code == 200
    che_cells = res_che.json()
    assert len(che_cells) == 5
    assert any("T. Nagar" in c["name"] for c in che_cells)

    # Test Kolkata
    res_ccu = client.get("/api/cells?city=Kolkata")
    assert res_ccu.status_code == 200
    ccu_cells = res_ccu.json()
    assert len(ccu_cells) == 4

def test_temperature_timeline_api():
    # 1. City-level timeline
    res = client.get("/api/temperature-timeline?city=Bengaluru")
    assert res.status_code == 200
    data = res.json()
    assert "diurnal_hours" in data
    assert len(data["diurnal_hours"]) == 9
    assert len(data["baseline_temp_c"]) == 9
    assert len(data["cooled_temp_c"]) == 9
    assert data["peak_high_c"] > data["low_temp_c"]
    assert len(data["forecast_7days"]) == 7

    # 2. Ward-specific timeline
    res_ward = client.get("/api/temperature-timeline?city=Pune&cell_id=PUN_001")
    assert res_ward.status_code == 200
    ward_data = res_ward.json()
    assert ward_data["ward_id"] == "PUN_001"
    assert "Shivajinagar" in ward_data["ward_name"]

def test_action_plan_with_persona_and_recommendations():
    res = client.post("/api/action-plan", json={
        "city": "Bengaluru",
        "budget_inr": 10000000.0,
        "scenario_type": "public_health_first",
        "persona": "Chief Public Health Officer"
    })
    assert res.status_code == 200
    plan = res.json()
    assert plan["persona"] == "Chief Public Health Officer"
    assert "strategic_recommendations" in plan
    assert len(plan["strategic_recommendations"]) > 0
    assert any("health" in r.lower() or "surveillance" in r.lower() or "asha" in r.lower() for r in plan["strategic_recommendations"])


