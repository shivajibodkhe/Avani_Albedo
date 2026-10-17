# Avani Albedo — Deployed Prototype & Judge Evaluation Guide

> **Official Competition Rule Compliance:**  
> *"Participants must provide a valid and accessible link to a deployed, working prototype. The prototype must remain functional throughout the evaluation process. If the application, APIs, integrations, or any other deployment-related components are unavailable or non-functional during evaluation, no additional consideration, retries, or allowances will be provided. The submission will be evaluated based on its functionality at the time of evaluation."*

---

## 🌐 1. Live Deployment Endpoints

| Environment | URL | Status | Region |
| :--- | :--- | :--- | :--- |
| **Production Prototype (Cloud Run)** | **`https://avani-albedo-hbxrfbol2a-el.a.run.app`** | 🟢 Live (HTTP 200) | `asia-south1` (Mumbai) |
| **Public API Health Probe** | `https://avani-albedo-hbxrfbol2a-el.a.run.app/api/status` | 🟢 Live (`"status":"ok"`) | Global |
| **OpenAPI / Swagger Documentation** | `https://avani-albedo-hbxrfbol2a-el.a.run.app/docs` | 🟢 Interactive Docs | Global |
| **GitHub Open-Source Repository** | `https://github.com/shivajibodkhe/Avani_Albedo` | 🟢 Public | Global |

---

## 🔑 2. Judge Access & Evaluation Credentials

To ensure a completely friction-free evaluation experience, the platform supports two login methods:

### Option A: Dedicated Judge Credentials (Instant Access)
* **Login URL:** `https://avani-albedo-hbxrfbol2a-el.a.run.app`
* **Username / Email:** `judges`
* **Password:** `AvaniAlbedo12042026#`
* *Role:* Evaluator / Municipal Executive (Pre-configured with full administrative rights to run optimizations, generate Gemini action plans, and export scenarios).

### Option B: 1-Click Google Sign-In (Firebase Authentication)
* Simply click the **"Continue with Google"** button on the login screen.
* Any standard Google / Gmail account is automatically authenticated and granted evaluator access.

### Option C: Super Admin Access
* **Email:** `srbodkhe@gmail.com` (Team Leader)
* *Role:* Super Admin with live GCP telemetry monitoring and scenario oversight.

---

## ⏱️ 3. Rapid 3-Minute Judge Evaluation Walkthrough

Follow these sequential steps to evaluate all core innovations within 3 minutes:

### Step 1: Landing Page & Public Help Bot (0:00 - 0:30)
1. Open `https://avani-albedo-hbxrfbol2a-el.a.run.app`.
2. Notice the live system health indicators: **Active Ward**, **Mean Surface Temp**, and **Google Cloud Run Status**.
3. Click the **Floating AI Assistant Bot** (bottom right corner).
4. Ask: *"How does Avani Albedo optimize urban cooling?"*
5. Witness instantaneous, domain-grounded responses powered by **Gemini 2.0 Flash**.

### Step 2: Authentication & Ward Telemetry Exploration (0:30 - 1:15)
1. Enter username `judges` and password `AvaniAlbedo12042026#`, then click **Sign In**.
2. On the dark-mode GIS workspace, toggle between satellite telemetry layers in the top toolbar:
   - **LST Heat Map:** Landsat 8/9 Thermal Infrared Radiance (identifying thermal hotspots like Dharavi at 42.1°C).
   - **NDVI Vegetation:** Sentinel-2 MSI 10m green canopy density.
   - **NDBI Built-Up:** Impervious concrete and corrugated metal roof surface indices.
   - **HVI Heat Vulnerability Index:** 6-factor composite socioeconomic and environmental vulnerability score.
3. Select different wards from the dropdown (e.g., **Dharavi / Ward G-North**, **Kurla / Ward L**, **Bandra West / Ward H-West**).

### Step 3: Google OR-Tools Prescriptive Optimization (1:15 - 2:00)
1. In the left-hand **Control Panel**, adjust the **Municipal Budget Slider** (e.g., set to ₹1.5 Crore / 15,000,000 INR).
2. Select an **Optimization Strategy**:
   - `AI Pareto Optimal` (Balanced thermal reduction & public health ROI)
   - `Green First` (Maximized tree planting subject to 16 m² root space constraints)
   - `Albedo First` (Zero-soil high-reflectivity cool roofs SRI ≥ 85%)
   - `Public Health First` (Hydration stations and shaded transit canopies)
3. Click **"Run Optimization Engine"**.
4. **Result:** In **under 50 milliseconds**, Google OR-Tools solves the Mixed-Integer Linear Program (MILP), rendering:
   - Specific counts: Number of Trees, Cool Roof Area (m²), Tensile Shades, and Hydration Kiosks.
   - Thermodynamic impact: Average temperature reduction (e.g., `-2.8°C`), surface albedo gain (`+0.19`), and population protected.
   - Spatial distribution points overlaid dynamically on the interactive map.

### Step 4: Gemini 2.0 Flash (Google AI) Executive Action Plan (2:00 - 2:45)
1. Under **Strategic Personas**, select an executive audience:
   - *Municipal Commissioner*
   - *Chief Public Health Officer*
   - *Urban Infrastructure Planner*
   - *Disaster Management Chief*
2. Click **"Generate AI Action Plan"**.
3. **Result:** Gemini 2.0 Flash synthesizes the OR-Tools optimization solution into an executive briefing featuring:
   - Thermodynamic justifications with Ward-level LST citations.
   - Budget expenditure breakdown with exact cost allocations.
   - Phased 30-60-90 day municipal procurement and installation milestones.

### Step 5: Scenario Persistence & Multi-Format Export (2:45 - 3:00)
1. Click **"Save Scenario"** — the plan is automatically stored in **Google Cloud Firestore** under `avani_scenarios`.
2. Click **"Export Plan"** to download the comprehensive scenario in **JSON**, **CSV**, or a styled **Printable PDF Summary**.

---

## 🏗️ 4. Google Cloud Production Architecture & Reliability Guarantees

To ensure 100% availability throughout the competition evaluation lifecycle, Avani Albedo is built with enterprise cloud redundancy:

```
[Evaluator Browser / Mobile]
            │
            ▼ HTTPS / TLS 1.3
[Google Cloud Armor & CDN]
            │
            ▼
[Google Cloud Run (asia-south1: Mumbai)]
   ├── Container Revision: avani-albedo-00016-zt2
   ├── Auto-Scaling: Serverless (0 to 10 instances, concurrency: 80)
   ├── Memory: 1 GiB | CPU: 1 vCPU
   ├── Secrets: Google Secret Manager (GEMINI_API_KEY mounted securely)
   │
   ├── Google OR-Tools (SCIP / MILP Solver) ── Sub-50ms deterministic execution
   │
   ├── Gemini 2.0 Flash Client (Google GenAI SDK) ── Exponential backoff retry logic
   │
   └── Google Cloud Firestore (Native Mode)
         ├── avani_scenarios (Scenario plans & audit logs)
         ├── avani_users (Judge and admin sessions)
         ├── avani_alerts (Real-time heat alerts)
         └── avani_config/runtime (Dynamic system configuration)
```

### High-Availability Safeguards:
1. **Zero Secret Leakage:** All API keys are stored in **Google Cloud Secret Manager** and injected into the Cloud Run container runtime environment without being exposed in static client JavaScript or GitHub commits.
2. **Session Persistence:** Evaluator login sessions are backed by both server-side JSON and Cloud Firestore session stores to prevent unexpected logouts during container cold-starts.
3. **Fallback Offline Optimization:** If external satellite API feeds experience upstream latency, the engine seamlessly switches to pre-cached, ground-truthed radiometric datasets for Mumbai wards without throwing errors to the judge.
4. **Permissive CORS & Mobile Responsive:** Works cleanly across Google Chrome, Safari, Firefox, Edge, and mobile tablet viewports.

---

## 🛠️ 5. Troubleshooting & Fallback Instructions for Judges

If you encounter any unexpected network or corporate proxy behavior during evaluation:

* **Clearing Cache / Incognito:** Open `https://avani-albedo-hbxrfbol2a-el.a.run.app` in an **Incognito / Private Browsing window**.
* **Direct Health Check:** Visit `https://avani-albedo-hbxrfbol2a-el.a.run.app/api/status` to confirm the backend is responding with `{"status":"ok"}`.
* **Direct Optimization API Test:** The OpenAPI UI is accessible at `https://avani-albedo-hbxrfbol2a-el.a.run.app/docs#/default/optimize_api_optimize_post` allowing direct interactive testing of the mathematical solver.
* **Emergency Technical Support Contact:**
  - Team Leader: Shivaji Bodkhe (`srbodkhe@gmail.com`)
  - Response time during evaluation: < 15 minutes.
