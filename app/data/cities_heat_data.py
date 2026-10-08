import copy
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.schemas import ClimateCell, CriticalAssets, DayForecast, TemperatureTimelineResponse
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

# ================= PUNE DATASET =================
PUNE_CELLS_DATA = [
    {
        "cell_id": "PUN_001", "name": "Shivajinagar Commercial Core", "zone": "Central",
        "center_lat": 18.5308, "center_lng": 73.8475,
        "boundary": [[18.5390, 73.8390], [18.5390, 73.8560], [18.5220, 73.8560], [18.5220, 73.8390]],
        "lst": 42.4, "ndvi": 0.08, "ndbi": 0.52, "albedo": 0.16, "heat_anomaly": +4.6,
        "population": 180000, "assets": {"schools": 18, "hospitals": 10, "transit_stops": 32},
        "built_density": 0.92, "heat_persistence_days": 65,
        "max_trees": 1200, "max_cool_roof_sqft": 450000, "max_shades": 28, "max_hydration": 24
    },
    {
        "cell_id": "PUN_002", "name": "Hinjawadi Tech & Industrial Zone", "zone": "West Suburbs",
        "center_lat": 18.5913, "center_lng": 73.7389,
        "boundary": [[18.6020, 73.7250], [18.6020, 73.7520], [18.5800, 73.7520], [18.5800, 73.7250]],
        "lst": 41.8, "ndvi": 0.12, "ndbi": 0.49, "albedo": 0.20, "heat_anomaly": +4.0,
        "population": 140000, "assets": {"schools": 8, "hospitals": 5, "transit_stops": 26},
        "built_density": 0.85, "heat_persistence_days": 58,
        "max_trees": 2000, "max_cool_roof_sqft": 600000, "max_shades": 25, "max_hydration": 20
    },
    {
        "cell_id": "PUN_003", "name": "Hadapsar Industrial Corridor", "zone": "East",
        "center_lat": 18.5089, "center_lng": 73.9260,
        "boundary": [[18.5200, 73.9140], [18.5200, 73.9380], [18.4980, 73.9380], [18.4980, 73.9140]],
        "lst": 43.1, "ndvi": 0.06, "ndbi": 0.56, "albedo": 0.14, "heat_anomaly": +5.3,
        "population": 210000, "assets": {"schools": 20, "hospitals": 9, "transit_stops": 35},
        "built_density": 0.94, "heat_persistence_days": 72,
        "max_trees": 900, "max_cool_roof_sqft": 520000, "max_shades": 30, "max_hydration": 26
    },
    {
        "cell_id": "PUN_004", "name": "Kothrud Residential Belt", "zone": "South-West",
        "center_lat": 18.5074, "center_lng": 73.8077,
        "boundary": [[18.5180, 73.7960], [18.5180, 73.8190], [18.4970, 73.8190], [18.4970, 73.7960]],
        "lst": 39.8, "ndvi": 0.16, "ndbi": 0.42, "albedo": 0.19, "heat_anomaly": +2.1,
        "population": 165000, "assets": {"schools": 16, "hospitals": 7, "transit_stops": 22},
        "built_density": 0.82, "heat_persistence_days": 44,
        "max_trees": 1500, "max_cool_roof_sqft": 380000, "max_shades": 18, "max_hydration": 15
    },
    {
        "cell_id": "PUN_005", "name": "Swargate Multi-Modal Transit Hub", "zone": "South Central",
        "center_lat": 18.5018, "center_lng": 73.8580,
        "boundary": [[18.5100, 73.8480], [18.5100, 73.8680], [18.4930, 73.8680], [18.4930, 73.8480]],
        "lst": 42.7, "ndvi": 0.05, "ndbi": 0.58, "albedo": 0.13, "heat_anomaly": +4.9,
        "population": 195000, "assets": {"schools": 14, "hospitals": 8, "transit_stops": 42},
        "built_density": 0.95, "heat_persistence_days": 68,
        "max_trees": 800, "max_cool_roof_sqft": 420000, "max_shades": 32, "max_hydration": 30
    }
]

# ================= CHENNAI DATASET =================
CHENNAI_CELLS_DATA = [
    {
        "cell_id": "MAA_001", "name": "T. Nagar Commercial Chokepoint", "zone": "Central",
        "center_lat": 13.0418, "center_lng": 80.2341,
        "boundary": [[13.0510, 80.2240], [13.0510, 80.2440], [13.0320, 80.2440], [13.0320, 80.2240]],
        "lst": 43.2, "ndvi": 0.04, "ndbi": 0.58, "albedo": 0.13, "heat_anomaly": +5.1,
        "population": 220000, "assets": {"schools": 15, "hospitals": 11, "transit_stops": 38},
        "built_density": 0.96, "heat_persistence_days": 78,
        "max_trees": 700, "max_cool_roof_sqft": 460000, "max_shades": 35, "max_hydration": 32
    },
    {
        "cell_id": "MAA_002", "name": "George Town Harbour Wholesale", "zone": "North",
        "center_lat": 13.0900, "center_lng": 80.2850,
        "boundary": [[13.1000, 80.2740], [13.1000, 80.2960], [13.0800, 80.2960], [13.0800, 80.2740]],
        "lst": 43.8, "ndvi": 0.03, "ndbi": 0.62, "albedo": 0.12, "heat_anomaly": +5.7,
        "population": 190000, "assets": {"schools": 12, "hospitals": 8, "transit_stops": 34},
        "built_density": 0.98, "heat_persistence_days": 82,
        "max_trees": 500, "max_cool_roof_sqft": 420000, "max_shades": 32, "max_hydration": 28
    },
    {
        "cell_id": "MAA_003", "name": "Guindy Industrial Estate", "zone": "South-West",
        "center_lat": 13.0067, "center_lng": 80.2025,
        "boundary": [[13.0180, 80.1910], [13.0180, 80.2140], [12.9950, 80.2140], [12.9950, 80.1910]],
        "lst": 42.5, "ndvi": 0.10, "ndbi": 0.51, "albedo": 0.18, "heat_anomaly": +4.4,
        "population": 130000, "assets": {"schools": 10, "hospitals": 6, "transit_stops": 28},
        "built_density": 0.88, "heat_persistence_days": 66,
        "max_trees": 1600, "max_cool_roof_sqft": 580000, "max_shades": 26, "max_hydration": 22
    },
    {
        "cell_id": "MAA_004", "name": "Velachery Urban Basin", "zone": "South",
        "center_lat": 12.9815, "center_lng": 80.2180,
        "boundary": [[12.9920, 80.2070], [12.9920, 80.2290], [12.9710, 80.2290], [12.9710, 80.2070]],
        "lst": 41.9, "ndvi": 0.08, "ndbi": 0.53, "albedo": 0.15, "heat_anomaly": +3.8,
        "population": 175000, "assets": {"schools": 14, "hospitals": 7, "transit_stops": 25},
        "built_density": 0.90, "heat_persistence_days": 60,
        "max_trees": 1200, "max_cool_roof_sqft": 450000, "max_shades": 24, "max_hydration": 20
    },
    {
        "cell_id": "MAA_005", "name": "Adyar Estuary & Green Corridor", "zone": "Coastal South",
        "center_lat": 13.0033, "center_lng": 80.2550,
        "boundary": [[13.0130, 80.2440], [13.0130, 80.2660], [12.9930, 80.2660], [12.9930, 80.2440]],
        "lst": 38.6, "ndvi": 0.22, "ndbi": 0.36, "albedo": 0.21, "heat_anomaly": +1.2,
        "population": 110000, "assets": {"schools": 12, "hospitals": 5, "transit_stops": 18},
        "built_density": 0.72, "heat_persistence_days": 35,
        "max_trees": 1800, "max_cool_roof_sqft": 300000, "max_shades": 15, "max_hydration": 12
    }
]

# ================= KOLKATA DATASET =================
KOLKATA_CELLS_DATA = [
    {
        "cell_id": "CCU_001", "name": "Burrabazar Wholesale Grid", "zone": "North Central",
        "center_lat": 22.5850, "center_lng": 88.3530,
        "boundary": [[22.5930, 88.3450], [22.5930, 88.3610], [22.5770, 88.3610], [22.5770, 88.3450]],
        "lst": 43.5, "ndvi": 0.03, "ndbi": 0.65, "albedo": 0.12, "heat_anomaly": +5.6,
        "population": 250000, "assets": {"schools": 14, "hospitals": 9, "transit_stops": 36},
        "built_density": 0.98, "heat_persistence_days": 80,
        "max_trees": 400, "max_cool_roof_sqft": 520000, "max_shades": 35, "max_hydration": 35
    },
    {
        "cell_id": "CCU_002", "name": "Howrah Station Rail Concourse", "zone": "West Riverbank",
        "center_lat": 22.5830, "center_lng": 88.3420,
        "boundary": [[22.5920, 88.3340], [22.5920, 88.3500], [22.5740, 88.3500], [22.5740, 88.3340]],
        "lst": 42.8, "ndvi": 0.04, "ndbi": 0.60, "albedo": 0.14, "heat_anomaly": +4.9,
        "population": 210000, "assets": {"schools": 10, "hospitals": 7, "transit_stops": 45},
        "built_density": 0.95, "heat_persistence_days": 74,
        "max_trees": 600, "max_cool_roof_sqft": 440000, "max_shades": 32, "max_hydration": 32
    },
    {
        "cell_id": "CCU_003", "name": "Salt Lake Sector V Tech Park", "zone": "East",
        "center_lat": 22.5760, "center_lng": 88.4340,
        "boundary": [[22.5860, 88.4230], [22.5860, 88.4450], [22.5660, 88.4450], [22.5660, 88.4230]],
        "lst": 41.2, "ndvi": 0.11, "ndbi": 0.48, "albedo": 0.22, "heat_anomaly": +3.3,
        "population": 120000, "assets": {"schools": 8, "hospitals": 5, "transit_stops": 28},
        "built_density": 0.84, "heat_persistence_days": 52,
        "max_trees": 1800, "max_cool_roof_sqft": 620000, "max_shades": 24, "max_hydration": 20
    },
    {
        "cell_id": "CCU_004", "name": "Park Street Central Corridor", "zone": "South Central",
        "center_lat": 22.5510, "center_lng": 88.3530,
        "boundary": [[22.5600, 88.3430], [22.5600, 88.3630], [22.5420, 88.3630], [22.5420, 88.3430]],
        "lst": 40.5, "ndvi": 0.14, "ndbi": 0.45, "albedo": 0.18, "heat_anomaly": +2.6,
        "population": 140000, "assets": {"schools": 15, "hospitals": 8, "transit_stops": 26},
        "built_density": 0.88, "heat_persistence_days": 46,
        "max_trees": 1400, "max_cool_roof_sqft": 400000, "max_shades": 20, "max_hydration": 18
    }
]

# ================= AHMEDABAD DATASET =================
AHMEDABAD_CELLS_DATA = [
    {
        "cell_id": "AMD_001", "name": "Kalupur Walled Heritage Core", "zone": "Central",
        "center_lat": 23.0280, "center_lng": 72.5980,
        "boundary": [[23.0370, 72.5890], [23.0370, 72.6070], [23.0190, 72.6070], [23.0190, 72.5890]],
        "lst": 45.1, "ndvi": 0.03, "ndbi": 0.64, "albedo": 0.13, "heat_anomaly": +6.2,
        "population": 260000, "assets": {"schools": 18, "hospitals": 12, "transit_stops": 38},
        "built_density": 0.97, "heat_persistence_days": 86,
        "max_trees": 600, "max_cool_roof_sqft": 540000, "max_shades": 36, "max_hydration": 34
    },
    {
        "cell_id": "AMD_002", "name": "Naroda GIDC Industrial Cluster", "zone": "North East",
        "center_lat": 23.0780, "center_lng": 72.6620,
        "boundary": [[23.0890, 72.6510], [23.0890, 72.6730], [23.0670, 72.6730], [23.0670, 72.6510]],
        "lst": 44.8, "ndvi": 0.04, "ndbi": 0.62, "albedo": 0.15, "heat_anomaly": +5.9,
        "population": 185000, "assets": {"schools": 12, "hospitals": 7, "transit_stops": 30},
        "built_density": 0.94, "heat_persistence_days": 82,
        "max_trees": 1100, "max_cool_roof_sqft": 650000, "max_shades": 32, "max_hydration": 28
    },
    {
        "cell_id": "AMD_003", "name": "SG Highway Corporate Corridor", "zone": "West",
        "center_lat": 23.0520, "center_lng": 72.5120,
        "boundary": [[23.0640, 72.5000], [23.0640, 72.5240], [23.0400, 72.5240], [23.0400, 72.5000]],
        "lst": 42.6, "ndvi": 0.09, "ndbi": 0.50, "albedo": 0.23, "heat_anomaly": +3.7,
        "population": 145000, "assets": {"schools": 10, "hospitals": 6, "transit_stops": 24},
        "built_density": 0.85, "heat_persistence_days": 62,
        "max_trees": 2200, "max_cool_roof_sqft": 680000, "max_shades": 25, "max_hydration": 20
    },
    {
        "cell_id": "AMD_004", "name": "Maninagar South Urban Belt", "zone": "South",
        "center_lat": 22.9980, "center_lng": 72.6050,
        "boundary": [[23.0080, 72.5950], [23.0080, 72.6150], [22.9880, 72.6150], [22.9880, 72.5950]],
        "lst": 43.0, "ndvi": 0.07, "ndbi": 0.55, "albedo": 0.16, "heat_anomaly": +4.1,
        "population": 210000, "assets": {"schools": 16, "hospitals": 8, "transit_stops": 28},
        "built_density": 0.91, "heat_persistence_days": 70,
        "max_trees": 1300, "max_cool_roof_sqft": 480000, "max_shades": 26, "max_hydration": 24
    }
]

# ================= JAIPUR DATASET =================
JAIPUR_CELLS_DATA = [
    {
        "cell_id": "JAI_001", "name": "Walled Pink City Heritage Corridor", "zone": "Central Heritage",
        "center_lat": 26.9220, "center_lng": 75.8267,
        "boundary": [[26.9320, 75.8160], [26.9320, 75.8370], [26.9120, 75.8370], [26.9120, 75.8160]],
        "lst": 44.5, "ndvi": 0.04, "ndbi": 0.60, "albedo": 0.18, "heat_anomaly": +5.5,
        "population": 220000, "assets": {"schools": 16, "hospitals": 9, "transit_stops": 34},
        "built_density": 0.96, "heat_persistence_days": 84,
        "max_trees": 700, "max_cool_roof_sqft": 450000, "max_shades": 35, "max_hydration": 30
    },
    {
        "cell_id": "JAI_002", "name": "Sitapura Industrial & SEZ Hub", "zone": "South",
        "center_lat": 26.7780, "center_lng": 75.8450,
        "boundary": [[26.7900, 75.8320], [26.7900, 75.8580], [26.7660, 75.8580], [26.7660, 75.8320]],
        "lst": 45.2, "ndvi": 0.03, "ndbi": 0.65, "albedo": 0.16, "heat_anomaly": +6.2,
        "population": 110000, "assets": {"schools": 6, "hospitals": 4, "transit_stops": 22},
        "built_density": 0.92, "heat_persistence_days": 88,
        "max_trees": 1500, "max_cool_roof_sqft": 650000, "max_shades": 28, "max_hydration": 26
    },
    {
        "cell_id": "JAI_003", "name": "Malviya Nagar Residential Belt", "zone": "South Central",
        "center_lat": 26.8550, "center_lng": 75.8150,
        "boundary": [[26.8660, 75.8030], [26.8660, 75.8270], [26.8440, 75.8270], [26.8440, 75.8030]],
        "lst": 42.1, "ndvi": 0.10, "ndbi": 0.48, "albedo": 0.21, "heat_anomaly": +3.1,
        "population": 160000, "assets": {"schools": 14, "hospitals": 7, "transit_stops": 24},
        "built_density": 0.85, "heat_persistence_days": 60,
        "max_trees": 1600, "max_cool_roof_sqft": 420000, "max_shades": 20, "max_hydration": 18
    }
]

# ================= SINGAPORE DATASET =================
SINGAPORE_CELLS_DATA = [
    {
        "cell_id": "SIN_001", "name": "Jurong Industrial Heavy Cluster", "zone": "West Industrial",
        "center_lat": 1.3329, "center_lng": 103.7050,
        "boundary": [[1.3440, 103.6930], [1.3440, 103.7170], [1.3210, 103.7170], [1.3210, 103.6930]],
        "lst": 37.8, "ndvi": 0.12, "ndbi": 0.55, "albedo": 0.16, "heat_anomaly": +4.2,
        "population": 95000, "assets": {"schools": 8, "hospitals": 4, "transit_stops": 25},
        "built_density": 0.90, "heat_persistence_days": 65,
        "max_trees": 1800, "max_cool_roof_sqft": 700000, "max_shades": 25, "max_hydration": 20
    },
    {
        "cell_id": "SIN_002", "name": "Orchard Downtown Urban Canyon", "zone": "Central",
        "center_lat": 1.3048, "center_lng": 103.8318,
        "boundary": [[1.3140, 103.8220], [1.3140, 103.8410], [1.2950, 103.8410], [1.2950, 103.8220]],
        "lst": 35.6, "ndvi": 0.18, "ndbi": 0.48, "albedo": 0.22, "heat_anomaly": +2.4,
        "population": 80000, "assets": {"schools": 6, "hospitals": 5, "transit_stops": 32},
        "built_density": 0.94, "heat_persistence_days": 42,
        "max_trees": 1200, "max_cool_roof_sqft": 450000, "max_shades": 28, "max_hydration": 22
    },
    {
        "cell_id": "SIN_003", "name": "Marina South Coastal Front", "zone": "Downtown South",
        "center_lat": 1.2789, "center_lng": 103.8590,
        "boundary": [[1.2880, 103.8490], [1.2880, 103.8690], [1.2700, 103.8690], [1.2700, 103.8490]],
        "lst": 33.5, "ndvi": 0.28, "ndbi": 0.35, "albedo": 0.26, "heat_anomaly": +0.8,
        "population": 45000, "assets": {"schools": 3, "hospitals": 2, "transit_stops": 20},
        "built_density": 0.65, "heat_persistence_days": 20,
        "max_trees": 2000, "max_cool_roof_sqft": 350000, "max_shades": 15, "max_hydration": 15
    }
]

# ================= LONDON DATASET =================
LONDON_CELLS_DATA = [
    {
        "cell_id": "LON_001", "name": "City of London Financial Core", "zone": "Central",
        "center_lat": 51.5155, "center_lng": -0.0922,
        "boundary": [[51.5230, -0.1040], [51.5230, -0.0800], [51.5080, -0.0800], [51.5080, -0.1040]],
        "lst": 34.2, "ndvi": 0.08, "ndbi": 0.58, "albedo": 0.18, "heat_anomaly": +4.8,
        "population": 85000, "assets": {"schools": 6, "hospitals": 4, "transit_stops": 38},
        "built_density": 0.95, "heat_persistence_days": 38,
        "max_trees": 800, "max_cool_roof_sqft": 450000, "max_shades": 22, "max_hydration": 20
    },
    {
        "cell_id": "LON_002", "name": "Croydon Urban Heat Suburb", "zone": "South London",
        "center_lat": 51.3762, "center_lng": -0.0982,
        "boundary": [[51.3870, -0.1120], [51.3870, -0.0840], [51.3650, -0.0840], [51.3650, -0.1120]],
        "lst": 32.8, "ndvi": 0.15, "ndbi": 0.46, "albedo": 0.19, "heat_anomaly": +3.4,
        "population": 195000, "assets": {"schools": 18, "hospitals": 6, "transit_stops": 28},
        "built_density": 0.82, "heat_persistence_days": 28,
        "max_trees": 1500, "max_cool_roof_sqft": 400000, "max_shades": 18, "max_hydration": 16
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
        "default_budget": 10000000.0,
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
        "default_budget": 15000000.0,
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
    "Pune": {
        "city_id": "pune",
        "name": "Pune Metropolitan Region",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [18.5204, 73.8567],
        "zoom": 12,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 10000000.0,
        "raw_cells": PUNE_CELLS_DATA
    },
    "Chennai": {
        "city_id": "chennai",
        "name": "Chennai (Tamil Nadu)",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [13.0827, 80.2707],
        "zoom": 11,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 12000000.0,
        "raw_cells": CHENNAI_CELLS_DATA
    },
    "Kolkata": {
        "city_id": "kolkata",
        "name": "Kolkata (West Bengal)",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [22.5726, 88.3639],
        "zoom": 11,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 12000000.0,
        "raw_cells": KOLKATA_CELLS_DATA
    },
    "Ahmedabad": {
        "city_id": "ahmedabad",
        "name": "Ahmedabad (Gujarat)",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [23.0225, 72.5714],
        "zoom": 11,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 12000000.0,
        "raw_cells": AHMEDABAD_CELLS_DATA
    },
    "Jaipur": {
        "city_id": "jaipur",
        "name": "Jaipur Pink City (Rajasthan)",
        "country": "India",
        "country_flag": "🇮🇳",
        "center": [26.9124, 75.7873],
        "zoom": 11,
        "currency": "INR",
        "currency_symbol": "₹",
        "default_budget": 10000000.0,
        "raw_cells": JAIPUR_CELLS_DATA
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
    "Singapore": {
        "city_id": "singapore",
        "name": "Singapore Island State",
        "country": "Singapore",
        "country_flag": "🇸🇬",
        "center": [1.3521, 103.8198],
        "zoom": 12,
        "currency": "SGD",
        "currency_symbol": "S$ ",
        "default_budget": 15000000.0,
        "raw_cells": SINGAPORE_CELLS_DATA
    },
    "London": {
        "city_id": "london",
        "name": "Greater London Heat Basin",
        "country": "United Kingdom",
        "country_flag": "🇬🇧",
        "center": [51.5074, -0.1278],
        "zoom": 11,
        "currency": "GBP",
        "currency_symbol": "£",
        "default_budget": 10000000.0,
        "raw_cells": LONDON_CELLS_DATA
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
    """Returns country -> cities hierarchy and ward metadata for cascading dropdowns."""
    hierarchy = {}
    for city_key, meta in CITIES_REGISTRY.items():
        country = meta["country"]
        if country not in hierarchy:
            hierarchy[country] = {
                "country": country,
                "flag": meta["country_flag"],
                "cities": []
            }
        wards_summary = [
            {
                "cell_id": w["cell_id"],
                "name": w["name"],
                "zone": w["zone"],
                "lst": w["lst"],
                "center": [w["center_lat"], w["center_lng"]]
            }
            for w in meta["raw_cells"]
        ]
        hierarchy[country]["cities"].append({
            "key": city_key,
            "name": meta["name"],
            "center": meta["center"],
            "zoom": meta["zoom"],
            "currency": meta["currency"],
            "currency_symbol": meta["currency_symbol"],
            "wards_count": len(meta["raw_cells"]),
            "wards": wards_summary
        })
    return {
        "default_country": "India",
        "default_city": "Bengaluru",
        "countries": list(hierarchy.values())
    }

def get_climate_cells_for_city(city_name: str) -> List[ClimateCell]:
    """Loads and instantiates ClimateCell objects for any registered city."""
    city_entry = None
    for k, v in CITIES_REGISTRY.items():
        if k.lower() == city_name.strip().lower() or v["city_id"] == city_name.strip().lower():
            city_entry = v
            break
            
    if not city_entry:
        city_entry = CITIES_REGISTRY["Bengaluru"]

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

def get_temperature_timeline(city_name: str, cell_id: Optional[str] = None) -> TemperatureTimelineResponse:
    """
    Computes a realistic 24-hour Diurnal Temperature Profile and 7-day heatwave forecast
    for the selected city or specific ward.
    """
    city_entry = None
    for k, v in CITIES_REGISTRY.items():
        if k.lower() == city_name.strip().lower() or v["city_id"] == city_name.strip().lower():
            city_entry = v
            break
    if not city_entry:
        city_entry = CITIES_REGISTRY["Bengaluru"]

    raw_cells = city_entry["raw_cells"]
    target_cell = None
    if cell_id:
        for c in raw_cells:
            if c["cell_id"] == cell_id:
                target_cell = c
                break
    if not target_cell:
        # Default to highest LST ward in the city
        target_cell = max(raw_cells, key=lambda x: x["lst"])

    peak_lst = target_cell["lst"]
    base_min = round(peak_lst - 17.5, 1) # Pre-dawn minimum (~23C-28C)
    
    # Realistic solar heating profile: hours from midnight to 21:00
    diurnal_hours = ["00:00", "03:00", "06:00", "09:00", "12:00", "14:00", "15:00", "18:00", "21:00"]
    # Solar insolation weight factors [0.0 - 1.0]
    solar_weights = [0.22, 0.08, 0.00, 0.45, 0.88, 1.00, 0.98, 0.65, 0.38]
    
    baseline_curve = []
    cooled_curve = []
    cooling_delta = 2.4 # Expected thermal drop with cool roofs & canopy
    
    for w in solar_weights:
        temp = round(base_min + (peak_lst - base_min) * w, 1)
        # Interventions have highest impact during high insolation (peak solar hours)
        cool_effect = round(cooling_delta * (0.35 + 0.65 * w), 1)
        cooled_temp = round(temp - cool_effect, 1)
        baseline_curve.append(temp)
        cooled_curve.append(cooled_temp)

    # 7-day forecast
    days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    today = datetime.now()
    forecast = []
    # Realistic anomaly variations across the upcoming week
    var_offsets = [0.0, +0.8, +1.5, +0.4, -0.6, +1.2, +0.3]
    for i in range(7):
        target_day = today + timedelta(days=i)
        offset = var_offsets[i]
        d_high = round(peak_lst + offset, 1)
        d_low = round(base_min + offset * 0.4, 1)
        d_mitigated = round(d_high - cooling_delta, 1)
        
        if d_high >= 44.0:
            alert = "Red Severe Alert"
        elif d_high >= 41.5:
            alert = "Orange Alert"
        elif d_high >= 38.0:
            alert = "Yellow Watch"
        else:
            alert = "Normal"
            
        forecast.append(DayForecast(
            day=days_names[target_day.weekday()],
            date=target_day.strftime("%d %b"),
            high_c=d_high,
            low_c=d_low,
            mitigated_high_c=d_mitigated,
            alert_level=alert
        ))

    # Calculate hours above 38°C (hazardous duration)
    hazard_hours = 8.5 if peak_lst >= 42.0 else (6.0 if peak_lst >= 39.0 else 4.0)

    return TemperatureTimelineResponse(
        city=city_entry["name"],
        ward_id=target_cell["cell_id"],
        ward_name=target_cell["name"],
        current_lst_c=peak_lst,
        peak_high_c=peak_lst,
        peak_time="14:00 (Peak Solar Flux)",
        low_temp_c=base_min,
        low_time="06:00 (Pre-Dawn Minimum)",
        heat_hazard_duration_hours=hazard_hours,
        cooling_delta_c=cooling_delta,
        diurnal_hours=diurnal_hours,
        baseline_temp_c=baseline_curve,
        cooled_temp_c=cooled_curve,
        forecast_7days=forecast
    )

