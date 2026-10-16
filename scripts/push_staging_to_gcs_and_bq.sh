#!/usr/bin/env bash
# ==============================================================================
# 🚀 Avani Albedo — Cost-Optimized Cloud Storage (GCS) to BigQuery Ingestion Pipeline
# ==============================================================================
# 💡 ARCHITECTURAL BENEFIT:
# Google BigQuery batch load (`bq load`) from Google Cloud Storage (GCS) is
# 100% FREE OF INGESTION CHARGES (unlike continuous streaming insert API calls).
#
# Workflow:
# 1. Local Staged JSONL -> 2. GCS Bucket Batch Upload -> 3. BigQuery Batch Load
# ==============================================================================

set -e

PROJECT_ID="avani-albedo"
DATASET_ID="avani_climate"
REGION="asia-south1"
BUCKET_NAME="gs://${PROJECT_ID}-climate-staging"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGING_DIR="${SCRIPT_DIR}/../data/json_staging"

echo "========================================================================"
echo " 🌍 Avani Albedo — Zero-Cost GCS to BigQuery Batch Loader"
echo "========================================================================"
echo "Project ID:   ${PROJECT_ID}"
echo "Dataset:      ${DATASET_ID}"
echo "GCS Target:   ${BUCKET_NAME}"
echo "Local Staging: ${STAGING_DIR}"
echo "========================================================================"

if [ ! -d "${STAGING_DIR}" ]; then
  echo "❌ Error: Staging directory ${STAGING_DIR} does not exist!"
  exit 1
fi

# Step 1: Ensure GCS Bucket Exists
echo ""
echo "📦 Step 1: Checking Google Cloud Storage Bucket (${BUCKET_NAME})..."
if gcloud storage buckets describe "${BUCKET_NAME}" >/dev/null 2>&1; then
  echo "  ✓ Cloud Storage bucket exists."
else
  echo "  Creating GCS bucket in region ${REGION}..."
  gcloud storage buckets create "${BUCKET_NAME}" --location="${REGION}" --project="${PROJECT_ID}"
  echo "  ✓ GCS bucket created."
fi

# Step 2: Batch Upload JSONL Files to Cloud Storage
echo ""
echo "☁️ Step 2: Uploading Staged JSONL Records to Cloud Storage..."
gcloud storage cp "${STAGING_DIR}"/*.jsonl "${BUCKET_NAME}/staging/"
echo "  ✓ All JSONL datasets uploaded to ${BUCKET_NAME}/staging/"

# Step 3: Zero-Cost Batch Load into BigQuery
echo ""
echo "⚡ Step 3: Executing Free Batch Loads from GCS to BigQuery (${DATASET_ID})..."

# Helper function to load a table
load_bq_table() {
  local table_name="$1"
  local schema_file="$2"
  echo "  • Loading ${table_name} from ${BUCKET_NAME}/staging/${table_name}.jsonl..."
  
  bq load \
    --source_format=NEWLINE_DELIMITED_JSON \
    --replace \
    --project_id="${PROJECT_ID}" \
    "${DATASET_ID}.${table_name}" \
    "${BUCKET_NAME}/staging/${table_name}.jsonl" \
    "${schema_file}"
  echo "    ✓ ${table_name} loaded successfully."
}

# Define and execute table loads with explicit schemas
load_bq_table "scientific_data_lineage" "dataset_name:STRING,sensor_or_model:STRING,spatial_resolution:STRING,temporal_span:STRING,radiative_transfer_formula:STRING,calibration_standard:STRING,rmse_accuracy:STRING,correlation_r2:FLOAT,confidence_level_pct:FLOAT,peer_reviewed_citations:STRING,updated_at:TIMESTAMP"

load_bq_table "urban_heat_cells" "cell_id:STRING,city:STRING,ward_id:STRING,ward_name:STRING,surface_temp_c:FLOAT,air_temp_c:FLOAT,heat_anomaly_c:FLOAT,ndvi:FLOAT,ndbi:FLOAT,albedo:FLOAT,hvi_score:FLOAT,vulnerability_category:STRING,population:INTEGER,schools_count:INTEGER,hospitals_count:INTEGER,transit_stops_count:INTEGER,built_density:FLOAT,heat_persistence_days:INTEGER,latitude:FLOAT,longitude:FLOAT,geom:GEOGRAPHY,updated_at:TIMESTAMP"

load_bq_table "twenty_year_climate_trends" "city:STRING,year:INTEGER,avg_lst_c:FLOAT,heat_anomaly_c:FLOAT,trees_lost_cumulative:INTEGER,ndvi:FLOAT,built_up_fraction:FLOAT,satellite_sensor:STRING,observation_date:STRING,created_at:TIMESTAMP"

load_bq_table "ward_vulnerability_index" "city:STRING,total_wards:INTEGER,avg_hvi_score:FLOAT,high_risk_wards:INTEGER,total_population_at_risk:INTEGER,avg_albedo:FLOAT,avg_surface_temp_c:FLOAT,critical_infrastructure_count:INTEGER,updated_at:TIMESTAMP"

load_bq_table "heat_action_interventions" "intervention_id:STRING,intervention_type:STRING,target_city:STRING,cooling_impact_c:FLOAT,albedo_delta:FLOAT,cost_inr:FLOAT,lifespan_years:INTEGER,co_benefits:STRING,created_at:TIMESTAMP"

load_bq_table "prescriptive_scenarios" "scenario_id:STRING,city:STRING,budget_inr:FLOAT,heat_reduction_pct:FLOAT,trees_planted:INTEGER,cool_roof_sqft:FLOAT,shades_installed:INTEGER,hydration_points:INTEGER,optimizer_solver:STRING,computation_time_ms:FLOAT,created_at:TIMESTAMP"

load_bq_table "realtime_microclimate_telemetry" "cell_id:STRING,city:STRING,ward_name:STRING,latitude:FLOAT,longitude:FLOAT,observation_time:TIMESTAMP,air_temp_c:FLOAT,surface_temp_c:FLOAT,apparent_temp_c:FLOAT,relative_humidity_pct:FLOAT,direct_solar_irradiance_wm2:FLOAT,noaa_heat_index_c:FLOAT,data_source:STRING,calibration_standard:STRING,geom:GEOGRAPHY,ingested_at:TIMESTAMP"

load_bq_table "historical_heatwave_observations" "city:STRING,year:INTEGER,peak_date:STRING,max_air_temp_c:FLOAT,max_apparent_temp_c:FLOAT,solar_radiation_mj_m2:FLOAT,heatwave_alert_level:STRING,data_source:STRING,ingested_at:TIMESTAMP"

echo ""
echo "========================================================================"
echo " 🏆 ALL 8 BIGQUERY DATASETS LOADED VIA GCS BATCH PIPELINE!"
echo " 💰 Total BigQuery Ingestion Charges: \$0.00 (Free GCS Batch Load)"
echo "========================================================================"
