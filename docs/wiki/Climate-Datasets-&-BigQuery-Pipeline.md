# 🛰️ Climate Datasets & BigQuery Pipeline

Avani Albedo ingests real planetary observations from ECMWF ERA5 reanalysis and multi-spectral satellite imagery (Landsat 8/9 Thermal Infrared, Sentinel-2 Optical).

---

## 📊 The 8 BigQuery Tables (`avani_climate`)

1. **`urban_heat_cells`**:
   - High-resolution hexagonal and polygon climate cells.
   - Includes surface temperature ($^\circ\text{C}$), air temperature ($^\circ\text{C}$), heat anomalies, NDVI (vegetation), NDBI (built index), albedo, HVI score, population, vulnerable infrastructure (schools, hospitals, transit stops), and a native BigQuery `GEOGRAPHY` spatial point `ST_GEOGPOINT(lon, lat)`.
2. **`historical_heatwave_observations`**:
   - 10-year recorded heatwave events across Indian & global metropolitan areas.
3. **`twenty_year_climate_trends`**:
   - 20-year annual and seasonal temperature anomalies from 2005 to 2025.
4. **`heat_action_interventions`**:
   - Catalog of cooling interventions (Cool Roofs, Urban Forestry, High-Albedo Pavements, Solar Reflective Canopies) with unit costs ($\text{INR/m}^2$) and cooling coefficients ($\Delta^\circ\text{C}$).
5. **`prescriptive_scenarios`**:
   - Audit trail of mathematical optimizer executions, budget allocations, and predicted temperature reductions.
6. **`realtime_microclimate_telemetry`**:
   - Hourly sensor feeds with ambient humidity, solar irradiance ($\text{W/m}^2$), and wind speed ($\text{m/s}$).
7. **`ward_vulnerability_index`**:
   - Ward-level aggregated Heat Vulnerability Index (HVI) categorized into Critical, Severe, High, Moderate, and Low.
8. **`scientific_data_lineage`**:
   - Data provenance tracking sensor types, spatial resolutions, calibration methods, and ISO timestamps.

---

## 💰 Zero-Cost Two-Stage Batch Pipeline

Streaming inserts to BigQuery cost money per megabyte. Avani Albedo eliminates 100% of BigQuery ingestion charges by using a two-stage local staging and GCS batch load pipeline:

```
[ Local Stage: data/json_staging/*.json ]
                 │
                 ▼
[ Google Cloud Storage: gs://avani-albedo-climate-staging/ ]
                 │ (bq load --source_format=NEWLINE_DELIMITED_JSON)
                 ▼
[ BigQuery: avani-albedo.avani_climate.* ]  <-- $0.00 INGESTION COST!
```

### Execution Script:
```bash
# Ingest all staged records to GCS and BigQuery in seconds
./scripts/push_staging_to_gcs_and_bq.sh
```
