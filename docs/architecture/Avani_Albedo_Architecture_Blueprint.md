# Avani Albedo
## Urban Heat Action Agent: Prescriptive Climate Resilience Engine

**Team Name:** Avani Albedo  
**Slogan:** Optimizing Albedo, Cooling the Earth.

---

# Executive Summary

Avani Albedo is an agentic urban-climate decision-support platform that combines calibrated satellite earth observation composites, BigQuery Geospatial analytics, Gemini 2.0 Flash (Google AI SDK), Google Cloud Run, and Leaflet.js to transform urban heat observations into explainable, budget-aware climate interventions.

Unlike traditional GIS systems that stop at identifying heat hotspots, Avani Albedo recommends actionable interventions such as:

- Tree canopy expansion (constrained by 16 m² root zone carrying capacity)
- High-albedo cool roof deployment (zero ground-soil requirement)
- Solar shade structures
- Public hydration stations

The platform evaluates cost, physical land feasibility, vulnerable population density, and thermodynamic cooling benefits before generating an optimized municipal climate action plan.

---

# High-Level Architecture

```text
User / Municipal Urban Planner
 │
 ▼
HTML5 / Vanilla JS / Leaflet.js (CartoDB Dark Matter GIS)
 │
 ▼
Cloud Run (FastAPI Serverless Application Backend)
 │
 ├── Calibrated Satellite Composites (Landsat 8/9 & Sentinel-2)
 ├── BigQuery Geospatial Staging Pipeline
 ├── Google OR-Tools Prescriptive MILP Solver (<50ms)
 ├── Micro-Climate Thermodynamic Equations
 └── Gemini 2.0 Flash Agent (google-genai SDK)
 │
 ▼
Multi-Objective Scenario Engine (Pareto Optimal Allocation)
 │
 ▼
Municipal Climate Action Plan & Implementation Roadmap
```

---

# Technology Stack

| Layer | Technology |
|---------|------------|
| Frontend | HTML5 / Modern CSS / Vanilla JS + Leaflet.js |
| Authentication | JWT Authentication & Firebase / Google 1-Click |
| API Layer | FastAPI on Google Cloud Run |
| Agent Layer | Gemini 2.0 Flash (`google-genai` SDK) |
| Earth Telemetry | Calibrated Landsat 8/9 & Sentinel-2 Composites |
| Data Warehouse | BigQuery (Geospatial Staging Pipeline) |
| Spatial Analytics | BigQuery `GEOGRAPHY` (`ST_GEOGFROMTEXT`, `ST_INTERSECTS`) |
| Optimization | Google OR-Tools (SCIP Mixed-Integer Linear Programming) |
| Operational DB | Google Cloud Firestore (Native Mode) |
| Secrets | Google Secret Manager / Environment Vault |
| CI/CD | GitHub Actions / Google Cloud Build |
| Monitoring & Logs| Cloud Logging & Health Endpoints |

---

# End-to-End Workflow

## Step 1: User Selects Area

Planner selects:

- City
- Neighborhood
- Custom polygon

Example:

```json
{
  "city": "Bengaluru",
  "budget": 10000000,
  "objective": "maximize_public_health"
}
```

---

## Step 2: Earth Engine Analysis

Compute:

- Land Surface Temperature (LST)
- NDVI
- NDBI
- Albedo
- Heat anomalies

Data Sources:

- Landsat 8/9
- Sentinel
- OpenStreetMap
- Public infrastructure datasets

Output:

```json
{
  "cell_id":"BLR_001",
  "lst":41.2,
  "ndvi":0.14,
  "albedo":0.18
}
```

---

## Step 3: BigQuery Spatial Intelligence

Store climate cells and infrastructure.

Datasets:

```text
avani_raw
avani_climate
avani_city
avani_intelligence
avani_scenarios
avani_audit
```

Spatial joins identify:

- Schools
- Hospitals
- Transit stops
- Population exposure

---

## Step 4: Heat Vulnerability Index

Formula:

```text
HVI =
0.30 Heat Severity
+0.20 Vegetation Deficit
+0.15 Population Exposure
+0.15 Critical Infrastructure Exposure
+0.10 Built Density
+0.10 Historical Heat Persistence
```

Output:

```text
0-30 Low
30-50 Moderate
50-70 High
70-85 Severe
85-100 Critical
```

---

## Step 5: Gemini Planning Agent

Gemini acts as:

- Planner
- Orchestrator
- Explainability engine

Available tools:

```text
get_heat_hotspots()
get_cell_environment()
get_nearby_assets()
estimate_intervention_cost()
simulate_intervention()
optimize_budget()
compare_scenarios()
```

---

## Step 6: Candidate Intervention Engine

### Tree Canopy

- Tree count
- Cost
- Cooling potential
- Population benefited

### Cool Roof

- Roof area
- Albedo improvement
- Retrofit cost

### Shade Structures

- Transit stops
- Public spaces
- Schools

### Hydration Stations

- Pedestrian corridors
- Transit hubs

---

## Step 7: Optimization Engine

Cloud Run + OR-Tools

Objective:

```text
Maximize:
Cooling Benefit
× Population Impact
× Vulnerability Score
× Infrastructure Priority
```

Subject to:

```text
Total Cost <= Budget
```

---

## Step 8: Cooling Impact Simulation

Predict:

- Temperature reduction
- Population benefit
- Heat exposure reduction

Using:

- Thermodynamic Heat Island Equations (Oke 1982, Akbari et al. 2001)
- Microclimate Surface Energy Balance Models
- Gemini 2.0 Flash for Qualitative Syntheses

---

## Step 9: Scenario Planning

### Green First
Prioritizes native tree canopies within physical soil bounds (16 m²/tree).

### Albedo First
Prioritizes high-reflectance cool roofs (SRI ≥ 104, zero ground-soil requirement).

### Public Health First
Prioritizes heat mitigation surrounding schools, senior living centers, and government hospitals.

### AI Optimized Plan
Pareto-optimal allocation solved via Google OR-Tools SCIP Mixed-Integer Linear Programming.

---

## Step 10: Final Gemini Recommendation

Example:

```text
342 Trees
12 Cool Roof Projects
9 Shade Structures
4 Hydration Stations

Budget Used:
₹99.4 Lakhs

Estimated Beneficiaries:
96,000 Citizens
```

---

# Security Architecture

```text
User
 ↓
JWT Auth / Google 1-Click
 ↓
Cloud Run (FastAPI Backend)
 ↓
IAM & Secret Manager
 ↓
Google Cloud Firestore
```

Services:

- Secret Manager
- Cloud Armor / Google DDoS Mitigation
- Audit Logs
- HTTPS TLS 1.3

---

# Observability

Metrics:

- API response latency (<100ms)
- OR-Tools optimization time (<50ms)
- Gemini token usage & latency
- Scenario generation time

Tools:

- Google Cloud Logging
- Health & Status Endpoints (`/api/status`)

---

# CI/CD Pipeline

```text
GitHub (main branch)
  ↓
GitHub Actions / Cloud Build
  ↓
Automated Pytest Suite (25/25 Tests Passing)
  ↓
Artifact Registry Container Build
  ↓
Google Cloud Run Deployment (asia-south1)
```

Environments:

- Dev (Local Uvicorn / Pytest)
- Prod (Google Cloud Run Serverless)

---

# Demo Flow

1. Open city heat vulnerability map (Bengaluru, Ahmedabad, Delhi, etc.)
2. Display hotspots and 6-factor composite HVI
3. Overlay schools, hospitals, and critical infrastructure
4. Adjust municipal budget slider and choose strategic objective
5. Run Google OR-Tools Prescriptive Solver (<50ms)
6. Generate Gemini 2.0 Flash persona-adaptive action plan
7. Compare multi-objective scenarios (Pareto, Green First, Albedo First, Health First)
8. Inspect 2014-2026 decadal historical heat timelapse

---

# One-Line Pitch

Avani Albedo combines calibrated earth observation composites, BigQuery geospatial pipelines, Google OR-Tools MILP, and Gemini 2.0 Flash to convert urban heat intelligence into explainable, budget-constrained climate resilience interventions.
