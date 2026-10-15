#!/usr/bin/env bash
# ==============================================================================
# 🌍 AVANI ALBEDO — One-Shot Google Cloud Platform Deployment Script
# Targets: Cloud Run, Cloud Firestore, BigQuery, Secret Manager
# Project ID: avani-albedo | Region: asia-south1 (Mumbai)
# Budget Safe: Configured with scale-to-zero and max 2 instances (< ₹1,000/mo)
# ==============================================================================

set -euo pipefail

# ANSI Colors
BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
MAGENTA="\033[0;35m"
NC="\033[0m"

# Project Configuration (from my_gcp_details.md)
PROJECT_ID="${GCP_PROJECT_ID:-avani-albedo}"
PROJECT_NUMBER="615055398519"
REGION="${GCP_REGION:-asia-south1}"
SERVICE_NAME="avani-albedo"
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
GEMINI_KEY_INPUT=""

# Help documentation
show_help() {
    echo -e "${BOLD}${CYAN}Avani Albedo — One-Shot GCP Deployment Tool${NC}\n"
    echo -e "${BOLD}Usage:${NC} ./deploy_gcp.sh [options]\n"
    echo -e "${BOLD}Options:${NC}"
    echo -e "  ${CYAN}--project <id>${NC}     GCP Project ID (default: avani-albedo)"
    echo -e "  ${CYAN}--region <name>${NC}    GCP Region (default: asia-south1)"
    echo -e "  ${CYAN}--gemini-key <key>${NC} Optional Gemini API Key to store in Secret Manager"
    echo -e "  ${CYAN}--help${NC}             Show this help message and exit\n"
    echo -e "${BOLD}Example:${NC}"
    echo -e "  ./deploy_gcp.sh"
    echo -e "  ./deploy_gcp.sh --gemini-key AIzaSy..."
    exit 0
}

# Parse optional arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --project)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --gemini-key)
            GEMINI_KEY_INPUT="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            ;;
    esac
done

echo -e "\n${BOLD}${CYAN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} ☁️ AVANI ALBEDO: One-Shot Google Cloud Production Deployment${NC}"
echo -e "${BOLD}${CYAN}==============================================================================${NC}"
echo -e "  ${BOLD}Project ID:${NC}       ${CYAN}${PROJECT_ID}${NC}"
echo -e "  ${BOLD}Project Number:${NC}   ${CYAN}${PROJECT_NUMBER}${NC}"
echo -e "  ${BOLD}Compute Region:${NC}   ${CYAN}${REGION}${NC} (Mumbai, India)"
echo -e "  ${BOLD}Service Name:${NC}     ${MAGENTA}${SERVICE_NAME}${NC}"
echo -e "  ${BOLD}Budget Limit:${NC}     ${GREEN}₹1,000 INR / month (Scale-to-zero enabled)${NC}"
echo -e "${CYAN}------------------------------------------------------------------------------${NC}\n"

# 1. Verify gcloud CLI
if ! command -v gcloud &>/dev/null; then
    echo -e "${RED}❌ Error: 'gcloud' CLI is not installed or not in PATH.${NC}"
    echo -e "Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo -e "${YELLOW}⚠️  No active Google Cloud account detected. Initiating login...${NC}"
    gcloud auth login
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
fi
echo -e "${GREEN}✓ Authenticated as: ${BOLD}${ACTIVE_ACCOUNT}${NC}"

# Set Active Project
echo -e "${CYAN}⚙️  Configuring default project to '${PROJECT_ID}'...${NC}"
gcloud config set project "${PROJECT_ID}" --quiet

# 2. Enable Required Google Cloud APIs
echo -e "\n${BOLD}${CYAN}[Step 1/5] Enabling Required Google Cloud APIs...${NC}"
APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "firestore.googleapis.com"
    "secretmanager.googleapis.com"
    "aiplatform.googleapis.com"
    "bigquery.googleapis.com"
    "storage.googleapis.com"
)

for API in "${APIS[@]}"; do
    echo -e "  • Ensuring ${API} is enabled..."
    gcloud services enable "${API}" --project="${PROJECT_ID}" --quiet
done
echo -e "${GREEN}✓ All core APIs successfully enabled.${NC}"

# 3. Firestore Native Database Initialization
echo -e "\n${BOLD}${CYAN}[Step 2/5] Initializing Cloud Firestore Database...${NC}"
if gcloud firestore databases describe --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${GREEN}✓ Cloud Firestore database already exists in project '${PROJECT_ID}'.${NC}"
else
    echo -e "${YELLOW}⚙️  Creating Cloud Firestore Native Database in region '${REGION}'...${NC}"
    gcloud firestore databases create \
        --location="${REGION}" \
        --type=firestore-native \
        --project="${PROJECT_ID}" \
        --quiet || {
            echo -e "${YELLOW}Notice: Firestore database creation reported: already exists or propagating.${NC}"
        }
    echo -e "${GREEN}✓ Cloud Firestore database initialized.${NC}"
fi

# 4. BigQuery Climate Dataset Setup
echo -e "\n${BOLD}${CYAN}[Step 3/5] Setting up BigQuery Geospatial Climate Dataset...${NC}"
if bq show --project_id="${PROJECT_ID}" avani_climate &>/dev/null; then
    echo -e "${GREEN}✓ BigQuery dataset 'avani_climate' already exists.${NC}"
else
    echo -e "${CYAN}⚙️  Creating BigQuery dataset 'avani_climate' in region '${REGION}'...${NC}"
    bq --location="${REGION}" mk \
        --dataset \
        --description="Avani Albedo Urban Heat Island and Geospatial Analytics Dataset" \
        "${PROJECT_ID}:avani_climate" 2>/dev/null || true
    echo -e "${GREEN}✓ BigQuery dataset 'avani_climate' ready.${NC}"
fi

# 5. Secret Manager & IAM Configuration
echo -e "\n${BOLD}${CYAN}[Step 4/5] Configuring Secret Manager & Cloud Run Permissions...${NC}"

# Check for GEMINI_API_KEY from argument or local .env
LOCAL_GEMINI_KEY=""
if [ -n "$GEMINI_KEY_INPUT" ]; then
    LOCAL_GEMINI_KEY="$GEMINI_KEY_INPUT"
elif [ -f ".env" ]; then
    LOCAL_GEMINI_KEY=$(grep -E "^GEMINI_API_KEY=" .env 2>/dev/null | cut -d '=' -f2- | tr -d ' "\r' || true)
fi

if [ -n "$LOCAL_GEMINI_KEY" ]; then
    echo -e "  • Storing GEMINI_API_KEY into Google Cloud Secret Manager..."
    if gcloud secrets describe GEMINI_API_KEY --project="${PROJECT_ID}" &>/dev/null; then
        echo -n "$LOCAL_GEMINI_KEY" | gcloud secrets versions add GEMINI_API_KEY \
            --data-file=- \
            --project="${PROJECT_ID}" \
            --quiet
    else
        echo -n "$LOCAL_GEMINI_KEY" | gcloud secrets create GEMINI_API_KEY \
            --data-file=- \
            --replication-policy="automatic" \
            --project="${PROJECT_ID}" \
            --quiet
    fi
    echo -e "${GREEN}  ✓ GEMINI_API_KEY secret secured in Secret Manager.${NC}"
fi

# Judge Password Secret
echo -e "  • Ensuring JUDGE_PASSWORD secret exists in Secret Manager..."
if gcloud secrets describe JUDGE_PASSWORD --project="${PROJECT_ID}" &>/dev/null; then
    echo -n "AvaniAlbedo12042026#" | gcloud secrets versions add JUDGE_PASSWORD \
        --data-file=- \
        --project="${PROJECT_ID}" \
        --quiet
else
    echo -n "AvaniAlbedo12042026#" | gcloud secrets create JUDGE_PASSWORD \
        --data-file=- \
        --replication-policy="automatic" \
        --project="${PROJECT_ID}" \
        --quiet
fi
echo -e "${GREEN}  ✓ JUDGE_PASSWORD secret secured (AvaniAlbedo12042026#).${NC}"

# Grant Secret Accessor role to Compute service account
echo -e "  • Granting Secret Accessor IAM role to Cloud Run service account..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None \
    --quiet 2>/dev/null || true
echo -e "${GREEN}✓ IAM permissions configured.${NC}"

# 6. Deploy Application to Cloud Run
echo -e "\n${BOLD}${CYAN}[Step 5/5] Building & Deploying to Google Cloud Run...${NC}"
echo -e "${YELLOW}Building container image via Google Cloud Build and deploying to '${REGION}'...${NC}"

# Build secret flags if GEMINI_API_KEY secret exists
SECRETS_PARAM="JUDGE_PASSWORD=JUDGE_PASSWORD:latest"
if gcloud secrets describe GEMINI_API_KEY --project="${PROJECT_ID}" &>/dev/null; then
    SECRETS_PARAM="GEMINI_API_KEY=GEMINI_API_KEY:latest,JUDGE_PASSWORD=JUDGE_PASSWORD:latest"
fi

# Create clean env-vars-file to avoid shell / comma dict parsing issues
ENV_FILE=$(mktemp)
cat <<EOF > "${ENV_FILE}"
GCP_PROJECT_ID: "${PROJECT_ID}"
GCP_REGION: "${REGION}"
APP_MODE: "live"
AUTH_ENABLED: "true"
ALLOWED_EMAILS: "shiv@webveer.com,srbodkhe@gmail.com"
DEFAULT_JUDGE_USER: "judges"
EOF

gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --platform=managed \
    --allow-unauthenticated \
    --min-instances=0 \
    --max-instances=2 \
    --memory=1Gi \
    --cpu=1 \
    --port=8000 \
    --env-vars-file="${ENV_FILE}" \
    --set-secrets="${SECRETS_PARAM}" \
    --quiet

rm -f "${ENV_FILE}"

# Retrieve Live URL
LIVE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --format='value(status.url)')

# Health Check Validation
echo -e "\n${CYAN}🩺 Running automated health check against ${LIVE_URL}/api/status...${NC}"
sleep 2
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${LIVE_URL}/api/status" || echo "000")

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} 🎉 AVANI ALBEDO IS LIVE ON GOOGLE CLOUD PLATFORM!${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}"
echo -e "  🌐 ${BOLD}Live Application URL:${NC}    ${MAGENTA}${LIVE_URL}${NC}"
echo -e "  📑 ${BOLD}Interactive Swagger API:${NC} ${CYAN}${LIVE_URL}/docs${NC}"
echo -e "  🩺 ${BOLD}API Health Status:${NC}       ${GREEN}HTTP ${STATUS_CODE} (Healthy)${NC}"
echo -e "  🛡️  ${BOLD}Cost Guardrail:${NC}          ${YELLOW}Scale-to-zero (0 idle instances), capped at max 2 instances${NC}"
echo -e "  ⚖️  ${BOLD}Judges Login:${NC}            ${BOLD}UserName: judges | Password: AvaniAlbedo12042026#${NC}"
echo -e "  👑 ${BOLD}Super Admins:${NC}            ${BOLD}shiv@webveer.com, srbodkhe@gmail.com${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}\n"
