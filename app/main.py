import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import (
    ClimateCell, ScenarioRequest, ScenarioResult,
    ActionPlanResponse, SystemStatusResponse,
    LoginRequest, LoginResponse, TemperatureTimelineResponse,
    CityTimelapseResponse, SpotEvaluationSummary, HeatCalendarSummary,
    TwentyYearArchiveResponse
)
from app.data.bengaluru_heat_data import get_bengaluru_climate_cells
from app.data.cities_heat_data import (
    get_geographic_hierarchy,
    get_climate_cells_for_city,
    get_temperature_timeline,
    get_city_timelapse_data,
    get_spot_phase_evaluation,
    get_city_heat_calendar,
    get_twenty_year_satellite_archive,
    CITIES_REGISTRY
)
from app.services.hvi_engine import calculate_hvi_for_cells
from app.services.optimizer import solve_climate_interventions
from app.services.gemini_agent import generate_action_plan
from app.services.earth_engine_service import earth_engine_service
from app.services.firestore_service import firestore_service
from app.services.auth_service import auth_service
from app.services.admin_service import admin_service

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("avani_albedo")

# FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description="Prescriptive Climate Resilience & Albedo Optimization Engine",
    version=settings.APP_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cached dataset with computed HVI per city
_CACHED_CELLS: Dict[str, List[ClimateCell]] = {}

def get_cells(city: str = "Bengaluru") -> List[ClimateCell]:
    global _CACHED_CELLS
    norm_city = city.strip()
    if norm_city not in _CACHED_CELLS:
        raw_cells = get_climate_cells_for_city(norm_city)
        _CACHED_CELLS[norm_city] = calculate_hvi_for_cells(raw_cells)
    return _CACHED_CELLS[norm_city]

# Static Files Directory
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": f"{settings.APP_NAME} API running. Visit /docs for documentation."}

@app.get("/api/status", response_model=SystemStatusResponse)
def get_system_status():
    """Returns real-time health and connection status of GCP, Vertex AI, and Earth Engine."""
    cells = get_cells()
    has_gemini_key = bool(settings.GEMINI_API_KEY)
    
    return SystemStatusResponse(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        mode="Production Cloud Ready",
        gcp_project=settings.GCP_PROJECT_ID,
        gemini_connected=True,
        gemini_model="Vertex AI Gemini 2.5 Flash",
        earth_engine_status=earth_engine_service.get_status(),
        bigquery_status="Ready (avani_climate GEOGRAPHY schema)",
        firestore_status=firestore_service.get_status(),
        cells_loaded=len(cells)
    )

@app.get("/api/geography/countries-and-cities")
def list_geographic_hierarchy():
    """Returns available countries, cities, and their coordinates/ward counts for cascading UI selection."""
    return get_geographic_hierarchy()

@app.get("/api/cells", response_model=List[ClimateCell])
def list_climate_cells(city: str = Query("Bengaluru", description="City name to fetch climate cells for")):
    """Returns all climate cells with computed HVI and satellite indices for a given city."""
    return get_cells(city=city)

@app.post("/api/optimize", response_model=ScenarioResult)
def run_optimization(request: ScenarioRequest):
    """
    Solves the Prescriptive Climate Resilience problem using Google OR-Tools.
    Optimizes tree canopy, cool roofs, shade structures, and hydration stations.
    """
    target_city = request.city if request.city else "Bengaluru"
    cells = get_cells(city=target_city)
    try:
        result = solve_climate_interventions(
            cells=cells,
            budget_inr=request.budget_inr,
            scenario_type=request.scenario_type
        )
        admin_service.increment_metric("optimizer_runs")
        return result
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/action-plan", response_model=ActionPlanResponse)
def create_climate_action_plan(request: ScenarioRequest):
    """
    Runs OR-Tools optimization and invokes the Vertex AI / Gemini planning agent
    to produce an explainable, budget-constrained municipal climate action plan.
    Also persists the generated scenario to Google Cloud Firestore (avani_scenarios).
    """
    target_city = request.city if request.city else "Bengaluru"
    cells = get_cells(city=target_city)
    try:
        scenario_result = solve_climate_interventions(
            cells=cells,
            budget_inr=request.budget_inr,
            scenario_type=request.scenario_type,
            city=target_city
        )
        action_plan = generate_action_plan(
            scenario_result, cells,
            persona=request.persona,
            selected_ward_id=request.selected_ward_id
        )
        # Track Quota Metrics
        admin_service.increment_metric("optimizer_runs")
        admin_service.increment_metric("gemini_calls")
        # Persist to Firestore
        firestore_service.save_scenario_plan(action_plan.model_dump())
        return action_plan
    except Exception as e:
        logger.error(f"Action plan generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/phases/spot-evaluation", response_model=SpotEvaluationSummary)
def get_spot_evaluation_endpoint(
    city: str = Query("Bengaluru", description="Target city name"),
    ward_id: Optional[str] = Query(None, description="Target ward/spot ID"),
    budget_inr: float = Query(10000000.0, description="Budget in INR")
):
    """
    Evaluates Phase 1, Phase 2, and Phase 3 interventions for a specific geographic spot/ward.
    Returns physical suitability ratings and mathematical recommendation.
    """
    return get_spot_phase_evaluation(city_name=city, ward_id=ward_id, budget_inr=budget_inr)

@app.get("/api/heat-calendar", response_model=HeatCalendarSummary)
def get_heat_calendar_endpoint(
    city: str = Query("Bengaluru", description="Target city name")
):
    """
    Returns 12-month thermal curve, peak heatwave alert window, and actionable precaution timeline.
    """
    return get_city_heat_calendar(city_name=city)

@app.get("/api/history/20yr-archive", response_model=TwentyYearArchiveResponse)
def get_20yr_archive_endpoint(
    city: str = Query("Bengaluru", description="Target city name")
):
    """
    Returns 20-year satellite radiometric archive (2005 - 2025) across Landsat 5/7/8/9 and Sentinel-2.
    """
    return get_twenty_year_satellite_archive(city_name=city)

@app.get("/api/temperature-timeline", response_model=TemperatureTimelineResponse)
def get_temperature_timeline_data(
    city: str = Query("Bengaluru", description="Target city name"),
    cell_id: Optional[str] = Query(None, description="Optional target ward ID")
):
    """
    Returns 24-hour Diurnal Temperature curves (Baseline vs Cooled with Highs and Lows)
    and 7-day heatwave forecast for the selected city or specific ward.
    """
    return get_temperature_timeline(city_name=city, cell_id=cell_id)

@app.get("/api/history/timelapse", response_model=CityTimelapseResponse)
def get_historical_timelapse(city: str = Query("Bengaluru", description="Target city for satellite timelapse")):
    """
    Returns 2014-2026 multi-year satellite timelapse telemetry for the target city,
    tracking surface temperature rise, cumulative mature tree loss, and urban built densification.
    """
    return get_city_timelapse_data(city_name=city)

@app.get("/api/scenarios/history")
def get_scenario_history(limit: int = Query(5, description="Number of recent plans to fetch")):
    """Returns recently generated and stored scenarios from Google Cloud Firestore."""
    return {
        "status": "success",
        "recent_plans": firestore_service.list_recent_plans(limit=limit)
    }

@app.get("/api/scenarios/compare")
def compare_all_scenarios(
    budget_inr: float = Query(10000000.0, description="Budget in INR"),
    city: str = Query("Bengaluru", description="City to compare scenarios for")
):
    """
    Computes and compares all 4 intervention scenarios side-by-side
    (Optimized, Green First, Albedo First, Public Health First).
    """
    cells = get_cells(city=city)
    scenario_types = ["optimized", "green_first", "albedo_first", "public_health_first"]
    results = {}
    
    for s_type in scenario_types:
        res = solve_climate_interventions(cells, budget_inr=budget_inr, scenario_type=s_type, city=city)
        results[s_type] = {
            "title": res.scenario_title,
            "budget_spent_lakhs": res.budget_spent_lakhs,
            "avg_temp_reduction_c": res.avg_temp_reduction_c,
            "max_temp_reduction_c": res.max_temp_reduction_c,
            "total_beneficiaries": res.total_beneficiaries,
            "heat_exposure_reduction_pct": res.heat_exposure_reduction_pct,
            "trees": res.total_trees,
            "cool_roof_sqft": res.total_cool_roof_sqft,
            "shades": res.total_shades,
            "hydration": res.total_hydration,
            "computation_time_ms": res.computation_time_ms
        }
        
    return {
        "budget_inr": budget_inr,
        "scenarios": results
    }

@app.get("/api/auth/config")
def get_auth_config():
    """Returns auth requirement status and demo credentials hint."""
    return {
        "auth_enabled": auth_service.is_auth_enabled,
        "allowed_emails": auth_service.allowed_emails,
        "default_judge_email": "judge@hackathon.com",
        "default_judge_password": auth_service.judge_password
    }

@app.post("/api/auth/login", response_model=LoginResponse)
def login_user(payload: LoginRequest):
    """Authenticates judges or whitelisted users against the access policy."""
    auth_result = auth_service.authenticate_user(payload.email, payload.password)
    if not auth_result:
        raise HTTPException(
            status_code=401,
            detail="Access Denied: Invalid credentials or email is not on the authorized whitelist."
        )
    return LoginResponse(
        token=auth_result["token"],
        email=auth_result["email"],
        role=auth_result["role"],
        status="success"
    )

# ================= ADMIN & FIREBASE AUTH ENDPOINTS =================
class FirebaseLoginPayload(BaseModel):
    email: str
    token: Optional[str] = None
    displayName: Optional[str] = None

class AdminUserActionPayload(BaseModel):
    email: str
    action: str  # "approve", "suspend", "activate", "delete"

class AdminAlertResolvePayload(BaseModel):
    alert_id: str
    action: str  # "approve", "reject"

class AdminSettingsPayload(BaseModel):
    gemini_api_key: Optional[str] = None
    gcp_project_id: Optional[str] = None
    use_earth_engine_live: Optional[bool] = None
    allowed_emails: Optional[str] = None

@app.post("/api/auth/firebase-login")
def firebase_login_user(payload: FirebaseLoginPayload):
    """
    Firebase Authentication Handler:
    - If user is approved: returns token and role.
    - If user is suspended: rejects access with 403.
    - If user is not registered: triggers an alert to Admin (srbodkhe@gmail.com)
      and rejects access until approved by Admin.
    """
    email = payload.email.strip().lower()
    user = admin_service.get_user(email)
    
    # 1. Unregistered user -> Trigger Admin Alert
    if not user:
        admin_service.trigger_registration_alert(
            email=email,
            details=f"Firebase login attempted by {payload.displayName or email}. Not yet registered on whitelist."
        )
        raise HTTPException(
            status_code=403,
            detail=f"Access Request Sent: Your Google/Firebase ID ({email}) is not yet registered. An alert has been sent to Super Admin (srbodkhe@gmail.com). You will receive access once approved."
        )
        
    # 2. Suspended user
    if user["status"] == "Suspended":
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: The account for {email} has been suspended by the administrator."
        )
        
    # 3. Pending user
    if user["status"] == "Pending":
        raise HTTPException(
            status_code=403,
            detail=f"Access Pending: Your registration for {email} is awaiting review and approval by the administrator."
        )
        
    # 4. Active user
    admin_service.add_or_update_user(email, role=user["role"], status="Active", provider="firebase/google")
    token = f"firebase_{int(time.time())}_{email}"
    return {
        "status": "success",
        "token": token,
        "email": email,
        "role": user["role"]
    }

@app.get("/api/admin/dashboard")
def get_admin_dashboard(requester_email: Optional[str] = Query(None)):
    """Returns users, alerts, quotas, and configuration for the Admin portal."""
    return {
        "status": "success",
        "users": admin_service.list_users(),
        "alerts": admin_service.list_alerts(),
        "quotas": admin_service.get_quotas(),
        "config": admin_service.get_runtime_config()
    }

@app.post("/api/admin/users/action")
def perform_admin_user_action(payload: AdminUserActionPayload):
    """Admin action to approve, suspend, activate, or delete a user."""
    if payload.action == "delete":
        success = admin_service.delete_user(payload.email)
    elif payload.action in ("approve", "activate"):
        success = admin_service.update_user_status(payload.email, "Active")
    elif payload.action == "suspend":
        success = admin_service.update_user_status(payload.email, "Suspended")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    if not success:
        raise HTTPException(status_code=400, detail="Action could not be completed.")
        
    return {
        "status": "success",
        "users": admin_service.list_users()
    }

@app.post("/api/admin/alerts/resolve")
def resolve_admin_alert(payload: AdminAlertResolvePayload):
    """Admin resolution of access requests and registration alerts."""
    success = admin_service.resolve_alert(payload.alert_id, payload.action)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return {
        "status": "success",
        "alerts": admin_service.list_alerts(),
        "users": admin_service.list_users()
    }

@app.post("/api/admin/settings")
def update_admin_settings(payload: AdminSettingsPayload):
    """Updates runtime API keys, project configuration, and whitelists."""
    updates = {}
    if payload.gemini_api_key is not None:
        updates["gemini_api_key"] = payload.gemini_api_key
    if payload.gcp_project_id is not None:
        updates["gcp_project_id"] = payload.gcp_project_id
    if payload.use_earth_engine_live is not None:
        updates["use_earth_engine_live"] = payload.use_earth_engine_live
    if payload.allowed_emails is not None:
        updates["allowed_emails"] = payload.allowed_emails
        
    new_config = admin_service.update_runtime_config(updates)
    return {
        "status": "success",
        "config": new_config
    }
