# Avani Albedo — Comprehensive GCP & Tools Developer Guide 🛠️

> **Project:** Avani Albedo (Urban Heat Action Agent)  
> **Challenge:** AI Builder Cup Hackathon  
> **Target Technologies:** Firebase, Firestore, Cloud Run, Vertex AI / Gemini, BigQuery, Google Earth Engine, Google OR-Tools  
> **Repository:** [https://github.com/shivajibodkhe/Avani_Albedo](https://github.com/shivajibodkhe/Avani_Albedo)

---

## 📑 Table of Contents
1. [Architecture & Technology Stack Overview](#1-architecture--technology-stack-overview)
2. [Prerequisites & Free Tier Eligibility](#2-prerequisites--free-tier-eligibility)
3. [GCP Project Setup & Authentication](#3-gcp-project-setup--authentication)
4. [Enabling Required Google Cloud APIs](#4-enabling-required-google-cloud-apis)
5. [Firestore Database Configuration](#5-firestore-database-configuration)
6. [Vertex AI & Gemini API Setup](#6-vertex-ai--gemini-api-setup)
7. [Google Earth Engine (GEE) Configuration](#7-google-earth-engine-gee-configuration)
8. [Deploying Backend to Google Cloud Run](#8-deploying-backend-to-google-cloud-run)
9. [Deploying Frontend to Firebase Hosting](#9-deploying-frontend-to-firebase-hosting)
10. [Local Development & Testing](#10-local-development--testing)
11. [Troubleshooting & FAQ](#11-troubleshooting--faq)

---

## 1. Architecture & Technology Stack Overview

Avani Albedo is built with a cohesive Google Cloud native stack:

| Component | Technology | Role in Avani Albedo |
| :--- | :--- | :--- |
| **Frontend** | Vanilla JS / Leaflet / HTML5 | High-performance, zero-bloat GIS dashboard with satellite & thermal layers. |
| **API & Optimizer** | FastAPI + Python + Google OR-Tools | Serves REST endpoints and solves Mixed-Integer Linear Programs (MIP) in <50ms. |
| **Container Hosting** | **Google Cloud Run** | Fully managed serverless container hosting for the FastAPI & OR-Tools engine. |
| **Operational Database** | **Google Cloud Firestore** | Stores generated climate action plans, ward allocations, and audit logs. |
| **Web Hosting & Auth** | **Firebase Hosting & Auth** | CDN edge caching, custom domain, and secure administrative authentication. |
| **AI Planning Agent** | **Vertex AI / Gemini 2.5 Flash** | Generates explainable executive briefings, physical rationales, and roadmaps. |
| **Spatial Analytics** | **BigQuery (GEOGRAPHY)** | Stores urban grid cells, ward boundaries, and critical infrastructure assets. |
| **Earth Observation** | **Google Earth Engine (GEE)** | Computes Land Surface Temp (Landsat 8/9), NDVI, NDBI, and Albedo composites. |

---

## 2. Prerequisites & Free Tier Eligibility

Everything required for this prototype can be configured on Google Cloud's **Free Tier / Free Credits**:
- **Cloud Run:** Free 2 million requests/month, 360,000 GB-seconds memory.
- **Firestore:** Free 1 GB stored data, 50,000 reads/day, 20,000 writes/day.
- **Firebase Hosting:** Free 10 GB storage, 360 MB/day data transfer.
- **Gemini:** 100% Free via Google AI Studio API Key (`aistudio.google.com/apikey`).
- **BigQuery:** Free 10 GB storage/month, 1 TB query analysis/month.
- **Earth Engine:** Free for developers, researchers, and non-commercial projects.

---

## 3. GCP Project Setup & Authentication

### Step 3.1: Log into Google Cloud via Terminal
```bash
gcloud auth login
gcloud auth application-default login
```
*A browser window will open. Sign in with your Google account.*

### Step 3.2: Set Your Active Project
If you have an existing project (e.g., `genai-2026`):
```bash
gcloud config set project YOUR_PROJECT_ID
```
Or create a new dedicated project:
```bash
gcloud projects create avani-albedo-resilience --name="Avani Albedo"
gcloud config set project avani-albedo-resilience
```

### Step 3.3: Set Default Region
```bash
gcloud config set run/region asia-south1
```

---

## 4. Enabling Required Google Cloud APIs

Run this single command in your terminal to enable all necessary GCP services:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  bigquery.googleapis.com \
  earthengine.googleapis.com \
  secretmanager.googleapis.com
```

### Verification:
```bash
gcloud services list --enabled | grep -E "run|firestore|aiplatform|earthengine"
```

---

## 5. Firestore Database Configuration

Avani Albedo uses **Cloud Firestore** in Native Mode to store:
- `avani_scenarios`: Historical optimization results, budget distributions, and KPI metrics.
- `avani_audit`: Municipal compliance and change logs.

### Step 5.1: Create Firestore Database
In the [Google Cloud Console](https://console.cloud.google.com/firestore):
1. Navigate to **Firestore** > **Databases**.
2. Click **Create Database**.
3. Select **Firestore Native mode** (Recommended).
4. Choose Location: `asia-south1` (Mumbai) or your preferred region.
5. Click **Create**.

*Or via gcloud CLI:*
```bash
gcloud firestore databases create --location=asia-south1 --type=firestore-native
```

### Step 5.2: Security Rules (`firestore.rules`)
The project includes pre-configured [firestore.rules](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/firestore.rules):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /avani_scenarios/{scenarioId} {
      allow read, write: if true;
    }
    match /avani_audit/{auditId} {
      allow read, write: if true;
    }
  }
}
```

---

## 6. Vertex AI & Gemini API Setup

You have two seamless options for powering the Gemini Climate Resilience Agent:

### Option A: Free Google AI Studio API Key (Fastest & 100% Free)
1. Go to [Google AI Studio (aistudio.google.com/apikey)](https://aistudio.google.com/apikey).
2. Click **Create API Key** and select your project.
3. Open your local `.env` file:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   ```
4. Save the file. The server automatically uses Gemini 2.5 Flash!

### Option B: Vertex AI Service Account (For Enterprise GCP Deployment)
1. In Cloud Console, go to **IAM & Admin** > **Service Accounts**.
2. Click **Create Service Account** (Name: `avani-ai-runner`).
3. Grant the role: `Vertex AI User` (`roles/aiplatform.user`).
4. Generate and download the JSON key.
5. Set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`.

---

## 7. Google Earth Engine (GEE) Configuration

1. Visit [signup.earthengine.google.com](https://signup.earthengine.google.com).
2. Sign up with your Google account for **Noncommercial / Academic / Developer** use.
3. Link your Cloud Project (`YOUR_PROJECT_ID`).
4. In your local `.env`:
   ```env
   USE_EARTH_ENGINE_LIVE=true
   ```
*(Note: If you leave `USE_EARTH_ENGINE_LIVE=false`, Avani Albedo automatically uses its calibrated 30m Landsat 8/9 composite dataset with zero errors!)*

---

## 8. Deploying Backend to Google Cloud Run

Google Cloud Run hosts the containerized FastAPI server, OR-Tools optimizer, and Gemini orchestration layer.

### One-Command Deployment (Simplest):
Run directly from the root of this project:
```bash
gcloud run deploy avani-albedo \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=YOUR_PROJECT_ID,APP_MODE=live"
```

Cloud Run will automatically:
1. Package the code using [Dockerfile](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/Dockerfile).
2. Build the container image using Cloud Build.
3. Deploy to a secure, HTTPS-enabled serverless URL (e.g., `https://avani-albedo-xxxxx-el.a.run.app`).

### Passing Secrets securely (Optional):
```bash
gcloud run services update avani-albedo \
  --region asia-south1 \
  --set-env-vars "GEMINI_API_KEY=YOUR_KEY"
```

---

## 9. Deploying Frontend to Firebase Hosting

You can connect **Firebase Hosting** to serve the static frontend and reverse-proxy API calls directly to Cloud Run:

### Step 9.1: Install Firebase CLI
```bash
npm install -g firebase-tools
firebase login
```

### Step 9.2: Connect Project
```bash
firebase use --add YOUR_PROJECT_ID
```

### Step 9.3: Deploy
```bash
firebase deploy --only hosting
```
Your application will be live at: `https://YOUR_PROJECT_ID.web.app`!

---

## 10. Local Development & Testing

### Running Locally:
```bash
# Option 1: Automated 1-step script (Recommended)
./run.sh

# Option 2: Direct Python launch
source .venv/bin/activate
python run.py
```

### Accessing the Local Services:
- **UI Dashboard:** `http://localhost:8000`
- **Swagger Documentation:** `http://localhost:8000/docs`
- **API Status / Health Check:** `http://localhost:8000/api/status`

### Demo & Admin Credentials:
- **Judge / Demo Login:** Email `srbodkhe@gmail.com` / Password `avani2026`
- **Admin Portal:** Email `admin@avani.eco` / Password `AdminPass123!`

### Running Automated Test Suite:
```bash
source .venv/bin/activate
pytest -v
```
All 16 unit & integration tests will execute in `< 5 seconds`.

### Stopping the Local Server:
Press `Ctrl + C` in your terminal.

---

## 11. Troubleshooting & FAQ

| Symptom | Probable Cause | Fix |
| :--- | :--- | :--- |
| `gcloud run deploy` fails with permission error | Cloud Build API or Artifact Registry not enabled | Run `gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com` |
| `Reauthentication required` in terminal | Google CLI auth token expired | Run `gcloud auth login` and complete browser sign-in |
| Firestore writes fail in local test | No active GCP credentials locally | Avani Albedo automatically buffers data locally in memory so no crashes occur. Run `gcloud auth application-default login` to enable live writes. |
| Port 8000 already allocated | Another local process on 8000 | Run `PORT=8080 python run.py` |
