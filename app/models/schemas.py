from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CriticalAssets(BaseModel):
    schools: int = Field(default=0, description="Number of schools and colleges")
    hospitals: int = Field(default=0, description="Hospitals, clinics, primary health centers")
    transit_stops: int = Field(default=0, description="Metro stations and bus terminals")

class ClimateCell(BaseModel):
    cell_id: str
    name: str
    zone: str
    center_lat: float
    center_lng: float
    boundary: List[List[float]] = Field(default_factory=list, description="Polygon [lat, lng] coordinates")
    lst: float = Field(..., description="Land Surface Temperature in Celsius")
    ndvi: float = Field(..., description="Normalized Difference Vegetation Index (0 to 1)")
    ndbi: float = Field(..., description="Normalized Difference Built-up Index (-1 to 1)")
    albedo: float = Field(..., description="Surface solar reflectance (0 to 1)")
    heat_anomaly: float = Field(..., description="Degrees above city average")
    population: int = Field(..., description="Total estimated residents")
    assets: CriticalAssets
    built_density: float = Field(..., description="Built density fraction (0 to 1)")
    heat_persistence_days: int = Field(..., description="Days per year exceeding 38C")
    
    # Calculated properties
    hvi_score: float = 0.0
    hvi_category: str = "Moderate"
    
    # Physical intervention headroom
    max_trees: int = 1000
    max_cool_roof_sqft: int = 250000
    max_shades: int = 25
    max_hydration: int = 15

class InterventionAllocation(BaseModel):
    cell_id: str
    cell_name: str
    trees: int = 0
    trees_cost: float = 0.0
    cool_roof_sqft: int = 0
    cool_roof_cost: float = 0.0
    shade_structures: int = 0
    shade_cost: float = 0.0
    hydration_stations: int = 0
    hydration_cost: float = 0.0
    total_cost: float = 0.0
    cooling_reduction_c: float = 0.0
    beneficiaries: int = 0
    hvi_score: float = 0.0
    hvi_category: str = "Moderate"

class ScenarioRequest(BaseModel):
    city: str = "Bengaluru"
    budget_inr: float = Field(default=10000000.0, description="Budget in INR (Default 1 Crore = 10,000,000)")
    scenario_type: str = Field(
        default="optimized",
        description="One of: 'optimized', 'green_first', 'albedo_first', 'public_health_first'"
    )
    custom_weights: Optional[Dict[str, float]] = None

class ScenarioResult(BaseModel):
    scenario_type: str
    scenario_title: str
    city: str
    total_budget_inr: float
    budget_spent_inr: float
    budget_remaining_inr: float
    budget_spent_lakhs: float
    avg_temp_reduction_c: float
    max_temp_reduction_c: float
    total_beneficiaries: int
    heat_exposure_reduction_pct: float
    total_trees: int
    total_cool_roof_sqft: int
    total_shades: int
    total_hydration: int
    allocations: List[InterventionAllocation]
    solver_status: str
    computation_time_ms: float

class WardPriority(BaseModel):
    rank: int
    cell_id: str
    cell_name: str
    hvi_score: float
    primary_interventions: List[str]
    justification: str

class ImplementationPhase(BaseModel):
    phase: str
    timeline: str
    key_milestones: List[str]
    estimated_spend_inr: float

class ActionPlanResponse(BaseModel):
    scenario_result: ScenarioResult
    executive_summary: str
    rationale: str
    ward_priorities: List[WardPriority]
    implementation_phases: List[ImplementationPhase]
    co_benefits: List[str]
    llm_model: str
    is_live_llm: bool
    status: str = "success"

class SystemStatusResponse(BaseModel):
    app_name: str
    version: str
    mode: str
    gcp_project: str
    gemini_connected: bool
    gemini_model: str
    earth_engine_status: str
    bigquery_status: str
    cells_loaded: int
