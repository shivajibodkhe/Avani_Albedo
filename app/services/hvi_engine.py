from typing import List
from app.models.schemas import ClimateCell

def normalize(val: float, min_val: float, max_val: float) -> float:
    """Normalizes a value to a 0-100 scale, clamped."""
    if max_val <= min_val:
        return 50.0
    norm = ((val - min_val) / (max_val - min_val)) * 100.0
    return max(0.0, min(100.0, norm))

def calculate_hvi_for_cells(cells: List[ClimateCell]) -> List[ClimateCell]:
    """
    Computes the Heat Vulnerability Index (HVI) according to the Blueprint formula:
    
    HVI = 
      0.30 * Heat Severity
    + 0.20 * Vegetation Deficit
    + 0.15 * Population Exposure
    + 0.15 * Critical Infrastructure Exposure
    + 0.10 * Built Density
    + 0.10 * Historical Heat Persistence
    
    Categories:
      0-30: Low
      30-50: Moderate
      50-70: High
      70-85: Severe
      85-100: Critical
    """
    if not cells:
        return []
    
    min_lst = min(c.lst for c in cells)
    max_lst = max(c.lst for c in cells)
    
    min_pop = min(c.population for c in cells)
    max_pop = max(c.population for c in cells)
    
    # Calculate asset vulnerability score for each cell:
    # Hospitals carry 3x weight, Schools 2x, Transit 1.5x
    def asset_score(c: ClimateCell) -> float:
        return (c.assets.hospitals * 3.0) + (c.assets.schools * 2.0) + (c.assets.transit_stops * 1.5)
    
    asset_scores = [asset_score(c) for c in cells]
    min_assets = min(asset_scores)
    max_assets = max(asset_scores)
    
    min_heat_days = min(c.heat_persistence_days for c in cells)
    max_heat_days = max(c.heat_persistence_days for c in cells)
    
    for c in cells:
        # 1. Heat Severity (0-100)
        heat_severity = normalize(c.lst, min_lst, max_lst)
        
        # 2. Vegetation Deficit (lower NDVI = higher deficit)
        veg_deficit = max(0.0, min(100.0, (1.0 - c.ndvi) * 100.0))
        
        # 3. Population Exposure (0-100)
        pop_exposure = normalize(c.population, min_pop, max_pop)
        
        # 4. Critical Infrastructure Exposure (0-100)
        infra_exposure = normalize(asset_score(c), min_assets, max_assets)
        
        # 5. Built Density (0-100)
        built_density_score = max(0.0, min(100.0, c.built_density * 100.0))
        
        # 6. Historical Heat Persistence (0-100)
        heat_persistence_score = normalize(c.heat_persistence_days, min_heat_days, max_heat_days)
        
        # Composite HVI
        hvi = (
            0.30 * heat_severity +
            0.20 * veg_deficit +
            0.15 * pop_exposure +
            0.15 * infra_exposure +
            0.10 * built_density_score +
            0.10 * heat_persistence_score
        )
        
        c.hvi_score = round(hvi, 1)
        
        # Category classification
        if c.hvi_score >= 85.0:
            c.hvi_category = "Critical"
        elif c.hvi_score >= 70.0:
            c.hvi_category = "Severe"
        elif c.hvi_score >= 50.0:
            c.hvi_category = "High"
        elif c.hvi_score >= 30.0:
            c.hvi_category = "Moderate"
        else:
            c.hvi_category = "Low"
            
        # Physical Land Feasibility Validation (Root zone: 16 m² per mature tree)
        unbuilt_ratio = max(0.02, 1.0 - c.built_density)
        # Average ward ground footprint ~ 1,200,000 m² (1.2 km²)
        # Validated permeable fraction of unbuilt space is ~30% (medians, school grounds, park setbacks)
        permeable_sqm = round(1200000.0 * unbuilt_ratio * 0.30, 0)
        c.permeable_land_sqm = permeable_sqm
        # Carrying capacity: strictly 16 m² root space per canopy tree
        capacity = max(100, int(permeable_sqm / 16.0))
        c.tree_carrying_capacity = capacity
        # Cap max_trees by physical carrying capacity
        c.max_trees = min(c.max_trees, capacity)
        
        if c.built_density >= 0.88:
            c.land_feasibility_status = "Constrained Ground Soil (High Built Density)"
            c.land_feasibility_note = f"Ground soil limited to {permeable_sqm:,.0f} m². Soil capped at {capacity:,} trees; excess heat redirected to Cool Roofs (0 m² soil)."
        elif c.built_density >= 0.75:
            c.land_feasibility_status = "Moderate Permeable Margin"
            c.land_feasibility_note = f"Viable capacity for {capacity:,} trees along road medians, institutional campuses & park setbacks."
        else:
            c.land_feasibility_status = "High Soil Availability"
            c.land_feasibility_note = f"Abundant permeable ground ({permeable_sqm:,.0f} m²). Optimal for dense urban micro-forests."
            
    return cells

