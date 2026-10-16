# AI Builder Cup — Mandatory Submission Brief Description

> **Instructions for Participant:**  
> Copy and paste the text in **Section 1** directly into the **"Brief description"** text box of the official AI Builder Cup submission form.  
> It explicitly addresses the mandatory prompt requirement: *"please include how you are leveraging Firebase, Firestore, Cloud Run and Gemini in your submission"*.

---

## 📌 Section 1: Official Submission Brief (Copy-Paste Ready)

### Project Name:
**Avani Albedo: Prescriptive Urban Climate Resilience & Albedo Optimization Engine**

### Tagline:
*Optimizing Albedo, Cooling the Earth.*

### Track & Theme:
**Sustainability & Social Impact** (Environmental resilience, urban climate intelligence, vulnerable community protection, and disaster preparedness).

---

### Description Text:

**Avani Albedo** is an agentic, planetary-scale urban climate resilience platform that transforms multi-spectral satellite heat observations into mathematically optimal, budget-constrained municipal cooling interventions (**Tree Canopy Planting, Zero-Soil High-Albedo Cool Roofs, Tensile Shade Structures, and Public Hydration Kiosks**).

While conventional GIS dashboards merely show passive heat maps, Avani Albedo computes a normalized 6-factor **Heat Vulnerability Index (HVI)** across metropolitan wards and leverages **Google OR-Tools** to solve a Mixed-Integer Linear Program (MILP), identifying the Pareto-optimal allocation of physical interventions within municipal budget limits in **under 50 milliseconds**.

### ☁️ How We Leverage Core Google Cloud Technologies:

1. **Vertex AI & Gemini 2.0 Flash:**
   - **Municipal Planning Agent:** Translates complex Pareto optimization solutions into executive, explainable climate action plans with thermodynamic justifications, prioritized ward allocations, and 3-phase implementation roadmaps tailored to specific decision-makers (*Municipal Commissioner, Chief Public Health Officer, Urban Infrastructure Planner, Disaster Management Chief*).
   - **24/7 AI Project Help Bot:** A domain-bound floating AI assistant embedded on the dashboard and landing gateway, answering scientific, algorithmic, and engineering questions with strict security guardrails preventing credential disclosure.

2. **Google Cloud Run:**
   - Powers the containerized, serverless FastAPI resilience backend and Google OR-Tools SCIP solver in `asia-south1`.
   - Delivers sub-50ms execution, dynamic auto-scaling from 0 to 10 instances with near-zero idle cost, and automated zero-downtime CI/CD deployment via GitHub Actions.

3. **Google Cloud Firestore (Native Mode):**
   - Automatically persists all municipal scenario plans in the `avani_scenarios` collection with full audit history.
   - Manages persistent judge/admin authentication records (`avani_users`), real-time access alerts (`avani_alerts`), and dynamic configuration states (`avani_config/runtime`) across container lifecycles.

4. **Firebase (Hosting & Authentication):**
   - **1-Click Google Sign-In & Auth:** Secure role-based identity management integrating Firebase Authentication with seamless evaluator access.
   - **Static Asset Delivery:** Lightning-fast global CDN delivery for the dark-mode interactive GIS interface.

5. **Complementary Google Geospatial & Optimization Stack:**
   - **Google Earth Engine (GEE):** Planetary radiometric calibration of Landsat 8/9 TIRS Band 10 (Land Surface Temperature) and Sentinel-2 MSI 10m (NDVI vegetation & NDBI built-up indices).
   - **BigQuery Geospatial:** High-performance spatial clustering (`ST_DWithin`, `ST_Intersects`) cross-referencing thermal hotspots with critical social assets (schools, hospitals, transit hubs).
   - **Physical Land Feasibility Engine:** Enforces a strict 16 m² root space constraint per tree, redirecting excess thermal load to Zero-Soil Cool Roofs (SRI ≥ 85%) in hyper-dense wards (>90% sealed concrete) to eliminate "ghost tree" planting failures.

---

## 📌 Section 2: Quick Reference Submission Details

| Form Field | Value to Enter |
| :--- | :--- |
| **Team Name** | Avani Albedo |
| **Team Leader** | **Shivaji Bodkhe** (`srbodkhe@gmail.com`) |
| **Team Members** | 1. **Shivaji Bodkhe** (Leader) — `srbodkhe@gmail.com`<br>2. **Niranchana K** — `niranchana.2001.17@gmail.com`<br>3. **Anusha D** — `anushadhananjayamurthy@gmail.com`<br>4. **Akshatha Ramachandra Prabhu** — `akshatha.r.prabhu@gmail.com` |
| **Project Title** | Avani Albedo — Prescriptive Climate Resilience Engine |
| **Track** | Sustainability & Social Impact |
| **GitHub Repository** | `https://github.com/shivajibodkhe/Avani_Albedo` |
| **Live Deployed Prototype Link** | `https://avani-albedo-hbxrfbol2a-el.a.run.app` |
| **Judge Access Credentials** | Email/Username: `judges` &bull; Password: `AvaniAlbedo12042026#` *(or Google 1-Click)* |
| **Key Technologies** | Gemini 2.0 Flash, Google Cloud Run, Cloud Firestore, Firebase, Google Earth Engine, BigQuery, Google OR-Tools |

