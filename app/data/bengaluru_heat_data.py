from typing import List
from app.models.schemas import ClimateCell, CriticalAssets

# High-fidelity Landsat 8/9 & Sentinel-2 composite dataset for Bengaluru climate cells
RAW_CELLS_DATA = [
    {
        "cell_id": "BLR_001",
        "name": "Peenya Industrial Area",
        "zone": "West",
        "center_lat": 13.0298,
        "center_lng": 77.5255,
        "boundary": [
            [13.0450, 77.5100],
            [13.0450, 77.5400],
            [13.0150, 77.5400],
            [13.0150, 77.5100]
        ],
        "lst": 42.8,  # Peak Land Surface Temp in Celsius
        "ndvi": 0.08, # Extremely low vegetation
        "ndbi": 0.45, # High built-up index
        "albedo": 0.14,# Dark tar / corrugated sheet roofs
        "heat_anomaly": +5.4,
        "population": 125000,
        "assets": {"schools": 14, "hospitals": 6, "transit_stops": 28},
        "built_density": 0.88,
        "heat_persistence_days": 68,
        "max_trees": 1500,
        "max_cool_roof_sqft": 450000,
        "max_shades": 30,
        "max_hydration": 20
    },
    {
        "cell_id": "BLR_002",
        "name": "KR Market & Chickpet",
        "zone": "South-Central",
        "center_lat": 12.9644,
        "center_lng": 77.5768,
        "boundary": [
            [12.9740, 77.5680],
            [12.9740, 77.5850],
            [12.9550, 77.5850],
            [12.9550, 77.5680]
        ],
        "lst": 41.6,
        "ndvi": 0.06,
        "ndbi": 0.52,
        "albedo": 0.16,
        "heat_anomaly": +4.2,
        "population": 168000,
        "assets": {"schools": 18, "hospitals": 9, "transit_stops": 34},
        "built_density": 0.94,
        "heat_persistence_days": 72,
        "max_trees": 600, # Dense, fewer plantable spaces
        "max_cool_roof_sqft": 320000,
        "max_shades": 25,
        "max_hydration": 25
    },
    {
        "cell_id": "BLR_003",
        "name": "Shivajinagar & Commercial St",
        "zone": "Central",
        "center_lat": 12.9856,
        "center_lng": 77.6057,
        "boundary": [
            [12.9950, 77.5970],
            [12.9950, 77.6150],
            [12.9760, 77.6150],
            [12.9760, 77.5970]
        ],
        "lst": 40.5,
        "ndvi": 0.11,
        "ndbi": 0.44,
        "albedo": 0.18,
        "heat_anomaly": +3.1,
        "population": 142000,
        "assets": {"schools": 22, "hospitals": 8, "transit_stops": 26},
        "built_density": 0.89,
        "heat_persistence_days": 58,
        "max_trees": 900,
        "max_cool_roof_sqft": 280000,
        "max_shades": 20,
        "max_hydration": 18
    },
    {
        "cell_id": "BLR_004",
        "name": "Whitefield Export Zone",
        "zone": "East",
        "center_lat": 12.9698,
        "center_lng": 77.7499,
        "boundary": [
            [12.9850, 77.7350],
            [12.9850, 77.7650],
            [12.9550, 77.7650],
            [12.9550, 77.7350]
        ],
        "lst": 39.8,
        "ndvi": 0.16,
        "ndbi": 0.38,
        "albedo": 0.22,
        "heat_anomaly": +2.4,
        "population": 195000,
        "assets": {"schools": 16, "hospitals": 7, "transit_stops": 22},
        "built_density": 0.76,
        "heat_persistence_days": 50,
        "max_trees": 2200,
        "max_cool_roof_sqft": 600000,
        "max_shades": 24,
        "max_hydration": 16
    },
    {
        "cell_id": "BLR_005",
        "name": "Electronic City Ph 1",
        "zone": "South-East",
        "center_lat": 12.8452,
        "center_lng": 77.6602,
        "boundary": [
            [12.8600, 77.6450],
            [12.8600, 77.6750],
            [12.8300, 77.6750],
            [12.8300, 77.6450]
        ],
        "lst": 40.2,
        "ndvi": 0.18,
        "ndbi": 0.39,
        "albedo": 0.20,
        "heat_anomaly": +2.8,
        "population": 110000,
        "assets": {"schools": 11, "hospitals": 5, "transit_stops": 19},
        "built_density": 0.72,
        "heat_persistence_days": 52,
        "max_trees": 1800,
        "max_cool_roof_sqft": 520000,
        "max_shades": 18,
        "max_hydration": 14
    },
    {
        "cell_id": "BLR_006",
        "name": "Majestic Kempegowda Interchange",
        "zone": "Central",
        "center_lat": 12.9767,
        "center_lng": 77.5713,
        "boundary": [
            [12.9860, 77.5620],
            [12.9860, 77.5800],
            [12.9670, 77.5800],
            [12.9670, 77.5620]
        ],
        "lst": 42.1,
        "ndvi": 0.05,
        "ndbi": 0.54,
        "albedo": 0.15,
        "heat_anomaly": +4.7,
        "population": 138000,
        "assets": {"schools": 12, "hospitals": 11, "transit_stops": 46},
        "built_density": 0.93,
        "heat_persistence_days": 70,
        "max_trees": 700,
        "max_cool_roof_sqft": 300000,
        "max_shades": 32,
        "max_hydration": 28
    },
    {
        "cell_id": "BLR_007",
        "name": "Yeshwanthpur Rail & APMC",
        "zone": "North-West",
        "center_lat": 13.0238,
        "center_lng": 77.5502,
        "boundary": [
            [13.0350, 77.5400],
            [13.0350, 77.5600],
            [13.0120, 77.5600],
            [13.0120, 77.5400]
        ],
        "lst": 41.2,
        "ndvi": 0.09,
        "ndbi": 0.48,
        "albedo": 0.17,
        "heat_anomaly": +3.8,
        "population": 115000,
        "assets": {"schools": 15, "hospitals": 7, "transit_stops": 25},
        "built_density": 0.86,
        "heat_persistence_days": 60,
        "max_trees": 1100,
        "max_cool_roof_sqft": 380000,
        "max_shades": 22,
        "max_hydration": 18
    },
    {
        "cell_id": "BLR_008",
        "name": "Hebbal Flyover Junction",
        "zone": "North",
        "center_lat": 13.0358,
        "center_lng": 77.5970,
        "boundary": [
            [13.0500, 77.5850],
            [13.0500, 77.6100],
            [13.0220, 77.6100],
            [13.0220, 77.5850]
        ],
        "lst": 39.4,
        "ndvi": 0.22,
        "ndbi": 0.35,
        "albedo": 0.20,
        "heat_anomaly": +2.0,
        "population": 98000,
        "assets": {"schools": 14, "hospitals": 4, "transit_stops": 20},
        "built_density": 0.68,
        "heat_persistence_days": 44,
        "max_trees": 2400,
        "max_cool_roof_sqft": 250000,
        "max_shades": 16,
        "max_hydration": 12
    },
    {
        "cell_id": "BLR_009",
        "name": "Koramangala Commercial",
        "zone": "South-East",
        "center_lat": 12.9352,
        "center_lng": 77.6245,
        "boundary": [
            [12.9480, 77.6120],
            [12.9480, 77.6370],
            [12.9220, 77.6370],
            [12.9220, 77.6120]
        ],
        "lst": 38.6,
        "ndvi": 0.24,
        "ndbi": 0.33,
        "albedo": 0.21,
        "heat_anomaly": +1.2,
        "population": 145000,
        "assets": {"schools": 19, "hospitals": 8, "transit_stops": 21},
        "built_density": 0.74,
        "heat_persistence_days": 38,
        "max_trees": 1600,
        "max_cool_roof_sqft": 340000,
        "max_shades": 14,
        "max_hydration": 12
    },
    {
        "cell_id": "BLR_010",
        "name": "Indiranagar 100ft Corridor",
        "zone": "East",
        "center_lat": 12.9719,
        "center_lng": 77.6412,
        "boundary": [
            [12.9830, 77.6300],
            [12.9830, 77.6520],
            [12.9600, 77.6520],
            [12.9600, 77.6300]
        ],
        "lst": 38.2,
        "ndvi": 0.26,
        "ndbi": 0.31,
        "albedo": 0.23,
        "heat_anomaly": +0.8,
        "population": 118000,
        "assets": {"schools": 17, "hospitals": 6, "transit_stops": 18},
        "built_density": 0.70,
        "heat_persistence_days": 34,
        "max_trees": 1500,
        "max_cool_roof_sqft": 260000,
        "max_shades": 12,
        "max_hydration": 10
    },
    {
        "cell_id": "BLR_011",
        "name": "Jayanagar 4th Block",
        "zone": "South",
        "center_lat": 12.9299,
        "center_lng": 77.5826,
        "boundary": [
            [12.9420, 77.5720],
            [12.9420, 77.5930],
            [12.9180, 77.5930],
            [12.9180, 77.5720]
        ],
        "lst": 36.8,
        "ndvi": 0.38, # High urban tree canopy
        "ndbi": 0.22,
        "albedo": 0.25,
        "heat_anomaly": -0.6,
        "population": 132000,
        "assets": {"schools": 24, "hospitals": 10, "transit_stops": 20},
        "built_density": 0.65,
        "heat_persistence_days": 22,
        "max_trees": 900,
        "max_cool_roof_sqft": 220000,
        "max_shades": 10,
        "max_hydration": 8
    },
    {
        "cell_id": "BLR_012",
        "name": "Malleshwaram Heritage Hub",
        "zone": "North-Central",
        "center_lat": 13.0031,
        "center_lng": 77.5685,
        "boundary": [
            [13.0150, 77.5580],
            [13.0150, 77.5790],
            [12.9910, 77.5790],
            [12.9910, 77.5580]
        ],
        "lst": 37.4,
        "ndvi": 0.33,
        "ndbi": 0.27,
        "albedo": 0.24,
        "heat_anomaly": +0.0,
        "population": 122000,
        "assets": {"schools": 26, "hospitals": 9, "transit_stops": 22},
        "built_density": 0.72,
        "heat_persistence_days": 28,
        "max_trees": 1000,
        "max_cool_roof_sqft": 240000,
        "max_shades": 12,
        "max_hydration": 10
    }
]

def get_bengaluru_climate_cells() -> List[ClimateCell]:
    """Returns the list of instantiated ClimateCell objects."""
    cells = []
    for item in RAW_CELLS_DATA:
        assets = CriticalAssets(**item["assets"])
        cell = ClimateCell(
            cell_id=item["cell_id"],
            name=item["name"],
            zone=item["zone"],
            center_lat=item["center_lat"],
            center_lng=item["center_lng"],
            boundary=item["boundary"],
            lst=item["lst"],
            ndvi=item["ndvi"],
            ndbi=item["ndbi"],
            albedo=item["albedo"],
            heat_anomaly=item["heat_anomaly"],
            population=item["population"],
            assets=assets,
            built_density=item["built_density"],
            heat_persistence_days=item["heat_persistence_days"],
            max_trees=item["max_trees"],
            max_cool_roof_sqft=item["max_cool_roof_sqft"],
            max_shades=item["max_shades"],
            max_hydration=item["max_hydration"]
        )
        cells.append(cell)
    return cells
