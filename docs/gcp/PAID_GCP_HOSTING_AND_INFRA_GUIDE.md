# ☁️ Avani Albedo: Paid Google Cloud Platform (GCP) Hosting & Infrastructure Guide

This guide provides end-to-end infrastructure specifications, architectural blueprints, cost estimations, and automated deployment commands to host **Avani Albedo** on your paid Google Cloud account.

---

## 🏗️ 1. Cloud Architecture Overview

```
                      +------------------------------------------+
                      |         End Users & Hackathon Judges     |
                      +------------------------------------------+
                                           |
                                           v
                       +---------------------------------------+
                       |   Firebase Hosting (Edge Global CDN)  |
                       |       https://<project>.web.app       |
                       +---------------------------------------+
                                           |
                      [Reverse Proxy: /api/** -> Cloud Run]
                                           |
                                           v
                       +---------------------------------------+
                       |      Google Cloud Run (Serverless)    |
                       |   Region: asia-south1 (Mumbai) / US   |
                       |   - FastAPI High-Performance Backend  |
                       |   - Google OR-Tools SCIP MIP Solver   |
                       +---------------------------------------+
                                    |              |
           +------------------------+              +-----------------------+
           |                                                               |
           v                                                               v
+---------------------------------------+              +---------------------------------------+
|    Cloud Firestore (Native Mode)      |              |   Vertex AI / Gemini 2.5 Flash API    |
| - avani_scenarios (Plan Archives)     |              | - Spatial Reasoning & Plan Synthesis  |
| - avani_audit (Administrative Logs)   |              | - Thermodynamic Rationale Generation  |
+---------------------------------------+              +---------------------------------------+
```

---

## 💰 2. Estimated Monthly Costs on Paid GCP Project

Because Avani Albedo is built with a serverless, on-demand design, running it on your paid GCP project will cost **almost ₹0 (or less than $1/month)** due to Google Cloud's generous Free Tier:

| Service | Allocation / Usage in Avani | GCP Free Tier Allowance | Est. Cost |
| :--- | :--- | :--- | :--- |
| **Cloud Run** | 1 vCPU, 1 GiB RAM, min-instances=0 | **2 Million requests/month FREE** | **₹0.00** |
| **Cloud Firestore** | Collections: `avani_scenarios`, `avani_audit` | **50,000 document reads/day, 20,000 writes/day FREE** | **₹0.00** |
| **Firebase Hosting** | Static HTML/CSS/JS edge CDN | **10 GB storage, 360 MB/day transfer FREE** | **₹0.00** |
| **Vertex AI / Gemini** | Gemini 2.5 Flash calls (~200 calls/day during demo) | Google AI Studio free tier / Vertex credits ($300 trial credits) | **₹0.00** |
| **Total Est. Cost** | — | — | **< ₹50 ($0.50)** |

---

## ⚡ 3. Quickstart: 1-Command Automated Deployment

We have included a production-grade automated deployment script [`deploy_gcp.sh`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/deploy_gcp.sh).

Open your local terminal and run:

```bash
# Make script executable and run with your GCP Project ID
chmod +x deploy_gcp.sh
./deploy_gcp.sh YOUR_PAID_PROJECT_ID
```

The script will automatically:
1. Configure `gcloud` to your target project.
2. Enable all required APIs (`run.googleapis.com`, `cloudbuild.googleapis.com`, `firestore.googleapis.com`, `aiplatform.googleapis.com`).
3. Initialize Cloud Firestore in Native mode.
4. Containerize the application and deploy it to **Cloud Run** with auto-scaling (0 to 10 instances).
5. Output your **Live Cloud Run URL** (e.g., `https://avani-albedo-xxxxx-el.a.run.app`).
6. Deploy the frontend to **Firebase Hosting** with automatic reverse-proxy routing to Cloud Run APIs.

---

## 📋 4. Step-by-Step Manual Deployment (Alternative)

If you prefer to execute commands step-by-step:

### Step 4.1: Login and Set Project
```bash
gcloud auth login
gcloud config set project YOUR_PAID_PROJECT_ID
```

### Step 4.2: Enable Google Cloud APIs
```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    firestore.googleapis.com \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com
```

### Step 4.3: Create Cloud Firestore Database (Native Mode)
```bash
gcloud firestore databases create --location=asia-south1 --type=firestore-native
```

### Step 4.4: Deploy to Cloud Run
```bash
gcloud run deploy avani-albedo \
    --source . \
    --platform managed \
    --region asia-south1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --port 8000 \
    --set-env-vars "GCP_PROJECT_ID=YOUR_PAID_PROJECT_ID,APP_ENV=production"
```

### Step 4.5: Deploy Firebase Hosting (Edge Distribution)
```bash
firebase login
firebase deploy --only hosting
```

---

## 🔑 5. Setting up Secrets & API Keys

### Option A: Via the In-App Super Admin Portal (Easiest)
1. Open your live app in the browser.
2. Click **⚙️ Admin** in the top-right corner.
3. Sign in as Super Admin (`srbodkhe@gmail.com`).
4. Paste your **Gemini API Key** and your **GCP Project ID**.
5. Click **💾 Save Cloud Configuration**. The engine updates immediately without requiring a restart!

### Option B: Via Cloud Run Environment Variables
```bash
gcloud run services update avani-albedo \
    --region asia-south1 \
    --update-env-vars "GEMINI_API_KEY=YOUR_GEMINI_API_KEY,GCP_PROJECT_ID=YOUR_PAID_PROJECT_ID"
```

---

## 🔍 6. Monitoring & Health Verification

Once deployed, verify live health:

- **Health Check Endpoint:**
  ```
  GET https://YOUR_CLOUD_RUN_URL/api/status
  ```
  Expected Response:
  ```json
  {
    "app_name": "Avani Albedo",
    "version": "1.0.0",
    "mode": "Production Cloud Ready",
    "gcp_project": "YOUR_PROJECT_ID",
    "gemini_connected": true,
    "gemini_model": "Vertex AI Gemini 2.5 Flash",
    "earth_engine_status": "Ready",
    "bigquery_status": "Ready",
    "firestore_status": "Ready (Live)",
    "cells_loaded": 12
  }
  ```

- **Cloud Run Logs:**
  View live logs in Google Cloud Console under **Cloud Run > avani-albedo > Logs**, or via terminal:
  ```bash
  gcloud run services logs tail avani-albedo --region asia-south1
  ```
