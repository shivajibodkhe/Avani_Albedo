# Avani Albedo 🌍
## Urban Heat Action Agent: Prescriptive Climate Resilience Engine

> **Team Name:** Avani Albedo  
> **Slogan:** *Optimizing Albedo, Cooling the Earth.*  
> **Repository:** [https://github.com/shivajibodkhe/Avani_Albedo](https://github.com/shivajibodkhe/Avani_Albedo)  
> **Author:** Shivaji Bodkhe (`srbodkhe@gmail.com`)

---

## 📌 Executive Summary

Urban Heat Islands (UHI) disproportionately impact dense metropolitan centers, driving localized temperatures up by 4°C to 8°C above baseline. Traditional GIS platforms only map hotspots without prescribing actionable, budget-constrained solutions.

**Avani Albedo** is an agentic urban-climate decision-support engine that combines:
- **Satellite Multi-Spectral Intelligence:** Landsat 8/9 Thermal Infrared (LST), Sentinel-2 (NDVI, NDBI), and surface albedo reflectance.
- **BigQuery Geospatial Analytics:** Exposure modeling across critical urban assets (schools, hospitals, transit terminals, population density).
- **Prescriptive Optimization (Google OR-Tools):** Mixed-Integer Linear Programming (MIP) that determines the mathematical Pareto-optimal distribution of 4 core climate interventions under budget constraints.
- **Vertex AI / Gemini 2.0 Flash:** Explainable AI planning agent generating municipal-grade climate action plans, implementation roadmaps, and thermodynamic rationale.

---

## 🏗️ High-Level Architecture

```text
User / Municipal Urban Planner
 │
 ▼
Interactive GIS Geospatial Dashboard (Dark-mode, Leaflet / Google Maps)
 │
 ▼
FastAPI Gateway & Geospatial Engine
 │
 ├── 1. Google Earth Engine (Landsat 8/9 LST + Sentinel-2 Composites)
 ├── 2. Heat Vulnerability Index (HVI) Engine (6-Factor Normalized Model)
 ├── 3. Google OR-Tools MIP Solver (SCIP Optimization Engine)
 └── 4. Vertex AI / Gemini 2.5 Agent (Prescriptive Briefing & Roadmap)
 │
 ▼
Exportable Climate Action Plan (PDF / JSON / Printable Briefing)
```

---

## 🚀 Quickstart Guide

### Option 1: Automatic One-Line Launch (macOS / Linux)
```bash
./run.sh
```
This script automatically sets up the Python virtual environment, installs dependencies, and launches the server.

### Option 2: Manual Setup
```bash
# 1. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Launch application
python run.py
```

Open your browser at:
- **Interactive UI Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ⚙️ Configuration & Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Key | Description | Default | Free / Paid |
| :--- | :--- | :--- | :--- |
| `APP_MODE` | Runtime mode (`auto`, `live`, or `simulation`) | `auto` | Free |
| `GEMINI_API_KEY` | Google AI Studio Gemini API Key | `""` (Uses expert fallback if empty) | **100% Free** |
| `GCP_PROJECT_ID` | Google Cloud Project ID | `genai-2026` | Free tier eligible |
| `GCP_REGION` | Compute region | `asia-south1` | Free |
| `USE_EARTH_ENGINE_LIVE` | Connect live to GEE API | `false` (Uses calibrated composite) | Free academic |
| `PORT` | Local web port | `8000` | Local |

> **Note on Zero-Error Fallback:** If `GEMINI_API_KEY` is not provided, the platform automatically switches to its deterministic, rule-based Prescriptive Resilience Engine. You can test and demo the complete platform without waiting for API keys!

---

## ☁️ Google Cloud & Permissions Setup (When Ready to Deploy)

To enable live Google Cloud services on your GCP Project:

### 1. Enable Required GCP APIs
```bash
gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  run.googleapis.com \
  earthengine.googleapis.com
```

### 2. IAM Roles Required
If running through a Service Account or developer Google account:
- `roles/aiplatform.user` (Vertex AI Gemini invocation)
- `roles/bigquery.dataEditor` & `roles/bigquery.jobUser` (Spatial analytics)
- `roles/run.developer` (Cloud Run container hosting)

### 3. Local CLI Authentication
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

---

## 🧮 Mathematical Formulations

### 1. Heat Vulnerability Index (HVI)
```text
HVI = 
  0.30 × Heat Severity (LST & Anomaly)
+ 0.20 × Vegetation Deficit (1.0 - NDVI)
+ 0.15 × Population Exposure
+ 0.15 × Critical Infrastructure Exposure (Hospitals × 3 + Schools × 2 + Transit × 1.5)
+ 0.10 × Built Density (NDBI / Impervious surface fraction)
+ 0.10 × Historical Heat Persistence (Days exceeding 38°C)
```
- **Scale:**
  - `0 - 30`: Low
  - `30 - 50`: Moderate
  - `50 - 70`: High
  - `70 - 85`: Severe
  - `85 - 100`: Critical

### 2. Prescriptive Multi-Objective Optimization (OR-Tools)
Maximize total weighted resilience impact:
$$\max \sum_{i \in \text{Wards}} \left( \text{CoolingBenefit}_i \times \text{PopWeight}_i \times \text{HVI}_i^{1.5} \times \text{InfraWeight}_i \right)$$

Subject to:
$$\sum_{i} \left( x_{\text{trees}, i} \cdot C_{\text{tree}} + x_{\text{roof}, i} \cdot C_{\text{roof}} + x_{\text{shade}, i} \cdot C_{\text{shade}} + x_{\text{hyd}, i} \cdot C_{\text{hyd}} \right) \le \text{Budget}$$

And physical ward constraints:
$$0 \le x_{\text{trees}, i} \le \text{MaxTrees}_i, \quad 0 \le x_{\text{roof}, i} \le \text{MaxRoofArea}_i$$

---

## 🧪 Testing & Validation

The codebase includes full automated tests for the HVI engine, OR-Tools optimization algorithms, and FastAPI endpoints:

```bash
source .venv/bin/activate
pytest -v
```

Output:
```text
tests/test_api.py::test_api_status PASSED
tests/test_api.py::test_api_cells PASSED
tests/test_api.py::test_api_optimize PASSED
tests/test_api.py::test_api_action_plan PASSED
tests/test_api.py::test_api_compare PASSED
tests/test_hvi.py::test_hvi_calculation_and_categories PASSED
tests/test_optimizer.py::test_optimizer_budget_and_scenarios PASSED
======================== 7 passed in 0.26s =========================
```

---

## 🛠️ Troubleshooting FAQ

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Port 8000 already in use** | Another process is bound to port 8000 | Set `PORT=8080` in `.env` or run `PORT=8080 python run.py` |
| **ModuleNotFoundError: No module named 'app'** | `PYTHONPATH` not recognized | Run via `python run.py` or `./run.sh`, which automatically adds the project root to `PYTHONPATH`. |
| **Gemini API rate limit or no key** | No `GEMINI_API_KEY` set | The platform gracefully activates its built-in fallback engine with realistic expert briefings. |
| **Google Earth Engine permission denied** | Account not registered on GEE | Free registration at [earthengine.google.com](https://earthengine.google.com). Leave `USE_EARTH_ENGINE_LIVE=false` to use high-res pre-calibrated Landsat composites. |

---

## 🌟 Hackathon Demo Flow

1. **Open Bengaluru Heat Map:** Observe 12 climate wards with color-coded HVI severity (e.g. Peenya at 80+ vs Jayanagar at 35).
2. **Inspect Vulnerabilities:** Click on *Peenya Industrial* or *KR Market* to view surface temperature (42.8°C), vegetation deficit, and hospital counts.
3. **Adjust Budget Slider:** Slide budget between ₹10 Lakhs and ₹5 Crore to see dynamic scaling.
4. **Choose Policy Objective:**
   - **AI Pareto-Optimized:** Balanced Knapsack solution.
   - **Green First:** 70% Urban Canopy expansion.
   - **Albedo First:** 65% Cool Roof retrofit focus.
   - **Public Health First:** Prioritize school/hospital transit corridors.
5. **Run Avani Climate Agent:** Observe instant solver execution (<50ms) and generated Gemini briefing.
6. **Compare Scenarios:** Click *"Compare All 4 Scenarios"* for side-by-side trade-off analysis.
7. **Export Plan:** Click *"Print / Export Action Plan"* for an audit-ready municipal presentation.
