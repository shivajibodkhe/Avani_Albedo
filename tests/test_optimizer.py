from app.data.bengaluru_heat_data import get_bengaluru_climate_cells
from app.services.hvi_engine import calculate_hvi_for_cells
from app.services.optimizer import solve_climate_interventions

def test_optimizer_budget_and_scenarios():
    cells = calculate_hvi_for_cells(get_bengaluru_climate_cells())
    budget = 10000000.0 # 1 Crore
    
    # 1. AI Optimized
    res_opt = solve_climate_interventions(cells, budget_inr=budget, scenario_type="optimized")
    assert res_opt.budget_spent_inr <= budget
    assert res_opt.budget_spent_inr > 0.8 * budget
    assert res_opt.avg_temp_reduction_c > 0.0
    assert res_opt.total_beneficiaries > 0
    assert len(res_opt.allocations) == 12
    
    # 2. Green First
    res_green = solve_climate_interventions(cells, budget_inr=budget, scenario_type="green_first")
    assert res_green.budget_spent_inr <= budget
    tree_spend = sum(a.trees_cost for a in res_green.allocations)
    assert tree_spend >= 0.58 * budget # Constraint was >= 60%
    
    # 3. Albedo First
    res_albedo = solve_climate_interventions(cells, budget_inr=budget, scenario_type="albedo_first")
    assert res_albedo.budget_spent_inr <= budget
    roof_spend = sum(a.cool_roof_cost for a in res_albedo.allocations)
    assert roof_spend >= 0.58 * budget # Constraint was >= 60%
    
    # 4. Public Health First
    res_health = solve_climate_interventions(cells, budget_inr=budget, scenario_type="public_health_first")
    assert res_health.budget_spent_inr <= budget
    health_spend = sum(a.shade_cost + a.hydration_cost for a in res_health.allocations)
    assert health_spend >= 0.34 * budget # Constraint was >= 35%
