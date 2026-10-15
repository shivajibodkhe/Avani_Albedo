#!/usr/bin/env python3
"""
Seed BigQuery Tables for Avani Albedo
Creates:
1. avani_climate.urban_heat_cells (with GEOGRAPHY spatial points)
2. avani_climate.heat_action_interventions (budget and cooling impacts)
3. avani_climate.prescriptive_scenarios (mathematical optimizer audit records)
"""

import sys
import json
import subprocess
from app.data.cities_heat_data import (
    get_geographic_hierarchy,
    get_climate_cells_for_city,
    get_twenty_year_satellite_archive,
    CITIES_REGISTRY
)

PROJECT_ID = "avani-albedo"
DATASET_ID = "avani_climate"

def run_bq_query(sql: str):
    """Executes a SQL query in BigQuery via bq CLI."""
    cmd = [
        "bq", "query",
        "--use_legacy_sql=false",
        f"--project_id={PROJECT_ID}",
        sql
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running query:\n{res.stderr}", file=sys.stderr)
        return False
    return True

def create_tables():
    print("🚀 Step 1: Creating BigQuery Tables...")

    # Table 1: Urban Heat Cells (Spatial Intelligence with GEOGRAPHY)
    ddl_cells = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.urban_heat_cells` (
        cell_id STRING,
        city STRING,
        ward_id STRING,
        ward_name STRING,
        surface_temp_c FLOAT64,
        air_temp_c FLOAT64,
        heat_anomaly_c FLOAT64,
        ndvi FLOAT64,
        ndbi FLOAT64,
        albedo FLOAT64,
        hvi_score FLOAT64,
        vulnerability_category STRING,
        population INT64,
        schools_count INT64,
        hospitals_count INT64,
        transit_stops_count INT64,
        built_density FLOAT64,
        heat_persistence_days INT64,
        latitude FLOAT64,
        longitude FLOAT64,
        geom GEOGRAPHY,
        updated_at TIMESTAMP
    );
    """
    if run_bq_query(ddl_cells):
        print("  ✓ Created table: urban_heat_cells")

    # Table 2: Heat Action Interventions
    ddl_interventions = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.heat_action_interventions` (
        intervention_id STRING,
        intervention_type STRING,
        target_city STRING,
        cooling_impact_c FLOAT64,
        albedo_delta FLOAT64,
        cost_inr FLOAT64,
        lifespan_years INT64,
        co_benefits STRING,
        created_at TIMESTAMP
    );
    """
    if run_bq_query(ddl_interventions):
        print("  ✓ Created table: heat_action_interventions")

    # Table 3: Prescriptive Scenarios
    ddl_scenarios = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.prescriptive_scenarios` (
        scenario_id STRING,
        city STRING,
        budget_inr FLOAT64,
        heat_reduction_pct FLOAT64,
        trees_planted INT64,
        cool_roof_sqft FLOAT64,
        shades_installed INT64,
        hydration_points INT64,
        optimizer_solver STRING,
        computation_time_ms FLOAT64,
        created_at TIMESTAMP
    );
    """
    if run_bq_query(ddl_scenarios):
        print("  ✓ Created table: prescriptive_scenarios")

    # Table 4: 20-Year Satellite Climate Radiometric Trends (2005 - 2025)
    ddl_trends = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.twenty_year_climate_trends` (
        city STRING,
        year INT64,
        avg_lst_c FLOAT64,
        heat_anomaly_c FLOAT64,
        trees_lost_cumulative INT64,
        ndvi FLOAT64,
        built_up_fraction FLOAT64,
        satellite_sensor STRING,
        observation_date STRING,
        created_at TIMESTAMP
    );
    """
    if run_bq_query(ddl_trends):
        print("  ✓ Created table: twenty_year_climate_trends")

    # Table 5: Ward Vulnerability Aggregates & Heat Index
    ddl_vulnerability = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET_ID}.ward_vulnerability_index` (
        city STRING,
        total_wards INT64,
        avg_hvi_score FLOAT64,
        high_risk_wards INT64,
        total_population_at_risk INT64,
        avg_albedo FLOAT64,
        avg_surface_temp_c FLOAT64,
        critical_infrastructure_count INT64,
        updated_at TIMESTAMP
    );
    """
    if run_bq_query(ddl_vulnerability):
        print("  ✓ Created table: ward_vulnerability_index")

def seed_cells():
    print("\n🌱 Step 2: Ingesting Urban Heat Cells into BigQuery...")
    hierarchy = get_geographic_hierarchy()
    
    cities = []
    for country in hierarchy.get("countries", []):
        for c in country.get("cities", []):
            cities.append(c["key"])

    rows = []
    for city in cities:
        cells = get_climate_cells_for_city(city)
        for c in cells:
            cell_dict = c.model_dump() if hasattr(c, "model_dump") else c.dict()
            assets = cell_dict.get("critical_assets", {}) or {}
            
            # Escape strings safely
            name_esc = cell_dict.get("name", "").replace("'", "\\'")
            zone_esc = cell_dict.get("zone", "").replace("'", "\\'")
            cat_esc = cell_dict.get("vulnerability_category", "Moderate").replace("'", "\\'")
            
            lat = float(cell_dict.get("center_lat", 0.0))
            lng = float(cell_dict.get("center_lng", 0.0))
            
            rows.append(f"""(
                '{cell_dict.get("cell_id")}',
                '{city}',
                '{zone_esc}',
                '{name_esc}',
                {float(cell_dict.get("surface_temp_c", 0.0))},
                {float(cell_dict.get("air_temp_c", 0.0))},
                {float(cell_dict.get("heat_anomaly", 0.0))},
                {float(cell_dict.get("ndvi", 0.0))},
                {float(cell_dict.get("ndbi", 0.0))},
                {float(cell_dict.get("albedo", 0.0))},
                {float(cell_dict.get("hvi_score", 0.0))},
                '{cat_esc}',
                {int(cell_dict.get("population", 0))},
                {int(assets.get("schools", 0))},
                {int(assets.get("hospitals", 0))},
                {int(assets.get("transit_stops", 0))},
                {float(cell_dict.get("built_density", 0.0))},
                {int(cell_dict.get("heat_persistence_days", 0))},
                {lat},
                {lng},
                ST_GEOGPOINT({lng}, {lat}),
                CURRENT_TIMESTAMP()
            )""")

    if not rows:
        print("No cells found to insert.")
        return

    # Delete existing rows and reinsert cleanly
    run_bq_query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.urban_heat_cells` WHERE TRUE;")

    # Batch insert in chunks of 50
    chunk_size = 50
    total_inserted = 0
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i + chunk_size]
        values_sql = ",\n".join(chunk)
        insert_sql = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.urban_heat_cells` (
            cell_id, city, ward_id, ward_name, surface_temp_c, air_temp_c,
            heat_anomaly_c, ndvi, ndbi, albedo, hvi_score, vulnerability_category,
            population, schools_count, hospitals_count, transit_stops_count,
            built_density, heat_persistence_days, latitude, longitude, geom, updated_at
        ) VALUES {values_sql};
        """
        if run_bq_query(insert_sql):
            total_inserted += len(chunk)
            print(f"  Inserted {total_inserted}/{len(rows)} climate cells...")

    print(f"  ✓ Total {total_inserted} climate cells ingested with GEOGRAPHY points.")

def seed_interventions_and_scenarios():
    print("\n🌿 Step 3: Seeding Interventions & Prescriptive Scenarios...")
    
    run_bq_query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.heat_action_interventions` WHERE TRUE;")
    run_bq_query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.prescriptive_scenarios` WHERE TRUE;")

    interventions_sql = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.heat_action_interventions` (
        intervention_id, intervention_type, target_city, cooling_impact_c,
        albedo_delta, cost_inr, lifespan_years, co_benefits, created_at
    ) VALUES
    ('INT_001', 'High-Albedo Cool Roof Coating', 'Bengaluru', 2.8, 0.45, 1200000, 7, 'Reduces indoor heat by 3.5C and air-conditioning electricity usage by 18%', CURRENT_TIMESTAMP()),
    ('INT_002', 'Urban Miyawaki Forest & Tree Canopy', 'Bengaluru', 3.4, 0.15, 2500000, 25, 'Biophilic carbon sink, stormwater filtration, and PM2.5 particulate reduction', CURRENT_TIMESTAMP()),
    ('INT_003', 'Tensile Shade Sails & Green Bus Stops', 'Bengaluru', 1.9, 0.35, 750000, 10, 'Immediate pedestrian relief from acute solar irradiation at transit stops', CURRENT_TIMESTAMP()),
    ('INT_004', 'Solar-Powered Mist Hydration Kiosks', 'Bengaluru', 1.2, 0.05, 450000, 8, 'Prevents heat exhaustion, dehydration, and heatstroke among outdoor workers', CURRENT_TIMESTAMP()),
    ('INT_005', 'High-Albedo Cool Roof Coating', 'Mumbai', 2.6, 0.42, 1800000, 7, 'Mitigates coastal high-humidity heat index across high-density wards', CURRENT_TIMESTAMP()),
    ('INT_006', 'Urban Miyawaki Forest & Tree Canopy', 'Mumbai', 3.2, 0.18, 3200000, 25, 'Absorbs urban heat island and improves coastal drainage', CURRENT_TIMESTAMP());
    """
    if run_bq_query(interventions_sql):
        print("  ✓ Seeded 6 prescriptive interventions.")

    scenarios_sql = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.prescriptive_scenarios` (
        scenario_id, city, budget_inr, heat_reduction_pct, trees_planted,
        cool_roof_sqft, shades_installed, hydration_points, optimizer_solver,
        computation_time_ms, created_at
    ) VALUES
    ('SCEN_BLR_01', 'Bengaluru', 10000000, 18.4, 1850, 420000, 32, 28, 'Google OR-Tools SCIP v9.8', 42.5, CURRENT_TIMESTAMP()),
    ('SCEN_BLR_02', 'Bengaluru', 25000000, 34.2, 4500, 1150000, 75, 60, 'Google OR-Tools SCIP v9.8', 68.2, CURRENT_TIMESTAMP()),
    ('SCEN_BOM_01', 'Mumbai', 15000000, 22.1, 2200, 680000, 40, 35, 'Google OR-Tools SCIP v9.8', 51.4, CURRENT_TIMESTAMP());
    """
    if run_bq_query(scenarios_sql):
        print("  ✓ Seeded 3 optimized mathematical scenarios.")

def seed_trends_and_vulnerability():
    print("\n🛰️ Step 4: Seeding 20-Year Climate Trends & Ward Vulnerability Indices...")

    # 1. Seed 20-Year Radiometric Trends
    run_bq_query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.twenty_year_climate_trends` WHERE TRUE;")
    run_bq_query(f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.ward_vulnerability_index` WHERE TRUE;")

    trend_rows = []
    vulnerability_rows = []

    for city_key, city_data in CITIES_REGISTRY.items():
        city_name = city_data["name"]
        
        # 20-Year Archive records
        archive = get_twenty_year_satellite_archive(city_name)
        for rec in archive.records:
            sensor_esc = rec.satellite_sensor.replace("'", "\\'")
            trend_rows.append(f"""(
                '{city_name}',
                {rec.year},
                {rec.avg_lst_c},
                {rec.heat_anomaly_c},
                {rec.trees_lost_cumulative},
                {rec.ndvi},
                {rec.built_up_fraction},
                '{sensor_esc}',
                '{rec.observation_date}',
                CURRENT_TIMESTAMP()
            )""")

        # Ward Vulnerability Aggregates
        cells = get_climate_cells_for_city(city_key)
        total_wards = len(cells)
        if total_wards > 0:
            avg_hvi = sum(getattr(c, "hvi_score", 0.0) for c in cells) / total_wards
            high_risk = sum(1 for c in cells if getattr(c, "hvi_category", "Moderate") in ["High", "Extreme", "Severe"])
            total_pop = sum(c.population for c in cells)
            avg_albedo = sum(c.albedo for c in cells) / total_wards
            avg_lst = sum(c.lst for c in cells) / total_wards
            total_infra = sum(
                (c.assets.schools + c.assets.hospitals + c.assets.transit_stops)
                for c in cells
            )

            vulnerability_rows.append(f"""(
                '{city_name}',
                {total_wards},
                {round(avg_hvi, 2)},
                {high_risk},
                {total_pop},
                {round(avg_albedo, 2)},
                {round(avg_lst, 1)},
                {total_infra},
                CURRENT_TIMESTAMP()
            )""")

    if trend_rows:
        trends_sql = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.twenty_year_climate_trends` (
            city, year, avg_lst_c, heat_anomaly_c, trees_lost_cumulative,
            ndvi, built_up_fraction, satellite_sensor, observation_date, created_at
        ) VALUES {', '.join(trend_rows)};
        """
        if run_bq_query(trends_sql):
            print(f"  ✓ Ingested {len(trend_rows)} 20-year satellite climate trend records across {len(CITIES_REGISTRY)} cities.")

    if vulnerability_rows:
        vuln_sql = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.ward_vulnerability_index` (
            city, total_wards, avg_hvi_score, high_risk_wards, total_population_at_risk,
            avg_albedo, avg_surface_temp_c, critical_infrastructure_count, updated_at
        ) VALUES {', '.join(vulnerability_rows)};
        """
        if run_bq_query(vuln_sql):
            print(f"  ✓ Ingested {len(vulnerability_rows)} ward vulnerability index records.")

if __name__ == "__main__":
    create_tables()
    seed_cells()
    seed_interventions_and_scenarios()
    seed_trends_and_vulnerability()
    print("\n🎉 BigQuery 'avani_climate' schema and tables are fully initialized!")
