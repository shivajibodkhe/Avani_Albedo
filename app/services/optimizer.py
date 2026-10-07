import time
from typing import List, Dict, Any, Tuple
from ortools.linear_solver import pywraplp
from app.models.schemas import ClimateCell, InterventionAllocation, ScenarioResult

# Unit Costs in INR
COST_PER_TREE = 3000.0          # Sapling, planting, 24-month survival maintenance
COST_PER_ROOF_SQFT = 45.0       # High-albedo elastomeric coating per sq ft
ROOF_UNIT_SQFT = 1000           # Optimize in blocks of 1,000 sq ft (₹45,000 / block)
COST_PER_ROOF_UNIT = COST_PER_ROOF_SQFT * ROOF_UNIT_SQFT
COST_PER_SHADE = 120000.0       # Solar-reflective tensile shade canopy at bus stops / schools
COST_PER_HYDRATION = 80000.0    # UV-purified, solar-chilled public drinking station

# Cooling Potential Constants (Estimated degrees C localized surface cooling)
COOLING_PER_TREE = 0.0009        # 1000 trees ~ 0.9 C
COOLING_PER_ROOF_SQFT = 0.000007 # 100,000 sq ft ~ 0.7 C
COOLING_PER_SHADE = 0.022        # Micro-climate shade cooling
COOLING_PER_HYDRATION = 0.005    # Thermal relief index proxy

def solve_climate_interventions(
    cells: List[ClimateCell],
    budget_inr: float = 10000000.0,
    scenario_type: str = "optimized"
) -> ScenarioResult:
    """
    Solves the Prescriptive Climate Resilience Mixed-Integer Linear Program using Google OR-Tools SCIP solver.
    """
    start_time = time.time()
    
    # Create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        # Fallback to CBC
        solver = pywraplp.Solver.CreateSolver("CBC")
    if not solver:
        raise RuntimeError("Neither SCIP nor CBC solver available in OR-Tools environment.")

    num_cells = len(cells)
    
    # Decision variables for each cell
    trees_var = []
    roof_units_var = []
    shades_var = []
    hydrations_var = []
    
    for c in cells:
        # Max bounds
        t_var = solver.IntVar(0, c.max_trees, f"trees_{c.cell_id}")
        r_var = solver.IntVar(0, c.max_cool_roof_sqft // ROOF_UNIT_SQFT, f"roof_{c.cell_id}")
        s_var = solver.IntVar(0, c.max_shades, f"shades_{c.cell_id}")
        h_var = solver.IntVar(0, c.max_hydration, f"hydration_{c.cell_id}")
        
        trees_var.append(t_var)
        roof_units_var.append(r_var)
        shades_var.append(s_var)
        hydrations_var.append(h_var)
        
    # Total Cost Expression
    total_cost_expr = solver.Sum([
        (trees_var[i] * COST_PER_TREE) +
        (roof_units_var[i] * COST_PER_ROOF_UNIT) +
        (shades_var[i] * COST_PER_SHADE) +
        (hydrations_var[i] * COST_PER_HYDRATION)
        for i in range(num_cells)
    ])
    
    # Primary Budget Constraint: Total Cost <= Budget
    solver.Add(total_cost_expr <= budget_inr)
    
    # Scenario Specific Constraints
    if scenario_type == "green_first":
        # At least 60% of budget allocated to trees
        tree_spend = solver.Sum([trees_var[i] * COST_PER_TREE for i in range(num_cells)])
        solver.Add(tree_spend >= 0.60 * budget_inr)
        
    elif scenario_type == "albedo_first":
        # At least 60% of budget allocated to cool roofs
        roof_spend = solver.Sum([roof_units_var[i] * COST_PER_ROOF_UNIT for i in range(num_cells)])
        solver.Add(roof_spend >= 0.60 * budget_inr)
        
    elif scenario_type == "public_health_first":
        # At least 35% allocated to shade structures & hydration stations
        health_spend = solver.Sum([
            (shades_var[i] * COST_PER_SHADE) + (hydrations_var[i] * COST_PER_HYDRATION)
            for i in range(num_cells)
        ])
        solver.Add(health_spend >= 0.35 * budget_inr)
        
    # Multi-Objective Function:
    # Maximize: Sum over cells of [
    #   (Cooling Benefit * Pop Weight * HVI Weight * Infra Weight)
    # ]
    objective = solver.Objective()
    
    for i, c in enumerate(cells):
        # Base multipliers
        hvi_weight = (c.hvi_score / 50.0) ** 1.5  # Higher HVI gets non-linear priority
        pop_weight = (c.population / 100000.0)
        infra_weight = 1.0 + (c.assets.schools * 0.05) + (c.assets.hospitals * 0.10)
        
        if scenario_type == "public_health_first":
            # Boost priority near schools and hospitals by 2x
            infra_weight *= 2.0
            
        cell_impact_factor = hvi_weight * pop_weight * infra_weight
        
        # Tree term
        tree_coef = (COOLING_PER_TREE * 10000.0) * cell_impact_factor
        if scenario_type == "green_first":
            tree_coef *= 1.8
            
        # Roof term (per 1,000 sq ft block)
        roof_coef = (COOLING_PER_ROOF_SQFT * ROOF_UNIT_SQFT * 10000.0) * cell_impact_factor
        if scenario_type == "albedo_first":
            roof_coef *= 1.8
            
        # Shade term
        shade_coef = (COOLING_PER_SHADE * 10000.0) * cell_impact_factor
        if scenario_type == "public_health_first":
            shade_coef *= 2.5
            
        # Hydration term
        hyd_coef = (COOLING_PER_HYDRATION * 10000.0) * cell_impact_factor
        if scenario_type == "public_health_first":
            hyd_coef *= 3.0
            
        objective.SetCoefficient(trees_var[i], tree_coef)
        objective.SetCoefficient(roof_units_var[i], roof_coef)
        objective.SetCoefficient(shades_var[i], shade_coef)
        objective.SetCoefficient(hydrations_var[i], hyd_coef)
        
    objective.SetMaximization()
    
    # Solve
    solver_status_code = solver.Solve()
    status_str = "OPTIMAL" if solver_status_code == pywraplp.Solver.OPTIMAL else "FEASIBLE"
    
    # Collect Allocations
    allocations: List[InterventionAllocation] = []
    total_spent = 0.0
    total_trees = 0
    total_roof_sqft = 0
    total_shades = 0
    total_hydration = 0
    cooling_reductions = []
    cell_beneficiaries = []
    
    for i, c in enumerate(cells):
        t_val = int(trees_var[i].solution_value())
        r_units = int(roof_units_var[i].solution_value())
        r_sqft = r_units * ROOF_UNIT_SQFT
        s_val = int(shades_var[i].solution_value())
        h_val = int(hydrations_var[i].solution_value())
        
        t_cost = t_val * COST_PER_TREE
        r_cost = r_units * COST_PER_ROOF_UNIT
        s_cost = s_val * COST_PER_SHADE
        h_cost = h_val * COST_PER_HYDRATION
        cell_total_cost = t_cost + r_cost + s_cost + h_cost
        
        # Localized cooling benefit
        cooling_c = round(
            (t_val * COOLING_PER_TREE) +
            (r_sqft * COOLING_PER_ROOF_SQFT) +
            (s_val * COOLING_PER_SHADE) +
            (h_val * COOLING_PER_HYDRATION),
            2
        )
        
        # Beneficiaries calculation: proportion of population in cooled zone
        # plus pedestrians served by hydration and shade
        coverage_ratio = min(1.0, (t_cost + r_cost) / (1500 * COST_PER_TREE + 200000 * COST_PER_ROOF_SQFT + 1))
        residents_protected = int(c.population * 0.4 * coverage_ratio)
        commuters_protected = (s_val * 1800) + (h_val * 2400)
        beneficiaries = residents_protected + commuters_protected
        
        alloc = InterventionAllocation(
            cell_id=c.cell_id,
            cell_name=c.name,
            trees=t_val,
            trees_cost=t_cost,
            cool_roof_sqft=r_sqft,
            cool_roof_cost=r_cost,
            shade_structures=s_val,
            shade_cost=s_cost,
            hydration_stations=h_val,
            hydration_cost=h_cost,
            total_cost=cell_total_cost,
            cooling_reduction_c=cooling_c,
            beneficiaries=beneficiaries,
            hvi_score=c.hvi_score,
            hvi_category=c.hvi_category
        )
        
        allocations.append(alloc)
        total_spent += cell_total_cost
        total_trees += t_val
        total_roof_sqft += r_sqft
        total_shades += s_val
        total_hydration += h_val
        cooling_reductions.append(cooling_c)
        cell_beneficiaries.append(beneficiaries)
        
    calc_time_ms = round((time.time() - start_time) * 1000.0, 1)
    avg_cooling = round(sum(cooling_reductions) / max(1, len(cooling_reductions)), 2)
    max_cooling = round(max(cooling_reductions) if cooling_reductions else 0.0, 2)
    total_ben = sum(cell_beneficiaries)
    
    # Heat exposure reduction percentage: weighted by HVI
    heat_exp_reduct = round(min(48.5, (avg_cooling / 2.5) * 45.0 + (total_spent / budget_inr) * 3.5), 1)
    
    titles = {
        "optimized": "AI Pareto-Optimized Multi-Intervention Plan",
        "green_first": "Green First: Urban Forest & Tree Canopy Focus",
        "albedo_first": "Albedo First: Cool Roof & Reflectance Retrofit",
        "public_health_first": "Public Health First: High-Vulnerability Corridor Priority"
    }
    
    return ScenarioResult(
        scenario_type=scenario_type,
        scenario_title=titles.get(scenario_type, "Custom Climate Intervention Plan"),
        city="Bengaluru",
        total_budget_inr=budget_inr,
        budget_spent_inr=round(total_spent, 2),
        budget_remaining_inr=round(max(0.0, budget_inr - total_spent), 2),
        budget_spent_lakhs=round(total_spent / 100000.0, 2),
        avg_temp_reduction_c=avg_cooling,
        max_temp_reduction_c=max_cooling,
        total_beneficiaries=total_ben,
        heat_exposure_reduction_pct=heat_exp_reduct,
        total_trees=total_trees,
        total_cool_roof_sqft=total_roof_sqft,
        total_shades=total_shades,
        total_hydration=total_hydration,
        allocations=allocations,
        solver_status=status_str,
        computation_time_ms=calc_time_ms
    )
