import copy
from typing import List, Dict, Any, Optional
from app.models.schemas import ClimateCell, CriticalAssets
from app.data.bengaluru_heat_data import RAW_CELLS_DATA as BENGALURU_CELLS_DATA

# ================= MUMBAI DATASET =================
MUMBAI_CELLS_DATA = [
    {
        "cell_id": "BOM_001",
        "name": "Dharavi High-Density Belt",
        "zone": "Central",
        "center_lat": 19.0400,
        "center_lng": 72.8550,
        "boundary": [
            [19.0480, 72.8450], [19.0480, 72.8650],
            [19.0320, 72.8650], [19.0320, 72.8450]
        ],
        "lst": 43.5, "ndvi": 0.04, "ndbi": 0.58, "albedo": 0.12, "heat_anomaly": +5.8,
        "population": 220000,
        "assets": {"schools": 22, "hospitals": 12, "transit_stops": 36},
        "built_density": 0.96, "heat_persistence_days": 75,
        "max_trees": 500, "max_cool_roof_sqft": 400000, "max_shades": 30, "max_hydration": 30
    },
    {
        "cell_id": "BOM_002",
        "name": "Bandra-Kurla Complex (BKC)",
        "zone": "Commercial West",
        "center_lat": 19.0657,
        "center_lng": 72.8687,
        "boundary": [
            [19.0750, 72.8580], [19.0750, 72.8790],
            [19.0550, 72.8790], [19.0550, 72.8580]
        ],
        "lst": 41.2, "ndvi": 0.12, "ndbi": 0.49, "albedo": 0.22, "heat_anomaly": +3.5,
        "population": 110000,
        "assets": {"schools": 10, "hospitals": 6, "transit_stops": 28},
        "built_density": 0.85, "heat_persistence_days": 56,
        "max_trees": 1800, "max_cool_roof_sqft": 650000, "max_shades": 25, "max_hydration": 20
    },
    {
        "cell_id": "BOM_003",
        "name": "Andheri East Industrial Hub",
        "zone": "Western Suburbs",
        "center_lat": 19.1136,
        "center_lng": 72.8697,
        "boundary": [
            [19.1240, 72.8580], [19.1240, 72.8820],
            [19.1020, 72.8820], [19.1020, 72.8580]
        ],
        "lst": 42.1, "ndvi": 0.08, "ndbi": 0.52, "albedo": 0.15, "heat_anomaly": +4.4,
        "population": 195000,
        "assets": {"schools": 18, "hospitals": 9, "transit_stops": 34},
        "built_density": 0.91, "heat_persistence_days": 65,
        "max_trees": 1200, "max_cool_roof_sqft": 480000, "max_shades": 28, "max_hydration": 22
    },
    {
        "cell_id": "BOM_004",
        "name": "Dadar Central Interchange",
        "zone": "South-Central",
        "center_lat": 19.0178,
        "center_lng": 72.8478,
        "boundary": [
            [19.0280, 72.8380], [19.0280, 72.8580],
            [19.0070, 72.8580], [19.0070, 72.8380]
        ],
        "lst": 40.8, "ndvi": 0.10, "ndbi": 0.46, "albedo": 0.18, "heat_anomaly": +3.1,
        "population": 165000,
        "assets": {"schools": 24, "hospitals": 11, "transit_stops": 42},
        "built_density": 0.89, "heat_persistence_days": 54,
        "max_trees": 900, "max_cool_roof_sqft": 350000, "max_shades": 32, "max_hydration": 25
    },
    {
        "cell_id": "BOM_005",
        "name": "Kurla West Transit Corridor",
        "zone": "Central Suburbs",
        "center_lat": 19.0680,
        "center_lng": 72.8790,
        "boundary": [
            [19.0780, 72.8700], [19.0780, 72.8900],
            [19.0580, 72.8900], [19.0580, 72.8700]
        ],
        "lst": 41.8, "ndvi": 0.07, "ndbi": 0.50, "albedo": 0.16, "heat_anomaly": +4.1,
        "population": 180000,
        "assets": {"schools": 16, "hospitals": 8, "transit_stops": 30},
        "built_density": 0.90, "heat_persistence_days": 62,
        "max_trees": 1100, "max_cool_roof_sqft": 420000, "max_shades": 24, "max_hydration": 20
    },
    {
        "cell_id": "BOM_006",
        "name": "Colaba & Fort Historic Precinct",
        "zone": "South Mumbai",
        "center_lat": 18.9220,
        "center_lng": 72.8340,
        "boundary": [
            [18.9350, 72.8250], [18.9350, 72.8450],
            [18.9100, 72.8450], [18.9100, 72.8250]
        ],
        "lst": 37.8, "ndvi": 0.22, "ndbi": 0.38, "albedo": 0.24, "heat_anomaly": +0.1,
        "population": 120000,
        "assets": {"schools": 19, "hospitals": 7, "transit_stops": 22},
        "built_density": 0.78, "heat_persistence_days": 32,
        "max_trees": 1400, "max_cool_roof_sqft": 300000, "max_shades": 16, "max_hydration": 14
    }
]

# ================= DELHI NCR DATASET =================
DELHI_CELLS_DATA = [
    {
        "cell_id": "DEL_001",
        "name": "Chandni Chowk & Old Delhi",
        "zone": "Central-North",
        "center_lat": 28.6562,
        "center_lng": 77.2300,
        "boundary": [
            [28.6670, 77.2200], [28.6670, 77.2420],
            [28.6450, 77.2420], [28.6450, 77.2200]
        ],
        "lst": 44.8, "ndvi": 0.05, "ndbi": 0.62, "albedo": 0.13, "heat_anomaly": +6.4,
        "population": 210000,
        "assets": {"schools": 25, "hospitals": 14, "transit_stops": 40},
        "built_density": 0.97, "heat_persistence_days": 84,
        "max_trees": 600, "max_cool_roof_sqft": 380000, "max_shades": 35, "max_hydration": 30
    },
    {
        "cell_id": "DEL_002",
        "name": "Okhla Industrial Estate",
        "zone": "South-East",
        "center_lat": 28.5355,
        "center_lng": 77.2732,
        "boundary": [
            [28.5480, 77.2600], [28.5480, 77.2880],
            [28.5220, 77.2880], [28.5220, 77.2600]
        ],
        "lst": 45.2, "ndvi": 0.07, "ndbi": 0.59, "albedo": 0.14, "heat_anomaly": +6.8,
        "population": 145000,
        "assets": {"schools": 14, "hospitals": 7, "transit_stops": 26},
        "built_density": 0.92, "heat_persistence_days": 82,
        "max_trees": 1400, "max_cool_roof_sqft": 600000, "max_shades": 30, "max_hydration": 24
    },
    {
        "cell_id": "DEL_003",
        "name": "Anand Vihar Transit Choke Point",
        "zone": "East",
        "center_lat": 28.6469,
        "center_lng": 77.3160,
        "boundary": [
            [28.6580, 77.3050], [28.6580, 77.3280],
            [28.6350, 77.3280], [28.6350, 77.3050]
        ],
        "lst": 43.9, "ndvi": 0.09, "ndbi": 0.54, "albedo": 0.15, "heat_anomaly": +5.5,
        "population": 175000,
        "assets": {"schools": 18, "hospitals": 8, "transit_stops": 38},
        "built_density": 0.88, "heat_persistence_days": 76,
        "max_trees": 1500, "max_cool_roof_sqft": 420000, "max_shades": 28, "max_hydration": 25
    },
    {
        "cell_id": "DEL_004",
        "name": "Connaught Place & Barakhamba",
        "zone": "Central",
        "center_lat": 28.6315,
        "center_lng": 77.2167,
        "boundary": [
            [28.6420, 77.2060], [28.6420, 77.2280],
            [28.6200, 77.2280], [28.6200, 77.2060]
        ],
        "lst": 41.5, "ndvi": 0.18, "ndbi": 0.45, "albedo": 0.22, "heat_anomaly": +3.1,
        "population": 95000,
        "assets": {"schools": 15, "hospitals": 9, "transit_stops": 32},
        "built_density": 0.82, "heat_persistence_days": 60,
        "max_trees": 2000, "max_cool_roof_sqft": 450000, "max_shades": 24, "max_hydration": 20
    },
    {
        "cell_id": "DEL_005",
        "name": "Rohini Sector 10 Dense Belt",
        "zone": "North-West",
        "center_lat": 28.7150,
        "center_lng": 77.1120,
        "boundary": [
            [28.7280, 77.1000], [28.7280, 77.1250],
            [28.7020, 77.1250], [28.7020, 77.1000]
        ],
        "lst": 43.1, "ndvi": 0.12, "ndbi": 0.48, "albedo": 0.18, "heat_anomaly": +4.7,
        "population": 190000,
        "assets": {"schools": 28, "hospitals": 10, "transit_stops": 26},
        "built_density": 0.86, "heat_persistence_days": 70,
        "max_trees": 1800, "max_cool_roof_sqft": 520000, "max_shades": 22, "max_hydration": 18
    },
    {
        "cell_id": "DEL_006",
        "name": "Chanakyapuri Green Belt",
        "zone": "South-Central",
        "center_lat": 28.5980,
        "center_lng": 77.1850,
        "boundary": [
            [28.6120, 77.1720], [28.6120, 77.1980],
            [28.5850, 77.1980], [28.5850, 77.1720]
        ],
        "lst": 37.2, "ndvi": 0.42, "ndbi": 0.20, "albedo": 0.26, "heat_anomaly": -1.2,
        "population": 65000,
        "assets": {"schools": 16, "hospitals": 5, "transit_stops": 16},
        "built_density": 0.45, "heat_persistence_days": 28,
        "max_trees": 1200, "max_cool_roof_sqft": 200000, "max_shades": 10, "max_hydration": 8
    }
]

# ================= HYDERABAD DATASET =================
HYDERABAD_CELLS_DATA = [
    {
        "cell_id": "HYD_001",
        "name": "Charminar & Old City",
        "zone": "South",
        "center_lat": 17.3616,
        "center_lng": 78.4747,
        "boundary": [
            [17.3720, 78.4640], [17.3720, 78.4860],
            [17.3500, 78.4860], [17.3500, 78.4640]
        ],
        "lst": 43.2, "ndvi": 0.06, "ndbi": 0.56, "albedo": 0.14, "heat_anomaly": +5.2,
        "population": 185000,
        "assets": {"schools": 20, "hospitals": 11, "transit_stops": 30},
        "built_density": 0.94, "heat_persistence_days": 74,
        "max_trees": 700, "max_cool_roof_sqft": 360000, "max_shades": 28, "max_hydration": 26
    },
    {
        "cell_id": "HYD_002",
        "name": "HITEC City IT Corridor",
        "zone": "West",
        "center_lat": 17.4474,
        "center_lng": 78.3762,
        "boundary": [
            [17.4600, 78.3630], [17.4600, 78.3900],
            [17.4350, 78.3900], [17.4350, 78.3630]
        ],
        "lst": 40.8, "ndvi": 0.14, "ndbi": 0.46, "albedo": 0.23, "heat_anomaly": +2.8,
        "population": 140000,
        "assets": {"schools": 12, "hospitals": 7, "transit_stops": 24},
        "built_density": 0.81, "heat_persistence_days": 54,
        "max_trees": 2000, "max_cool_roof_sqft": 620000, "max_shades": 22, "max_hydration": 18
    },
    {
        "cell_id": "HYD_003",
        "name": "Secunderabad Railway Hub",
        "zone": "North",
        "center_lat": 17.4399,
        "center_lng": 78.4983,
        "boundary": [
            [17.4520, 78.4860], [17.4520, 78.5100],
            [17.4270, 78.5100], [17.4270, 78.4860]
        ],
        "lst": 42.4, "ndvi": 0.08, "ndbi": 0.51, "albedo": 0.16, "heat_anomaly": +4.4,
        "population": 160000,
        "assets": {"schools": 17, "hospitals": 9, "transit_stops": 36},
        "built_density": 0.89, "heat_persistence_days": 68,
        "max_trees": 1200, "max_cool_roof_sqft": 410000, "max_shades": 26, "max_hydration": 22
    },
    {
        "cell_id": "HYD_004",
        "name": "Jubilee Hills & KBR Park",
        "zone": "Central-West",
        "center_lat": 17.4319,
        "center_lng": 78.4150,
        "boundary": [
            [17.4450, 78.4020], [17.4450, 78.4280],
            [17.4180, 78.4280], [17.4180, 78.4020]
        ],
        "lst": 37.6, "ndvi": 0.36, "ndbi": 0.25, "albedo": 0.25, "heat_anomaly": -0.4,
        "population": 88000,
        "assets": {"schools": 15, "hospitals": 6, "transit_stops": 16},
        "built_density": 0.58, "heat_persistence_days": 32,
        "max_trees": 1100, "max_cool_roof_sqft": 240000, "max_shades": 12, "max_hydration": 10
    }
]

# ================= GLOBAL: DUBAI (UAE) =================
DUBAI_CELLS_DATA = [
    {
        "cell_id": "DXB_001",
        "name": "Deira Heritage & Souk Corridor",
        "zone": "Creek North",
        "center_lat": 25.2697,
        "center_lng": 55.3095,
        "boundary": [
            [25.2800, 55.2980], [25.2800, 55.3220],
            [25.2580, 55.3220], [25.2580, 55.2980]
        ],
        "lst": 47.8, "ndvi": 0.02, "ndbi": 0.65, "albedo": 0.16, "heat_anomaly": +5.5,
        "population": 195000,
        "assets": {"schools": 14, "hospitals": 8, "transit_stops": 32},
        "built_density": 0.95, "heat_persistence_days": 95,
        "max_trees": 400, "max_cool_roof_sqft": 550000, "max_shades": 38, "max_hydration": 35
    },
    {
        "cell_id": "DXB_002",
        "name": "Al Quoz Industrial Zone",
        "zone": "Central South",
        "center_lat": 25.1380,
        "center_lng": 55.2350,
        "boundary": [
            [25.1500, 55.2200], [25.1500, 55.2500],
            [25.1250, 55.2500], [25.1250, 55.2200]
        ],
        "lst": 48.9, "ndvi": 0.01, "ndbi": 0.68, "albedo": 0.18, "heat_anomaly": +6.6,
        "population": 130000,
        "assets": {"schools": 8, "hospitals": 5, "transit_stops": 22},
        "built_density": 0.92, "heat_persistence_days": 102,
        "max_trees": 800, "max_cool_roof_sqft": 750000, "max_shades": 34, "max_hydration": 30
    },
    {
        "cell_id": "DXB_003",
        "name": "Downtown & Business Bay",
        "zone": "Central Commercial",
        "center_lat": 25.1880,
        "center_lng": 55.2750,
        "boundary": [
            [25.2000, 55.2600], [25.2000, 55.2900],
            [25.1750, 55.2900], [25.1750, 55.2600]
        ],
        "lst": 44.5, "ndvi": 0.09, "ndbi": 0.52, "albedo": 0.28, "heat_anomaly": +2.2,
        "population": 165000,
        "assets": {"schools": 11, "hospitals": 7, "transit_stops": 28},
        "built_density": 0.88, "heat_persistence_days": 78,
        "max_trees": 1600, "max_cool_roof_sqft": 600000, "max_shades": 26, "max_hydration": 24
    }
]

# ================= GLOBAL: PHOENIX (USA) =================
PHOENIX_CELLS_DATA = [
    {
        "cell_id": "PHX_001",
        "name": "Maryvale Residential Heat Pocket",
        "zone": "West Phoenix",
        "center_lat": 33.4950,
        "center_lng": -112.1850,
        "boundary": [
            [33.5100, -112.2050], [33.5100, -112.1650],
            [33.4800, -112.1650], [33.4800, -112.2050]
        ],
        "lst": 46.8, "ndvi": 0.06, "ndbi": 0.55, "albedo": 0.15, "heat_anomaly": +5.2,
        "population": 210000,
        "assets": {"schools": 22, "hospitals": 9, "transit_stops": 34},
        "built_density": 0.88, "heat_persistence_days": 88,
        "max_trees": 2200, "max_cool_roof_sqft": 600000, "max_shades": 35, "max_hydration": 28
    },
    {
        "cell_id": "PHX_002",
        "name": "Downtown Phoenix Urban Core",
        "zone": "Central",
        "center_lat": 33.4484,
        "center_lng": -112.0740,
        "boundary": [
            [33.4600, -112.0900], [33.4600, -112.0580],
            [33.4360, -112.0580], [33.4360, -112.0900]
        ],
        "lst": 45.4, "ndvi": 0.08, "ndbi": 0.51, "albedo": 0.22, "heat_anomaly": +3.8,
        "population": 125000,
        "assets": {"schools": 14, "hospitals": 7, "transit_stops": 30},
        "built_density": 0.86, "heat_persistence_days": 80,
        "max_trees": 1500, "max_cool_roof_sqft": 520000, "max_shades": 28, "max_hydration": 25
    }
]

# ================= MASTER METROPOLITAN REGISTRY =================
CITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Bengaluru": {
        "city_id": "bengaluru",
        "name": "Bengaluru (Karnataka)",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [12.9716, 77.5946],
        "zoom": 11,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 10000000.0, # 1 Crore
        "raw_cells": BENGALURU_CELLS_DATA
    },
    "Mumbai": {
        "city_id": "mumbai",
        "name": "Mumbai (Maharashtra)",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [19.0760, 72.8777],
        "zoom": 11,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 15000000.0, # 1.5 Crore
        "raw_cells": MUMBAI_CELLS_DATA
    },
    "Delhi": {
        "city_id": "delhi",
        "name": "Delhi NCR (Capital Region)",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [28.6139, 77.2090],
        "zoom": 11,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 15000000.0,
        "raw_cells": DELHI_CELLS_DATA
    },
    "Hyderabad": {
        "city_id": "hyderabad",
        "name": "Hyderabad (Telangana)",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [17.3850, 78.4867],
        "zoom": 11,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 10000000.0,
        "raw_cells": HYDERABAD_CELLS_DATA
    },
    "Dubai": {
        "city_id": "dubai",
        "name": "Dubai Urban Corridor",
        "country": "United Arab Emirates",
        "country_flag": "🇦🇪",
        "center": [25.2048, 55.2708],
        "zoom": 11,
        "currency": "AED",
        "currency_symbol": "AED ",
        "default_budget": 20000000.0,
        "raw_cells": DUBAI_CELLS_DATA
    },
    "Phoenix": {
        "city_id": "phoenix",
        "name": "Phoenix Metro (Arizona)",
        "country": "United States",
        "country_flag": "🇺🇸",
        "center": [33.4484, -112.0740],
        "zoom": 11,
        "currency": "USD",
        "currency_symbol": "$",
        "default_budget": 12000000.0,
        "raw_cells": PHOENIX_CELLS_DATA
    }
}

def get_geographic_hierarchy() -> Dict[str, Any]:
    """Returns country -> cities hierarchy for cascading dropdowns."""
    hierarchy = {}
    for city_key, meta in CITIES_REGISTRY.items():
        country = meta["country"]
        if country not in hierarchy:
            hierarchy[country] = {
                "country": country,
                "flag": meta["country_flag"],
                "cities": []
            }
        hierarchy[country]["cities"].append({
            "key": city_key,
            "name": meta["name"],
            "center": meta["center"],
            "zoom": meta["zoom"],
            "currency": meta["currency"],
            "currency_symbol": meta["currency_symbol"]
        })
    return {
        "default_country": "India",
        "default_city": "Bengaluru",
        "countries": list(hierarchy.values())
    }

def get_climate_cells_for_city(city_name: str) -> List[ClimateCell]:
    """Loads and instantiates ClimateCell objects for any registered city."""
    # Normalize lookup
    city_entry = None
    for k, v in CITIES_REGISTRY.items():
        if k.lower() == city_name.strip().lower() or v["city_id"] == city_name.strip().lower():
            city_entry = v
            break
            
    if not city_entry:
        city_entry = CITIES_REGISTRY["Bengaluru"] # Fallback

    raw_data = city_entry["raw_cells"]
    cells = []
    for item in raw_data:
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
            max_trees=item.get("max_trees", 1200),
            max_cool_roof_sqft=item.get("max_cool_roof_sqft", 400000),
            max_shades=item.get("max_shades", 25),
            max_hydration=item.get("max_hydration", 20)
        )
        cells.append(cell)
    return cells
