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
    
    # Physical intervention headroom & Land Feasibility
    max_trees: int = 1000
    max_cool_roof_sqft: int = 250000
    max_shades: int = 25
    max_hydration: int = 15
    permeable_land_sqm: float = 25000.0
    tree_carrying_capacity: int = 1500
    land_feasibility_status: str = "Verified Viable"
    land_feasibility_note: str = "Validated road medians, park peripheries & schoolyards"

class YearlyTimelapseRecord(BaseModel):
    year: int
    avg_lst_c: float
    heat_anomaly_c: float
    trees_lost_cumulative: int
    ndvi: float
    built_up_fraction: float
    hvi_score: float
    hvi_category: str
    satellite_sensor: str
    observation_date: str

class CityTimelapseResponse(BaseModel):
    city: str
    available_years: List[int]
    total_trees_lost_decade: int
    total_temp_rise_c: float
    records: List[YearlyTimelapseRecord]
    restoration_target_trees: int
    restoration_cool_roof_sqft: int

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
    persona: str = Field(
        default="Municipal Commissioner",
        description="Decision-maker persona: 'Municipal Commissioner', 'Public Health Officer', 'Urban Planner', 'Disaster Management Head'"
    )
    selected_ward_id: Optional[str] = Field(
        default=None,
        description="Optional specific ward ID for high-precision localized intervention"
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

class PhaseSpotEvaluation(BaseModel):
    phase_id: str
    phase_title: str
    timeline: str
    focus_interventions: List[str]
    cooling_impact_c: float
    land_requirement: str
    speed: str
    suitability_score_pct: int
    suitability_rating: str
    is_recommended_best: bool
    rationale: str

class SpotEvaluationSummary(BaseModel):
    ward_id: str
    ward_name: str
    city: str
    built_density_pct: int
    unbuilt_pct: int
    peak_lst: float
    hvi_score: float
    recommended_phase_id: str
    recommended_phase_name: str
    why_recommended: str
    phases: List[PhaseSpotEvaluation]

class HeatwaveMonthRisk(BaseModel):
    month: str
    month_num: int
    high_lst: float
    status: str
    action_note: str

class HeatCalendarSummary(BaseModel):
    city: str
    country: str
    peak_heatwave_window: str
    precaution_prep_window: str
    planting_window: str
    emergency_threshold_c: float
    months: List[HeatwaveMonthRisk] = []
    advisories: List[str] = []

class TwentyYearRecord(BaseModel):
    year: int
    avg_lst_c: float
    heat_anomaly_c: float
    trees_lost_cumulative: int
    ndvi: float
    built_up_fraction: float
    satellite_sensor: str
    observation_date: str

class TwentyYearArchiveResponse(BaseModel):
    city: str
    archive_span: str = "2005 - 2025 (20 Years)"
    total_temp_rise_c: float
    total_trees_lost_20yr: int
    built_up_surge_pct: float
    records: List[TwentyYearRecord]
    data_availability_summary: str

class ActionPlanResponse(BaseModel):
    scenario_result: ScenarioResult
    executive_summary: str
    rationale: str
    persona: str = "Municipal Commissioner"
    strategic_recommendations: List[str] = []
    land_feasibility_summary: str = "Physical land validation complete. In high-density wards (>85% concrete), tree capacity is strictly bounded to open schoolyards, road medians and park setbacks. Excess cooling demand is safely routed to high-albedo rooftop interventions requiring zero ground soil."
    ward_priorities: List[WardPriority]
    implementation_phases: List[ImplementationPhase]
    co_benefits: List[str]
    llm_model: str
    is_live_llm: bool
    spot_phase_evaluation: Optional[SpotEvaluationSummary] = None
    heat_calendar: Optional[HeatCalendarSummary] = None
    status: str = "success"

class DayForecast(BaseModel):
    day: str
    date: str
    high_c: float
    low_c: float
    mitigated_high_c: float
    alert_level: str

class TemperatureModeInfo(BaseModel):
    name: str
    mode_id: str
    source: str
    measures: str
    typical_example: str
    sensor_platform: Optional[str] = None
    typical_temp_c: Optional[float] = None

class TemperatureTimelineResponse(BaseModel):
    city: str
    ward_id: Optional[str] = None
    ward_name: Optional[str] = None
    current_lst_c: float
    peak_high_c: float
    peak_time: str
    low_temp_c: float
    low_time: str
    heat_hazard_duration_hours: float
    cooling_delta_c: float
    diurnal_hours: List[str]
    baseline_temp_c: List[float]
    cooled_temp_c: List[float]
    forecast_7days: List[DayForecast]
    air_temp_high_c: Optional[float] = None
    air_temp_low_c: Optional[float] = None
    air_temp_cooled_c: Optional[float] = None
    air_baseline_temp_c: Optional[List[float]] = None
    air_cooled_temp_c: Optional[List[float]] = None
    lst_vs_air_delta_c: Optional[float] = None
    season_note: Optional[str] = "Peak Summer Heatwave Baseline (April/May) vs 2m Ambient Air Temp"
    surface_mode: Optional[TemperatureModeInfo] = None
    ambient_mode: Optional[TemperatureModeInfo] = None

class SystemStatusResponse(BaseModel):
    app_name: str
    version: str
    mode: str
    gcp_project: str
    gemini_connected: bool
    gemini_model: str
    earth_engine_status: str
    bigquery_status: str
    firestore_status: str = "Ready (avani_scenarios)"
    cells_loaded: int

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    email: str
    role: str
    status: str = "success"

class CopilotChatRequest(BaseModel):
    message: str
    city: Optional[str] = "Bengaluru"
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class CopilotChatResponse(BaseModel):
    status: str = "success"
    response: str
    model: str
    sources: List[str] = Field(default_factory=list)

