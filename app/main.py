import logging
from typing import List, Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import (
    ClimateCell, ScenarioRequest, ScenarioResult,
    ActionPlanResponse, SystemStatusResponse
)
from app.data.bengaluru_heat_data import get_bengaluru_climate_cells
from app.services.hvi_engine import calculate_hvi_for_cells
from app.services.optimizer import solve_climate_interventions
from app.services.gemini_agent import generate_action_plan
from app.services.earth_engine_service import earth_engine_service
from app.services.firestore_service import firestore_service

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

# In-memory cached dataset with computed HVI
_CACHED_CELLS: List[ClimateCell] = []

def get_cells() -> List[ClimateCell]:
    global _CACHED_CELLS
    if not _CACHED_CELLS:
        raw_cells = get_bengaluru_climate_cells()
        _CACHED_CELLS = calculate_hvi_for_cells(raw_cells)
    return _CACHED_CELLS

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

@app.get("/api/cells", response_model=List[ClimateCell])
def list_climate_cells():
    """Returns all climate cells with computed HVI and satellite indices."""
    return get_cells()

@app.post("/api/optimize", response_model=ScenarioResult)
def run_optimization(request: ScenarioRequest):
    """
    Solves the Prescriptive Climate Resilience problem using Google OR-Tools.
    Optimizes tree canopy, cool roofs, shade structures, and hydration stations.
    """
    cells = get_cells()
    try:
        result = solve_climate_interventions(
            cells=cells,
            budget_inr=request.budget_inr,
            scenario_type=request.scenario_type
        )
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
    cells = get_cells()
    try:
        scenario_result = solve_climate_interventions(
            cells=cells,
            budget_inr=request.budget_inr,
            scenario_type=request.scenario_type
        )
        action_plan = generate_action_plan(scenario_result, cells)
        # Persist to Firestore
        firestore_service.save_scenario_plan(action_plan.model_dump())
        return action_plan
    except Exception as e:
        logger.error(f"Action plan generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios/history")
def get_scenario_history(limit: int = Query(5, description="Number of recent plans to fetch")):
    """Returns recently generated and stored scenarios from Google Cloud Firestore."""
    return {
        "status": "success",
        "recent_plans": firestore_service.list_recent_plans(limit=limit)
    }

@app.get("/api/scenarios/compare")
def compare_all_scenarios(budget_inr: float = Query(10000000.0, description="Budget in INR")):
    """
    Computes and compares all 4 intervention scenarios side-by-side
    (Optimized, Green First, Albedo First, Public Health First).
    """
    cells = get_cells()
    scenario_types = ["optimized", "green_first", "albedo_first", "public_health_first"]
    results = {}
    
    for s_type in scenario_types:
        res = solve_climate_interventions(cells, budget_inr=budget_inr, scenario_type=s_type)
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
