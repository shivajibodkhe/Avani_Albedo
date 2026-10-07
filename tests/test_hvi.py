from app.data.bengaluru_heat_data import get_bengaluru_climate_cells
from app.services.hvi_engine import calculate_hvi_for_cells

def test_hvi_calculation_and_categories():
    cells = get_bengaluru_climate_cells()
    assert len(cells) == 12
    
    calculated = calculate_hvi_for_cells(cells)
    assert len(calculated) == 12
    
    for c in calculated:
        # Score must be between 0 and 100
        assert 0.0 <= c.hvi_score <= 100.0
        # Category must be valid
        assert c.hvi_category in ["Low", "Moderate", "High", "Severe", "Critical"]
        
    # Peenya and KR Market have high LST and low vegetation, so their HVI should be High or Severe/Critical
    peenya = next(c for c in calculated if c.cell_id == "BLR_001")
    kr_market = next(c for c in calculated if c.cell_id == "BLR_002")
    jayanagar = next(c for c in calculated if c.cell_id == "BLR_011")
    
    assert peenya.hvi_score > jayanagar.hvi_score
    assert kr_market.hvi_score > jayanagar.hvi_score
