# ☁️ Avani Albedo — Google Cloud Platform Project Details

> **Project Name:** AVANI ALBEDO  
> **Project ID:** `avani-albedo`  
> **Project Number:** `615055398519`  
> **GCP Console Dashboard:** [https://console.cloud.google.com/home/dashboard?project=avani-albedo](https://console.cloud.google.com/home/dashboard?project=avani-albedo)  
> **Compute Region:** `asia-south1` (Mumbai, India)  
> **Allocated Monthly Budget:** ₹1,000 INR / month  

---

## 💰 Budget & Cost Guardrails (₹1,000 INR / Month)

To guarantee you never exceed your ₹1,000 monthly budget, our infrastructure uses Google Cloud's **scale-to-zero** and Free Tier allowances:

| Service | Configuration for Zero Waste | Cost Impact |
| :--- | :--- | :--- |
| **Cloud Run** | `--min-instances 0 --max-instances 2 --memory 512Mi --cpu 1` | Scale to zero when idle. Free tier includes first 2M requests/mo. |
| **Cloud Secret Manager** | Store production API keys and judge passwords | First **6 active secret versions** & 10,000 operations/mo are **100% FREE**. |
| **Cloud Firestore** | Native mode in `asia-south1` | First 1 GB storage & 50,000 reads/day are **FREE**. |
| **BigQuery** | Spatial queries (`avani_climate` dataset) | First 1 TB query analysis/mo is **FREE**. |
| **Artifact Registry** | Container image registry (`avani-repo`) | Pennies per GB for lightweight Docker images (< ₹10/mo). |

---

## 🔐 Google Cloud Secret Manager Integration

### Why Use Secret Manager?
Instead of hardcoding keys in `.env` files or Docker containers, Secret Manager securely encrypts and version-controls API keys. Cloud Run mounts them automatically into the app environment at boot.

### 1. Store a Secret in Secret Manager
Run these commands from your terminal:

```bash
# Store Gemini API Key
echo -n "YOUR_GEMINI_API_KEY_HERE" | gcloud secrets create GEMINI_API_KEY \
    --data-file=- \
    --project=avani-albedo \
    --replication-policy="automatic"

# Store Judge Access Password
echo -n "YOUR_SECURE_JUDGE_PASSWORD" | gcloud secrets create JUDGE_PASSWORD \
    --data-file=- \
    --project=avani-albedo \
    --replication-policy="automatic"
```

### 2. Update an Existing Secret Version
```bash
echo -n "NEW_SECRET_VALUE" | gcloud secrets versions add GEMINI_API_KEY \
    --data-file=- \
    --project=avani-albedo
```

### 3. Grant Cloud Run Permission to Read Secrets
```bash
# Get your Cloud Run default service account
PROJECT_NUMBER=615055398519
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant Secret Manager Secret Accessor role
gcloud projects add-iam-policy-binding avani-albedo \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
```

### 4. Deploy Cloud Run with Secrets Automatically Injected
```bash
gcloud run deploy avani-albedo \
    --project=avani-albedo \
    --region=asia-south1 \
    --image=asia-south1-docker.pkg.dev/avani-albedo/avani-repo/avani-albedo:latest \
    --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest,JUDGE_PASSWORD=JUDGE_PASSWORD:latest"
```

---

## ⚙️ Active Google Cloud APIs for `avani-albedo`

The following required APIs are already enabled:
- ✅ `secretmanager.googleapis.com` (Secret Manager)
- ✅ `bigquery.googleapis.com` (BigQuery Geospatial Analysis)
- ✅ `datastore.googleapis.com` (Firestore / Datastore)
- ✅ `storage.googleapis.com` (Google Cloud Storage)
- ✅ `logging.googleapis.com` & `monitoring.googleapis.com` (Cloud Operations)
- ✅ `run.googleapis.com` (Cloud Run)
- ✅ `cloudbuild.googleapis.com` (Cloud Build)
- ✅ `artifactregistry.googleapis.com` (Container Registry)
- ✅ `firebase.googleapis.com` (Firebase Management)
- ✅ `identitytoolkit.googleapis.com` (Firebase Authentication / Identity Platform)

---

## 🔥 Firebase Project & Web App Configuration

> **Firebase Console URL:** [https://console.firebase.google.com/project/avani-albedo/overview](https://console.firebase.google.com/project/avani-albedo/overview)

```json
{
  "projectId": "avani-albedo",
  "appId": "1:615055398519:web:f6c09d29e5bb2982d6d872",
  "storageBucket": "avani-albedo.firebasestorage.app",
  "apiKey": "AIzaSyDrRVQqwPRA8vGdpHgzZlDNgwqN4XzxeNc",
  "authDomain": "avani-albedo.firebaseapp.com",
  "messagingSenderId": "615055398519",
  "projectNumber": "615055398519"
}
```

---

## 🪣 Google Cloud Storage (GCS)
- **Staging Bucket:** `gs://avani-albedo-climate-staging/`
- **Location:** `asia-south1` (Mumbai)
- **Storage Class:** Standard (< ₹1 / month)
- **Staging Directory:** `gs://avani-albedo-climate-staging/staging/`
- **Purpose:** Receives high-fidelity JSONL batches for **zero-cost batch loading** into BigQuery.

---

## 📊 Google BigQuery Production Dataset
- **Dataset ID:** `avani-albedo.avani_climate`
- **Data Location:** `asia-south1`
- **Live Tables (Verified):**
  1. `urban_heat_cells` (59 rows with `GEOGRAPHY` spatial points)
  2. `realtime_microclimate_telemetry` (59 rows of live ERA5/NOAA Heat Index telemetry)
  3. `historical_heatwave_observations` (56 verified summer peak records from ECMWF ERA5)
  4. `twenty_year_climate_trends` (65 rows of satellite radiometric time series)
  5. `ward_vulnerability_index` (13 rows across all supported cities)
  6. `heat_action_interventions` (6 prescriptive interventions)
  7. `prescriptive_scenarios` (3 OR-Tools mathematical optimization runs)
  8. `scientific_data_lineage` (3 peer-reviewed calibration standards)

---

## 🚀 Live Cloud Run Production Deployment
- **Production URL:** [https://avani-albedo-hbxrfbol2a-el.a.run.app](https://avani-albedo-hbxrfbol2a-el.a.run.app)
- **Container Registry:** `asia-south1-docker.pkg.dev/avani-albedo/avani-repo/avani-albedo:latest`
- **Region:** `asia-south1`
- **Security:** Full FastAPI Swagger `/docs` and API endpoints protected with Google Identity Platform / Firebase Auth.