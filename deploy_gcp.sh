#!/usr/bin/env bash
# ==============================================================================
# Avani Albedo - 1-Click Production Deployment to Paid Google Cloud Platform
# Deploys: Cloud Run (Backend API & OR-Tools Solver) + Cloud Firestore + Firebase
# ==============================================================================

set -e

# ANSI Color codes for clean output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "====================================================================="
echo "  🌍 AVANI ALBEDO - 1-CLICK PAID GCP PRODUCTION DEPLOYMENT ENGINE   "
echo "  Optimizing Albedo, Cooling the Earth • AI Builder Cup Hackathon   "
echo "====================================================================="
echo -e "${NC}"

# 1. Detect or Prompt for GCP Project ID
PROJECT_ID="${1:-$GCP_PROJECT_ID}"
if [ -z "$PROJECT_ID" ]; then
    ACTIVE_PROJECT=$(gcloud config get-value project 2>/dev/null || true)
    if [ -n "$ACTIVE_PROJECT" ] && [ "$ACTIVE_PROJECT" != "(unset)" ]; then
        PROJECT_ID="$ACTIVE_PROJECT"
    fi
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Please enter your Paid Google Cloud Project ID:${NC} "
    read -r PROJECT_ID
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP Project ID is required. Exiting.${NC}"
    exit 1
fi

REGION="${GCP_REGION:-asia-south1}" # Mumbai region (or us-central1)
SERVICE_NAME="avani-albedo"

echo -e "${CYAN}Target Project ID :${NC} ${BOLD}${PROJECT_ID}${NC}"
echo -e "${CYAN}Target GCP Region :${NC} ${BOLD}${REGION}${NC}"
echo -e "${CYAN}Cloud Run Service :${NC} ${BOLD}${SERVICE_NAME}${NC}"
echo ""

# 2. Authenticate & Configure gcloud
echo -e "${YELLOW}Step 1/5: Configuring gcloud project...${NC}"
gcloud config set project "$PROJECT_ID"

# 3. Enable Required Google Cloud APIs
echo -e "${YELLOW}Step 2/5: Enabling necessary Google Cloud APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    firestore.googleapis.com \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com \
    --project "$PROJECT_ID"
echo -e "${GREEN}✓ All Cloud APIs successfully enabled.${NC}"

# 4. Check / Initialize Cloud Firestore in Native Mode
echo -e "${YELLOW}Step 3/5: Checking Cloud Firestore database...${NC}"
if ! gcloud firestore databases describe --project "$PROJECT_ID" &>/dev/null; then
    echo -e "${CYAN}Creating default Firestore database in Native mode (Location: ${REGION})...${NC}"
    gcloud firestore databases create --location="$REGION" --type=firestore-native --project "$PROJECT_ID" || true
    echo -e "${GREEN}✓ Firestore Native database initialized.${NC}"
else
    echo -e "${GREEN}✓ Firestore database is already active.${NC}"
fi

# 5. Build and Deploy Container to Cloud Run
echo -e "${YELLOW}Step 4/5: Building and deploying container to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --port 8000 \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},APP_ENV=production" \
    --project "$PROJECT_ID"

# Retrieve the live Cloud Run Service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format 'value(status.url)' --project "$PROJECT_ID")

echo ""
echo -e "${GREEN}${BOLD}=====================================================================${NC}"
echo -e "${GREEN}${BOLD}  🎉 SUCCESS: Avani Albedo Backend is LIVE on Cloud Run!            ${NC}"
echo -e "${GREEN}${BOLD}  Live URL: ${CYAN}${SERVICE_URL}${NC}"
echo -e "${GREEN}${BOLD}=====================================================================${NC}"
echo ""

# 6. Optional: Deploy Firebase Hosting Edge CDN
echo -e "${YELLOW}Step 5/5: Firebase Hosting Edge Deployment (Optional)...${NC}"
if command -v firebase &>/dev/null; then
    echo -e "${CYAN}Updating firebase.json rewrite to point to live Cloud Run service...${NC}"
    # Ensure firebase.json rewrites point to the deployed Cloud Run service
    cat <<EOF > firebase.json
{
  "hosting": {
    "public": "app/static",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "$SERVICE_NAME",
          "region": "$REGION"
        }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
EOF
    echo -e "${CYAN}Deploying Firebase Hosting...${NC}"
    firebase deploy --only hosting --project "$PROJECT_ID" || echo -e "${YELLOW}Firebase deploy skipped or requires login.${NC}"
else
    echo -e "${YELLOW}Note: 'firebase' CLI not found. You can directly access your full app on the Cloud Run URL:${NC}"
    echo -e "${CYAN}${SERVICE_URL}${NC}"
fi

echo ""
echo -e "${GREEN}${BOLD}Deployment Complete! Your paid GCP project is now hosting Avani Albedo.${NC}"
