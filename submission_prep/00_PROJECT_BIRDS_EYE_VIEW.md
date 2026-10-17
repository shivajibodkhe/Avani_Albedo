# 🦅 Avani Albedo — Project Bird’s-Eye View (Master Executive Summary)

> **Challenge:** Google Cloud AI Builder Cup 2026  
> **Track:** Sustainability & Social Impact  
> **Tagline:** *Optimizing Albedo, Cooling the Earth.*  
> **Project Version:** `v1.1.4` (Production Cloud Ready)  
> **Live Deployed Prototype:** [https://avani-albedo-hbxrfbol2a-el.a.run.app](https://avani-albedo-hbxrfbol2a-el.a.run.app)  
> **GitHub Repository:** [https://github.com/shivajibodkhe/Avani_Albedo](https://github.com/shivajibodkhe/Avani_Albedo)  

---

## 🎯 1. The Core Problem & The Innovation Gap

* **The Crisis:** Rapid urbanization replaces natural canopy with dark asphalt and concrete, elevating Land Surface Temperatures (LST) above **43°C to 48°C** in metropolitan corridors—over **11°C hotter** than ambient air. Extreme heat waves claim over **25,000 lives annually** across the Global South.
* **Why Conventional GIS Fails:** Google Maps, climate viewers, and traditional GIS systems are **passive observation tools**—they show where hotspots are, but cannot prescribe what to do, how much budget to spend, or where interventions will physically survive.
* **The "Ghost Tree" Planting Trap:** Cities spend crores planting saplings, but up to **70% die** because hyper-dense urban wards have **85% to 98% sealed concrete** with zero permeable root space.
* **The Avani Albedo Breakthrough:** Avani Albedo is a **prescriptive climate resilience decision engine**. It converts satellite telemetry into mathematically optimal, physically realizable municipal cooling portfolios in **under 35 milliseconds**.

---

## 🔬 2. The Algorithmic Engine & Mathematical Foundation

```
[Landsat 8/9 & Sentinel-2] ──► [6-Factor HVI Engine] ──► [Google OR-Tools MILP] ──► [Gemini 2.0 Flash] ──► [Cloud Firestore]
    (Thermal & Vegetation)        (0–100 Ward Scoring)       (<35ms SCIP Solver)       (Thermodynamic Brief)   (Scenario Archive)
```

1. **6-Factor Normalized Heat Vulnerability Index (HVI):**
   * Computes continuous ward risk (0 to 100):  
     $$\text{HVI} = 0.25(\text{LST}_{\text{norm}}) + 0.20(1 - \text{NDVI}) + 0.15(\text{NDBI}) + 0.15(\text{Pop}_{\text{norm}}) + 0.15(\text{Demo}_{\text{vuln}}) + 0.10(\text{Asset}_{\text{deficit}})$$
2. **Google OR-Tools Mixed-Integer Linear Programming (MILP):**
   * Uses the **SCIP solver** to maximize thermal cooling and population protection along the Pareto efficiency frontier subject to budget constraints $\sum (C_i \cdot x_i) \le B$.
3. **The 16 m² Root-Zone Carrying Capacity Bound:**
   * Enforces a strict physical bound: every mature tree requires $\ge 16\,\text{m}^2$ of unsealed soil.
   * When a ward's permeable soil capacity is exhausted, the solver automatically redirects remaining budget to **High-Albedo Cool Roofs (SRI $\ge 104$)**, which require **$0\,\text{m}^2$ of ground soil**, guaranteeing 100% physical survival.

---

## 🛠️ 3. The 4 Prescriptive Cooling Interventions

| # | Intervention | Cooling Impact | Soil Constraint | Unit Cost | Primary Strategic Role |
| :-: | :--- | :---: | :---: | :---: | :--- |
| **1** | **Urban Canopy & Pocket Forests** | $-2.0^\circ\text{C}$ to $-3.5^\circ\text{C}$ | $\ge 16\,\text{m}^2$ soil/tree | ₹3,500 / tree | Biophilic cooling, rainwater percolation, PM2.5 air filtration |
| **2** | **High-Albedo Cool Roofs (SRI $\ge 104$)** | $-1.8^\circ\text{C}$ to $-2.5^\circ\text{C}$ | **$0\,\text{m}^2$ (Zero Soil)** | ₹120 / $\text{m}^2$ | Industrial/commercial roofs, reflects 88% of incoming solar flux |
| **3** | **Tensile Solar Shade Canopies** | $-4.0^\circ\text{C}$ to $-6.5^\circ\text{C}$ | Minimal anchor posts | ₹85,000 / unit | Shading pedestrian transit corridors, outdoor bus terminals |
| **4** | **Smart Public Hydration Kiosks** | Direct heat-stroke relief | Water line tap | ₹150,000 / kiosk | Slashes acute heat dehydration near hospitals and markets |

---

## 🤖 4. Gemini 2.0 Flash Generative Reasoning

* **SDK:** `google-genai` SDK (`gemini-2.0-flash`) via the Gemini Developer API (Google AI).
* **Municipal Decision Personas:** Adapts action plans to 4 specific municipal stakeholders:
  1. *Municipal Commissioner* (Macro resilience ROI, budget feasibility, ESG compliance)
  2. *Chief Public Health Officer* (Heat stroke mortality mitigation, vulnerable asset protection)
  3. *Urban Infrastructure Planner* (Transit shading, cool pavement, rooftop albedo retrofit)
  4. *Disaster Management Chief* (Peak heatwave early warning, drinking water logistics)
* **3-Phase Implementation Roadmaps:**
  * **Phase 1: Rapid Relief (Weeks 1–8):** Zero-soil cool roofs on public schools, hospitals, and transit stops.
  * **Phase 2: Systematic Resilience (Months 2–6):** Tensile shade structures and chilled water kiosks.
  * **Phase 3: Long-Term Transformation (Months 6–24):** Native tree sapling planting during monsoon windows.
* **24/7 AI Project Help Bot:** Embedded on landing page and dashboard; answers scientific and algorithmic queries with strict regex guardrails preventing secret/credential leakage.

---

## 🏛️ 5. Verified Google Cloud Platform (GCP) Stack

| GCP Service | Architectural Role | Enterprise Specification |
| :--- | :--- | :--- |
| **Google Cloud Run** | Serverless Backend & Solver | Containerized FastAPI (Python 3.12, Uvicorn) in `asia-south1` (Mumbai). Autoscales 0➔10 instances, concurrency: 80, sub-50ms execution. |
| **Cloud Firestore** | Enterprise Persistence | Native Mode. Persists scenarios (`avani_scenarios`), sessions (`avani_users`), and audit records (`avani_alerts`). |
| **Firebase** | Ingress & Authentication | Global Edge CDN hosting, TLS 1.3 HTTPS, Google 1-Click OAuth + Judge/Admin RBAC. |
| **BigQuery** | Geospatial Staging Pipeline | Executes spatial SQL (`ST_GEOGFROMTEXT`, `ST_INTERSECTS`) across 8 analytical staging tables loaded via free batch loads (`bq load`). |
| **Cloud Storage (GCS)** | Multi-Spectral Raster Store | Bucket `gs://avani-albedo-climate-staging` holding GeoTIFF rasters and GeoJSON boundaries. |
| **Secret Manager** | Security & Secret Isolation | Securely injects `GEMINI_API_KEY` and `JUDGE_PASSWORD` at container runtime via `--set-secrets`. |
| **CI/CD & Testing** | Automated Cloud Delivery | GitHub Actions & Cloud Build pipeline triggering **25/25 passing automated tests** before zero-downtime deployment. |

---

## 👥 6. Official Team & Hackathon Credentials

| Detail | Official Value |
| :--- | :--- |
| **Team Name** | **Avani Albedo** |
| **Team Leader** | **Shivaji Bodkhe** (`srbodkhe@gmail.com`) |
| **Team Members** | 1. **Shivaji Bodkhe** (Leader) &bull; 2. **Niranchana K** &bull; 3. **Anusha D** &bull; 4. **Akshatha Ramachandra Prabhu** |
| **Evaluator Login** | **Username:** `judges` &bull; **Password:** `AvaniAlbedo12042026#` *(or Google 1-Click)* |
| **Super Admin Login** | `srbodkhe@gmail.com` *(Full GCP telemetry & user management)* |
| **Production URL** | `https://avani-albedo-hbxrfbol2a-el.a.run.app` |
| **Coverage** | 9 Metropolitan Cities: Bengaluru, Delhi, Mumbai, Ahmedabad, Chennai, Hyderabad, Kolkata, Dubai, and Nagpur |
