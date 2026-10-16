# 🏛️ Architecture & GCP Infrastructure

Avani Albedo uses an enterprise-grade, cost-optimized Google Cloud Platform (GCP) architecture in region `asia-south1` (Mumbai).

---

## 🏗️ High-Level System Architecture

```
[ Client Browser / UI ]
         │ (HTTPS / WebSockets)
         ▼
[ Google Cloud Run ] (FastAPI Python 3.14 container, autoscaling 0->10)
   ├── Auth Service: Firebase Google 1-Click Auth + JWT Verification
   ├── Spatial API: Heat vulnerability index (HVI), climate cells, wards
   ├── Optimizer Core: Google OR-Tools SCIP solver
   └── Copilot Service: Google Gemini 2.5 Flash
         │
         ├──► [ Cloud Firestore Native ] (Real-time user accounts, access alerts, scenario plans)
         ├──► [ Google Cloud Storage (GCS) ] (Zero-cost batch staging bucket: gs://avani-albedo-climate-staging/)
         ├──► [ Google BigQuery ] (Dataset: avani_climate, GEOGRAPHY spatial points, 8 analytical tables)
         └──► [ Google Vertex AI / GenAI SDK ] (Gemini 2.5 Flash with climate domain knowledge)
```

---

## ☁️ Google Cloud Services & Free-Tier Optimization

| GCP Service | Purpose | Cost Optimization Strategy |
| :--- | :--- | :--- |
| **Cloud Run** | Microservices API & Web UI | Min instances = 0 (scale-to-zero when idle). First 2 million requests/month free. |
| **Cloud Firestore** | Real-time user accounts, alerts, scenarios | Free Tier: 50,000 reads & 20,000 writes/day. Zero latency (<10ms). |
| **BigQuery** | Petabyte-scale climate analytics & spatial queries | Ingestion via **batch loading** (`bq load --source_format=NEWLINE_DELIMITED_JSON`) = **$0.00 ingestion cost**. |
| **Cloud Storage** | Staging raw satellite JSONs & GeoJSONs | 5GB Standard Storage free tier. |
| **Gemini 2.5 Flash** | AI Copilot for climate resilience recommendations | Free tier: 15 RPM, 1,500 RPD on Google AI Studio / Vertex AI. |

---

## 🚀 Deployment Commands

```bash
# Deploy to Google Cloud Run
./deploy_gcp.sh

# Or manual deployment:
gcloud run deploy avani-albedo \
    --source . \
    --platform managed \
    --region asia-south1 \
    --allow-unauthenticated \
    --set-env-vars="GCP_PROJECT_ID=avani-albedo,ENVIRONMENT=production"
```
