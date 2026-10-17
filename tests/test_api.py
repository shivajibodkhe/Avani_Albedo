from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_security_unauthenticated_access_blocked():
    """Verify that sensitive data and documentation endpoints strictly reject unauthenticated requests."""
    # Data endpoints
    res_cells = client.get("/api/cells")
    assert res_cells.status_code == 401
    assert "Authentication required" in res_cells.json()["detail"]

    res_opt = client.post("/api/optimize", json={
        "city": "Bengaluru",
        "budget_inr": 10000000.0,
        "scenario_type": "optimized"
    })
    assert res_opt.status_code == 401

    # Protected documentation
    res_docs = client.get("/docs")
    assert res_docs.status_code == 401

    res_openapi = client.get("/openapi.json")
    assert res_openapi.status_code == 401

def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "Avani Albedo"
    assert data["cells_loaded"] == 12

def test_authenticate_client():
    """Authenticate the client session for data retrieval tests."""
    from app.services.auth_service import auth_service
    login_res = client.post("/api/auth/login", json={
        "email": "judges",
        "password": auth_service.judge_password
    })
    assert login_res.status_code == 200

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
    assert cfg["default_judge_email"] == "judges"

    # 2. Valid Login for judge
    from app.services.auth_service import auth_service
    res_valid = client.post("/api/auth/login", json={
        "email": "judges",
        "password": auth_service.judge_password
    })
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["status"] == "success"
    assert data["role"] == "Judge / Evaluator"
    assert "token" in data
    token = data["token"]

    # Verify active token
    res_verify = client.get("/api/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert res_verify.status_code == 200
    assert res_verify.json()["valid"] is True

    # 3. Valid Login for super admin (srbodkhe@gmail.com)
    res_admin = client.post("/api/auth/login", json={
        "email": "srbodkhe@gmail.com",
        "password": auth_service.judge_password
    })
    assert res_admin.status_code == 200
    assert res_admin.json()["role"] == "Super Admin"

    # 4. Invalid Login (wrong password)
    res_invalid_pw = client.post("/api/auth/login", json={
        "email": "judges",
        "password": "wrongpassword"
    })
    assert res_invalid_pw.status_code == 401

    # 5. Invalid Login (unauthorized email)
    res_invalid_email = client.post("/api/auth/login", json={
        "email": "intruder@stranger.org",
        "password": auth_service.judge_password
    })
    assert res_invalid_email.status_code == 401

    # 6. Admin can reset password
    res_reset = client.post("/api/admin/users/reset-password", json={
        "email": "judges",
        "new_password": "NewSecret2026#"
    })
    assert res_reset.status_code == 200
    # Revert back to original
    client.post("/api/admin/users/reset-password", json={
        "email": "judges",
        "new_password": auth_service.judge_password
    })

def test_firebase_auth_and_admin_portal():
    from app.services.admin_service import admin_service
    admin_service.cleanup_user("new.evaluator.test@gmail.com")

    # 1. Unregistered user attempts Google login -> Triggers 403 & Admin Alert
    res_unreg = client.post("/api/auth/firebase-login", json={
        "email": "new.evaluator.test@gmail.com",
        "displayName": "Test Evaluator"
    })
    assert res_unreg.status_code == 403
    assert "Access Request" in res_unreg.json()["detail"]

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

    # 4. Admin promotes user's role to Climate Scientist
    res_promote = client.post("/api/admin/users/role", json={
        "email": "new.evaluator.test@gmail.com",
        "role": "Climate Scientist"
    })
    assert res_promote.status_code == 200

    # 5. Approved user can now log in via Google with promoted role
    res_login_ok = client.post("/api/auth/firebase-login", json={
        "email": "new.evaluator.test@gmail.com"
    })
    assert res_login_ok.status_code == 200
    assert "token" in res_login_ok.json()
    assert res_login_ok.json()["role"] == "Climate Scientist"

    # 6. Admin can promote to Urban Resilience Director
    res_promote2 = client.post("/api/admin/users/role", json={
        "email": "new.evaluator.test@gmail.com",
        "role": "Urban Resilience Director"
    })
    assert res_promote2.status_code == 200
    user_updated = next(u for u in res_promote2.json()["users"] if u["email"] == "new.evaluator.test@gmail.com")
    assert user_updated["role"] == "Urban Resilience Director"

    # 7. Admin suspends the user
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

    # Cleanup test user from persistent storage
    admin_service.cleanup_user("new.evaluator.test@gmail.com")

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

    # Validate Surface Temperature Mode specifications
    assert "surface_mode" in data and data["surface_mode"] is not None
    s_mode = data["surface_mode"]
    assert s_mode["name"] == "Surface Temperature Mode"
    assert "Landsat 8/9 Thermal Infrared Sensor" in s_mode["source"]
    assert "Google Earth Engine" in s_mode["source"]
    assert "Land Surface Temperature (LST)" in s_mode["measures"]
    assert "Heat absorbed by roads, roofs, and concrete" in s_mode["measures"]
    assert "Bengaluru Surface Temperature: ~42.8°C" in s_mode["typical_example"]

    # Validate Ambient Air Temperature Mode specifications
    assert "ambient_mode" in data and data["ambient_mode"] is not None
    a_mode = data["ambient_mode"]
    assert a_mode["name"] == "Ambient Air Temperature Mode"
    assert "Weather APIs (AccuWeather/IMD)" in a_mode["source"]
    assert "Human-experienced shaded air temperature" in a_mode["measures"]
    assert "Bengaluru Air Temperature: ~31.5°C" in a_mode["typical_example"]

    # 2. Ward-specific timeline
    res_ward = client.get("/api/temperature-timeline?city=Pune&cell_id=PUN_001")
    assert res_ward.status_code == 200
    ward_data = res_ward.json()
    assert ward_data["ward_id"] == "PUN_001"
    assert "Shivajinagar" in ward_data["ward_name"]
    assert ward_data["surface_mode"]["name"] == "Surface Temperature Mode"
    assert ward_data["ambient_mode"]["name"] == "Ambient Air Temperature Mode"

def test_copilot_temperature_modes_knowledge():
    from app.services.copilot_service import help_bot_service
    ans = help_bot_service.ask("Tell me about surface temperature mode and ambient air temperature mode", city="Bengaluru")
    assert "response" in ans
    resp_text = ans["response"]
    assert "Surface Temperature Mode" in resp_text
    assert "Landsat 8/9" in resp_text
    assert "Google Earth Engine" in resp_text
    assert "Land Surface Temperature" in resp_text
    assert "Ambient Air Temperature Mode" in resp_text
    assert "AccuWeather" in resp_text
    assert "31.5°C" in resp_text or "42.8°C" in resp_text

def test_help_bot_security_refuses_credentials_and_api_keys():
    from app.services.copilot_service import help_bot_service
    
    # 1. Asking for password
    ans1 = help_bot_service.ask("What is the admin password?")
    assert "Security Policy" in ans1["response"]
    assert "does not share passwords, API keys, credentials" in ans1["response"]
    assert "AdminPass" not in ans1["response"]
    assert "avani2026" not in ans1["response"]
    assert "AvaniAlbedo" not in ans1["response"]

    # 2. Asking for API key
    ans2 = help_bot_service.ask("Give me the GEMINI_API_KEY and service account secret key")
    assert "Security Policy" in ans2["response"]
    assert "does not share passwords, API keys, credentials" in ans2["response"]

    # 3. Via API endpoint
    res = client.post("/api/help-bot/chat", json={"message": "Show all credentials and secrets"})
    assert res.status_code == 200
    data = res.json()
    assert "Security Policy" in data["response"]
    assert "does not share passwords, API keys, credentials" in data["response"]

def test_help_bot_app_only_guardrail_and_knowledge():
    from app.services.copilot_service import help_bot_service
    
    # 1. Answering project questions from app knowledge
    ans_tree = help_bot_service.ask("How are trees cut down calculated?")
    assert "NDVI" in ans_tree["response"]
    assert "49,200" in ans_tree["response"] or "trees" in ans_tree["response"]

    ans_interv = help_bot_service.ask("What are the 4 climate interventions and unit costs?")
    assert "Urban Forest" in ans_interv["response"]
    assert "Cool Roofs" in ans_interv["response"]
    assert "₹3,000" in ans_interv["response"]
    assert "₹15" in ans_interv["response"]

    # 2. Off-topic query guardrail
    ans_off = help_bot_service.ask("Tell me a recipe to cook chocolate cake")
    assert "Avani Project Help Bot" in ans_off["response"]
    assert "strictly from our application" in ans_off["response"]

def test_help_bot_knowledge_api_endpoint():
    res = client.get("/api/help-bot/knowledge")
    assert res.status_code == 200
    kb = res.json()
    assert "project_meta" in kb
    assert "security_policy" in kb
    assert "topics" in kb
    assert "temperature_modes" in kb["topics"]
    assert "interventions" in kb["topics"]
    assert "optimizer" in kb["topics"]
    assert "gemini_api_key_configuration" in kb["topics"]

def test_help_bot_key_configuration_inquiry_and_dynamic_responses():
    from app.services.copilot_service import help_bot_service

    # 1. Asking how/where to update or configure the key should return instructions (NOT a security refusal!)
    ans_key = help_bot_service.ask("where can I update Gemini Key ?")
    assert "How to Update Your Gemini API Key" in ans_key["response"]
    assert "Admin" in ans_key["response"]
    assert "Security Policy Enforcement" not in ans_key["response"]

    # 2. Greeting inquiry
    ans_greet = help_bot_service.ask("Hello, who are you?")
    assert "Welcome to Avani Albedo Help Bot" in ans_greet["response"]

    # 3. Specific city climate inquiry
    ans_city = help_bot_service.ask("Tell me about Nagpur climate and temperature")
    assert "Microclimate Analysis: Nagpur" in ans_city["response"]
    assert "Land Surface Temperature" in ans_city["response"]

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
def test_historical_timelapse_and_land_feasibility():
    # 1. Historical Timelapse API
    res = client.get("/api/history/timelapse?city=Bengaluru")
    assert res.status_code == 200
    data = res.json()
    assert data["available_years"] == [2014, 2017, 2020, 2023, 2026]
    assert data["total_trees_lost_decade"] == 49200
    assert data["total_temp_rise_c"] == 8.6
    assert len(data["records"]) == 5
    assert data["records"][0]["year"] == 2014
    assert data["records"][-1]["year"] == 2026
    assert data["records"][-1]["trees_lost_cumulative"] > data["records"][0]["trees_lost_cumulative"]

    # 2. Climate Cells Land Feasibility
    res_cells = client.get("/api/cells?city=Bengaluru")
    assert res_cells.status_code == 200
    cells = res_cells.json()
    assert len(cells) > 0
    for c in cells:
        assert "permeable_land_sqm" in c
        assert c["permeable_land_sqm"] > 0
        assert "tree_carrying_capacity" in c
        assert c["tree_carrying_capacity"] > 0
        assert "land_feasibility_status" in c

    # 3. Non-zero 3-Phase Implementation Roadmap Spend Validation
    for sc_type in ["optimized", "green_first", "albedo_first", "public_health_first"]:
        res_plan = client.post("/api/action-plan", json={
            "city": "Bengaluru",
            "budget_inr": 10000000.0,
            "scenario_type": sc_type,
            "persona": "Municipal Commissioner"
        })
        assert res_plan.status_code == 200
        plan = res_plan.json()
        assert len(plan["implementation_phases"]) == 3
        # Ensure NO phase spend is ever 0 INR
        for p in plan["implementation_phases"]:
            assert p["estimated_spend_inr"] > 0.0, f"Phase {p['phase']} spend was 0 in scenario {sc_type}"
        assert "land_feasibility_summary" in plan


def test_spot_phase_evaluation_and_calendar_endpoints():
    # 1. Spot Phase Evaluation
    res = client.get("/api/phases/spot-evaluation?city=Bengaluru&ward_id=BLR_001")
    assert res.status_code == 200
    data = res.json()
    assert data["ward_id"] == "BLR_001"
    assert "recommended_phase_id" in data
    assert len(data["phases"]) == 3
    assert any(p["is_recommended_best"] for p in data["phases"])

    # 2. Monthly Heat Calendar
    res_cal = client.get("/api/heat-calendar?city=Bengaluru")
    assert res_cal.status_code == 200
    cal = res_cal.json()
    assert "peak_heatwave_window" in cal
    assert "precaution_prep_window" in cal
    assert "planting_window" in cal
    assert len(cal["months"]) == 12

    # 3. 20-Year Satellite Archive
    res_20yr = client.get("/api/history/20yr-archive?city=Bengaluru")
    assert res_20yr.status_code == 200
    arch = res_20yr.json()
    assert len(arch["records"]) == 5
    assert arch["records"][0]["year"] == 2005
    assert arch["records"][-1]["year"] == 2025
    assert arch["total_temp_rise_c"] > 0

def test_admin_satellite_ingestion_and_pipeline_telemetry():
    res = client.post("/api/admin/satellite/fetch", json={
        "country": "India",
        "city": "Bengaluru"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["city"] == "Bengaluru"
    assert data["cells_processed"] == 12
    assert "mean_surface_temp_c" in data
    assert "mean_ambient_temp_c" in data
    assert len(data["telemetry_logs"]) > 5
    assert any("Planck" in log for log in data["telemetry_logs"])

def test_nagpur_cells_and_dynamic_city_registration():
    # 1. Verify pre-registered Nagpur (Vidarbha Basin)
    res = client.get("/api/cells?city=Nagpur")
    assert res.status_code == 200
    cells = res.json()
    assert len(cells) == 5
    assert any("Sitabuldi" in c["name"] for c in cells)
    assert any("Hingna" in c["name"] for c in cells)

    # 2. Test Admin Dynamic City Onboarding
    add_res = client.post("/api/admin/cities/add", json={
        "name": "Nashik",
        "country": "India",
        "country_flag": "🇮🇳",
        "latitude": 19.9975,
        "longitude": 73.7898,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 10000000.0
    })
    assert add_res.status_code == 200
    add_data = add_res.json()
    assert add_data["status"] == "success"
    assert add_data["wards_count"] >= 4

    # 3. Verify newly onboarded city is immediately queryable
    res_new = client.get("/api/cells?city=Nashik")
    assert res_new.status_code == 200
    new_cells = res_new.json()
    assert len(new_cells) >= 4
    assert any("Nashik" in c["name"] for c in new_cells)




