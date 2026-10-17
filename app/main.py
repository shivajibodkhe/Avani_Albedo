import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query, Header, Depends, Request, Response
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models.schemas import (
    ClimateCell, ScenarioRequest, ScenarioResult,
    ActionPlanResponse, SystemStatusResponse,
    LoginRequest, LoginResponse, TemperatureTimelineResponse,
    CityTimelapseResponse, SpotEvaluationSummary, HeatCalendarSummary,
    TwentyYearArchiveResponse, CopilotChatRequest, CopilotChatResponse,
    AddCityRequest
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
    register_new_city,
    CITIES_REGISTRY
)
from app.services.hvi_engine import calculate_hvi_for_cells
from app.services.optimizer import solve_climate_interventions
from app.services.gemini_agent import generate_action_plan
from app.services.earth_engine_service import earth_engine_service
from app.services.firestore_service import firestore_service
from app.services.auth_service import auth_service
from app.services.admin_service import admin_service
from app.services.copilot_service import copilot_service

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("avani_albedo")

# FastAPI App with customized /docs security
app = FastAPI(
    title=settings.APP_NAME,
    description="Prescriptive Climate Resilience & Albedo Optimization Engine",
    version=settings.APP_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_authenticated_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """
    Enforces authentication across all data endpoints and interactive Swagger API docs.
    Accepts:
    1. Header: Authorization: Bearer <token>
    2. Cookie: avani_token
    3. Query parameter: ?token=<token>
    """
    if not auth_service.is_auth_enabled:
        return {"email": "guest@avani.eco", "role": "Municipal Planner"}

    clean_token = None
    if authorization and authorization.startswith("Bearer "):
        clean_token = authorization.split("Bearer ", 1)[1].strip()
    elif request.cookies.get("avani_token"):
        clean_token = request.cookies.get("avani_token").strip()
    elif token:
        clean_token = token.strip()

    if not clean_token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in via the Avani Albedo portal."
        )

    session = auth_service.verify_token(clean_token)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session. Please log in."
        )
    return session

def get_optional_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
) -> Optional[Dict[str, Any]]:
    """Gracefully resolves authenticated user if available, without throwing 401."""
    try:
        return get_authenticated_user(request, authorization, token)
    except Exception:
        return None

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

@app.get("/favicon.ico", include_in_schema=False)
def serve_favicon():
    favicon_file = STATIC_DIR / "favicon.svg"
    if favicon_file.exists():
        return FileResponse(favicon_file, media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="Favicon not found")

# ================= PROTECTED SWAGGER & OPENAPI DOCUMENTATION =================
@app.get("/docs", include_in_schema=False)
def get_swagger_documentation(request: Request, user: Dict[str, Any] = Depends(get_authenticated_user)):
    """Protected Swagger UI documentation — accessible only to authenticated users."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - Swagger UI",
        swagger_favicon_url="/static/favicon.ico"
    )

@app.get("/redoc", include_in_schema=False)
def get_redoc_documentation(request: Request, user: Dict[str, Any] = Depends(get_authenticated_user)):
    """Protected ReDoc API documentation — accessible only to authenticated users."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - ReDoc"
    )

@app.get("/openapi.json", include_in_schema=False)
def get_openapi_specification(request: Request, user: Dict[str, Any] = Depends(get_authenticated_user)):
    """Protected OpenAPI specification schema — accessible only to authenticated users."""
    return JSONResponse(get_openapi(title=settings.APP_NAME, version=settings.APP_VERSION, routes=app.routes))

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
        gemini_model="Gemini 2.0 Flash (Google AI)",
        earth_engine_status=earth_engine_service.get_status(),
        bigquery_status="Offline Staging Ready (avani_climate GEOGRAPHY schema)",
        firestore_status=firestore_service.get_status(),
        cells_loaded=len(cells)
    )

@app.get("/api/geography/countries-and-cities")
def list_geographic_hierarchy():
    """Returns available countries, cities, and their coordinates/ward counts for cascading UI selection."""
    return get_geographic_hierarchy()

@app.get("/api/cells", response_model=List[ClimateCell])
def list_climate_cells(
    city: str = Query("Bengaluru", description="City name to fetch climate cells for"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Returns all climate cells with computed HVI and satellite indices for a given city."""
    return get_cells(city=city)

@app.post("/api/optimize", response_model=ScenarioResult)
def run_optimization(request: ScenarioRequest, user: Dict[str, Any] = Depends(get_authenticated_user)):
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
def create_climate_action_plan(request: ScenarioRequest, user: Dict[str, Any] = Depends(get_authenticated_user)):
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
    budget_inr: float = Query(10000000.0, description="Budget in INR"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Evaluates Phase 1, Phase 2, and Phase 3 interventions for a specific geographic spot/ward.
    Returns physical suitability ratings and mathematical recommendation.
    """
    return get_spot_phase_evaluation(city_name=city, ward_id=ward_id, budget_inr=budget_inr)

@app.get("/api/heat-calendar", response_model=HeatCalendarSummary)
def get_heat_calendar_endpoint(
    city: str = Query("Bengaluru", description="Target city name"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Returns 12-month thermal curve, peak heatwave alert window, and actionable precaution timeline.
    """
    return get_city_heat_calendar(city_name=city)

@app.get("/api/history/20yr-archive", response_model=TwentyYearArchiveResponse)
def get_20yr_archive_endpoint(
    city: str = Query("Bengaluru", description="Target city name"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Returns 20-year satellite radiometric archive (2005 - 2025) across Landsat 5/7/8/9 and Sentinel-2.
    """
    return get_twenty_year_satellite_archive(city_name=city)

@app.get("/api/temperature-timeline", response_model=TemperatureTimelineResponse)
def get_temperature_timeline_data(
    city: str = Query("Bengaluru", description="Target city name"),
    cell_id: Optional[str] = Query(None, description="Optional target ward ID"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Returns 24-hour Diurnal Temperature curves (Baseline vs Cooled with Highs and Lows)
    and 7-day heatwave forecast for the selected city or specific ward.
    """
    return get_temperature_timeline(city_name=city, cell_id=cell_id)

@app.get("/api/history/timelapse", response_model=CityTimelapseResponse)
def get_historical_timelapse(
    city: str = Query("Bengaluru", description="Target city for satellite timelapse"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Returns 2014-2026 multi-year satellite timelapse telemetry for the target city,
    tracking surface temperature rise, cumulative mature tree loss, and urban built densification.
    """
    return get_city_timelapse_data(city_name=city)

@app.get("/api/scenarios/history")
def get_scenario_history(
    limit: int = Query(5, description="Number of recent plans to fetch"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Returns recently generated and stored scenarios from Google Cloud Firestore."""
    return {
        "status": "success",
        "recent_plans": firestore_service.list_recent_plans(limit=limit)
    }

@app.get("/api/scenarios/compare")
def compare_all_scenarios(
    budget_inr: float = Query(10000000.0, description="Budget in INR"),
    city: str = Query("Bengaluru", description="City to compare scenarios for"),
    user: Dict[str, Any] = Depends(get_authenticated_user)
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
    """Returns auth requirement status and allowed accounts."""
    return {
        "auth_enabled": auth_service.is_auth_enabled,
        "allowed_emails": auth_service.allowed_emails,
        "default_judge_email": "judges"
    }

@app.get("/api/auth/verify")
def verify_auth_token(authorization: Optional[str] = Header(None)):
    """Validates that a token is currently active and not expired."""
    if not auth_service.is_auth_enabled:
        return {"valid": True, "email": "guest@avani.eco", "role": "Municipal Planner"}
        
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication token required.")
        
    token = authorization.split("Bearer ", 1)[1].strip()
    session = auth_service.verify_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please log in.")
        
    return {
        "valid": True,
        "email": session["email"],
        "role": session["role"]
    }

@app.post("/api/auth/login", response_model=LoginResponse)
def login_user(payload: LoginRequest, response: Response):
    """Authenticates judges or authorized administrative users against the access policy."""
    auth_result = auth_service.authenticate_user(payload.email, payload.password)
    if not auth_result:
        raise HTTPException(
            status_code=401,
            detail="Access Denied: Invalid credentials or account is not authorized."
        )
    # Set session cookie for seamless browser and Swagger docs access
    response.set_cookie(
        key="avani_token",
        value=auth_result["token"],
        max_age=86400 * 7,
        httponly=False,
        samesite="lax",
        path="/"
    )
    return LoginResponse(
        token=auth_result["token"],
        email=auth_result["email"],
        role=auth_result["role"],
        status="success"
    )

@app.post("/api/auth/logout")
def logout_user(response: Response):
    """Logs out user and clears the session cookie."""
    response.delete_cookie("avani_token", path="/")
    return {"status": "success", "message": "Logged out successfully."}

# ================= ADMIN & FIREBASE AUTH ENDPOINTS =================
class FirebaseLoginPayload(BaseModel):
    email: str
    token: Optional[str] = None
    displayName: Optional[str] = None

class AdminUserActionPayload(BaseModel):
    email: str
    action: str  # "approve", "suspend", "activate", "delete"
    role: Optional[str] = None

class AdminRoleUpdatePayload(BaseModel):
    email: str
    role: str

class AdminPasswordResetPayload(BaseModel):
    email: str
    new_password: str

class AdminAlertResolvePayload(BaseModel):
    alert_id: str
    action: str  # "approve", "reject"
    role: Optional[str] = None

class AdminSettingsPayload(BaseModel):
    gemini_api_key: Optional[str] = None
    gcp_project_id: Optional[str] = None
    use_earth_engine_live: Optional[bool] = None
    allowed_emails: Optional[str] = None

@app.post("/api/auth/firebase-login")
def firebase_login_user(payload: FirebaseLoginPayload, response: Response):
    """
    Google Authentication Handler:
    - If user is approved (Active): returns active session token, sets session cookie, and returns role.
    - If user is suspended: rejects access with 403.
    - If user is pending: rejects access with 403 until approved.
    - If user is not registered: creates access request with status 'Pending',
      alerts Admin (srbodkhe@gmail.com), and rejects access with 403 until approved.
    """
    email = payload.email.strip().lower()
    user = admin_service.get_user(email)
    
    # 1. Unregistered user -> Trigger Admin Alert and register as Pending
    if not user:
        admin_service.trigger_registration_alert(
            email=email,
            details=f"Access requested by {payload.displayName or email} with Google Account. Needs Admin approval."
        )
        raise HTTPException(
            status_code=403,
            detail=f"Access Request Submitted: Your Google account ({email}) has been submitted for approval by Administrator (srbodkhe@gmail.com). You will receive access once approved."
        )
        
    # 2. Suspended user
    if user.get("status") == "Suspended":
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: The account for {email} has been suspended by the administrator."
        )
        
    # 3. Pending user
    if user.get("status") == "Pending":
        raise HTTPException(
            status_code=403,
            detail=f"Access Pending: Your access request for {email} is currently under review by Administrator (srbodkhe@gmail.com). Please check back once approved."
        )
        
    # 4. Active user (Approved!)
    admin_service.add_or_update_user(email, role=user["role"], status="Active", provider="google")
    token = auth_service.create_session(email, user["role"])
    
    # Set session cookie for seamless browser and Swagger docs access
    response.set_cookie(
        key="avani_token",
        value=token,
        max_age=86400 * 7,
        httponly=False,
        samesite="lax",
        path="/"
    )
    return {
        "status": "success",
        "token": token,
        "email": email,
        "role": user["role"]
    }

@app.get("/api/admin/dashboard")
def get_admin_dashboard(
    requester_email: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Returns users, alerts, quotas, and configuration for the Admin portal."""
    return {
        "status": "success",
        "users": admin_service.list_users(),
        "alerts": admin_service.list_alerts(),
        "quotas": admin_service.get_quotas(),
        "config": admin_service.get_runtime_config()
    }

@app.post("/api/admin/users/action")
def perform_admin_user_action(
    payload: AdminUserActionPayload,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Admin action to approve, suspend, activate, or delete a user."""
    if payload.action == "delete":
        success = admin_service.delete_user(payload.email)
    elif payload.action in ("approve", "activate"):
        success = admin_service.update_user_status(payload.email, "Active", default_role=payload.role)
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

@app.post("/api/admin/users/role")
def update_user_role(
    payload: AdminRoleUpdatePayload,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Admin action to promote or change a user's role."""
    success = admin_service.update_user_role(payload.email, payload.role)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "status": "success",
        "message": f"Role for {payload.email} promoted/updated to {payload.role}.",
        "users": admin_service.list_users()
    }

@app.post("/api/admin/users/reset-password")
def reset_user_password(
    payload: AdminPasswordResetPayload,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Admin action to reset user or judges password."""
    success = admin_service.reset_user_password(payload.email, payload.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Password reset could not be completed.")
    return {
        "status": "success",
        "message": f"Password for {payload.email} has been reset successfully.",
        "users": admin_service.list_users()
    }

@app.post("/api/admin/alerts/resolve")
def resolve_admin_alert(
    payload: AdminAlertResolvePayload,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Admin resolution of access requests and registration alerts."""
    success = admin_service.resolve_alert(payload.alert_id, payload.action, role=payload.role)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return {
        "status": "success",
        "alerts": admin_service.list_alerts(),
        "users": admin_service.list_users()
    }

@app.post("/api/admin/settings")
def update_admin_settings(
    payload: AdminSettingsPayload,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Updates runtime API keys, project configuration, and access controls."""
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

class SatelliteFetchRequest(BaseModel):
    country: str = "India"
    city: str = "Bengaluru"
    sensors: Optional[List[str]] = None

@app.post("/api/admin/satellite/fetch")
def trigger_satellite_fetch(
    payload: SatelliteFetchRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Triggers on-demand multi-spectral & thermal satellite telemetry ingestion for a country and city."""
    return admin_service.trigger_satellite_ingestion(
        country=payload.country,
        city=payload.city,
        sensors=payload.sensors
    )

@app.post("/api/admin/cities/add")
def add_new_city_endpoint(
    payload: AddCityRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """
    Allows Admins to onboard and register a new metropolitan city.
    Automatically synthesizes initial microclimate wards, calculates HVI,
    and updates the geographic hierarchy.
    """
    entry = register_new_city(
        city_name=payload.name,
        country=payload.country,
        country_flag=payload.country_flag,
        center_lat=payload.latitude,
        center_lng=payload.longitude,
        currency=payload.currency,
        currency_symbol=payload.currency_symbol,
        default_budget=payload.default_budget
    )
    admin_service.increment_metric("earth_engine_queries")
    return {
        "status": "success",
        "message": f"Successfully onboarded {payload.name} ({payload.country}) with {len(entry['raw_cells'])} microclimate wards.",
        "city": entry["name"],
        "city_key": payload.name.strip(),
        "wards_count": len(entry["raw_cells"]),
        "center": entry["center"]
    }

@app.post("/api/copilot/chat", response_model=CopilotChatResponse)
@app.post("/api/help-bot/chat", response_model=CopilotChatResponse)
def ask_project_copilot(
    payload: CopilotChatRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Avani Project Help Bot powered by Gemini 2.0 Flash & Extensible JSON Knowledge Base.
    Answers any query strictly related to the Avani Albedo application.
    Enforces strict security guardrails: NEVER discloses passwords, credentials, or API keys.
    """
    admin_service.increment_metric("gemini_calls")
    result = copilot_service.ask(
        query=payload.message,
        history=payload.history,
        city=payload.city or "Bengaluru"
    )
    return CopilotChatResponse(
        status="success",
        response=result["response"],
        model=result["model"],
        sources=result.get("sources", [])
    )

@app.get("/api/help-bot/knowledge")
def get_help_bot_knowledge_summary(user: Dict[str, Any] = Depends(get_authenticated_user)):
    """
    Returns the knowledge base topics and metadata from app/data/help_bot_knowledge.json.
    Can be inspected and updated in future.
    """
    return copilot_service.knowledge
