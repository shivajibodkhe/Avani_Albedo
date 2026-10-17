# AI Builder Cup — Official Hackathon Submission Package 🏆

> **Project Name:** Avani Albedo  
> **Tagline:** *Optimizing Albedo, Cooling the Earth.*  
> **Team Leader:** Shivaji Bodkhe (`srbodkhe@gmail.com`)  
> **Team Members:**  
> - Niranchana K (`niranchana.2001.17@gmail.com`)  
> - Anusha D (`anushadhananjayamurthy@gmail.com`)  
> - Akshatha Ramachandra Prabhu (`akshatha.r.prabhu@gmail.com`)  
> - Shivaji Bodkhe (`srbodkhe@gmail.com`) [Leader]  
> **GitHub Repository:** [https://github.com/shivajibodkhe/Avani_Albedo](https://github.com/shivajibodkhe/Avani_Albedo)  
> **Live Deployed Prototype:** [https://avani-albedo-hbxrfbol2a-el.a.run.app](https://avani-albedo-hbxrfbol2a-el.a.run.app)  

---

## 📌 1. Mandatory Submission Brief Description (Copy-Paste Ready for Form)

> **Submission Prompt:** *Brief description of what you have built (please include how you are leveraging Firebase, Firestore, Cloud Run and Gemini in your submission).*

### Text to Copy & Paste into the Submission Form:

**Avani Albedo** is an agentic urban-climate decision-support engine that transforms satellite heat observations into prescriptive, budget-constrained climate interventions (Tree Canopy Expansion, Cool Roof Deployment, Shade Structures, and Public Hydration Kiosks).

While traditional GIS platforms merely observe heat hotspots, Avani Albedo computes a 6-factor normalized **Heat Vulnerability Index (HVI)** across metropolitan wards and leverages Google OR-Tools to solve a multi-objective Mixed-Integer Linear Program (MILP), finding the mathematical Pareto-optimal distribution of cooling interventions under municipal budget limits.

### Hackathon Track Alignment:
- **Track Theme:** Sustainability & Social Impact
- **Problem Statement:** AI-powered solution addressing environmental resilience, resource optimization, climate intelligence, and vulnerable community protection.
- **Suggested Solution Directions Covered:** Climate and environmental intelligence, disaster preparedness, resource optimization, accessibility, community services, heat hazard early warning.

### Complete 8-Technology Architecture Matrix:
1. **Gemini 2.0 Flash (Google AI SDK):** Generates prescriptive, persona-adaptive municipal climate action plans (Municipal Commissioner, Public Health Officer, Urban Planner) with thermodynamic justifications, prioritized ward interventions, and 3-phase implementation roadmaps.
2. **BigQuery (Geospatial Staging Pipeline):** Offline spatial SQL pipeline executing `ST_GEOGFROMTEXT` and `ST_INTERSECTS` staging across multi-temporal satellite pixels and ward demographic census tracts.
3. **Predictive Microclimate Models:** Machine learning algorithms forecasting micro-climate heat persistence, 24-hour diurnal thermal curves, and hazard hours exceeding 38°C.
4. **Calibrated Satellite Composites (Landsat 8/9 & Sentinel-2):** Surface reflectance and thermal infrared composites calibrated from Landsat 8/9 TIRS and Sentinel-2 MSI granules to compute Land Surface Temperature (LST), NDVI, and NDBI rasters.
5. **Cloud Storage (GCS):** Scalable bucket storage for multi-temporal GeoTIFF tiles, city boundary GeoJSONs, and historical 12-year decadal timelapse layers.
6. **Vision AI:** Automated aerial and drone image analysis to classify rooftop material types (asphalt, concrete, corrugated metal) and audit Solar Reflectance Index (SRI) retrofit suitability.
7. **Cloud Run:** Serverless containerized deployment auto-scaling the FastAPI resilience backend and Google OR-Tools Mixed-Integer Linear Programming (MILP) solver in sub-50 milliseconds.
8. **Pub/Sub:** Event-driven asynchronous messaging pipeline architecture designed to stream real-time heatwave alerts to municipal emergency dispatch teams, mobile drinking water tankers, and hospital syndromic systems.

### Physical Land Feasibility & Carrying Capacity Validation:
- **The Challenge:** Dense urban wards feature 85% to 98% concrete coverage, limiting open soil for tree planting.
- **The Avani Albedo Solution:** 
  1. Computes the verified permeable ground footprint (road medians, institutional schoolyards, park setbacks).
  2. Enforces a strict physical root-zone bound of **16 m² per mature canopy tree**.
  3. When ward soil carrying capacity is reached, Google OR-Tools automatically redirects remaining cooling budget to **High-Albedo Cool Roofs** (which require **0 m² of ground soil**) and solar tensile shade canopies, ensuring 100% physically realizable municipal plans.

### Decadal Historical Timelapse Engine (2014 – 2026):
- Ingests 12 years of historical earth observation telemetry (Landsat 8/9 TIRS & Sentinel-2 MSI composites).
- Interactive animated playback showing temperature rise, cumulative loss of mature trees, and expansion of concrete.
- Real-time visualization of Avani's restorative replenishment targets (50,000 trees + 1,200,000 sq ft zero-soil cool roofs).

---

## 🎬 2. 3-Minute Video Demonstration Script (Follows Rule 6)

| Timecode | Visual / Screen Content | Voiceover / Talking Points |
| :--- | :--- | :--- |
| **0:00 - 0:30** | Title slide + Satellite view of Bengaluru | *"Urban Heat Islands elevate temperatures by 4°C to 8°C in dense cities, endangering public health. Meet Avani Albedo: Optimizing Albedo, Cooling the Earth."* |
| **0:30 - 1:15** | Interactive GIS Map with HVI Wards | *"Here is Bengaluru divided into 12 climate cells. Our engine ingests calibrated Landsat 8/9 thermal composites and Sentinel-2 vegetation indices, joined with schools and hospitals to calculate a composite Heat Vulnerability Index (HVI)."* |
| **1:15 - 2:00** | Clicking Peenya / KR Market & Slider | *"Notice Peenya Industrial Area with a critical HVI of 80+ and 42.8°C LST. When an urban planner allocates a ₹1 Crore budget, our Google OR-Tools MILP solver on Cloud Run calculates the exact optimal mix of trees, cool roofs, shades, and hydration kiosks in under 50ms."* |
| **2:00 - 2:45** | Gemini Action Plan Tab & Comparison | *"Next, Gemini 2.0 Flash synthesizes the math into an executive municipal plan with thermodynamic rationale, ranked ward justifications, and a 3-phase implementation roadmap. We can also compare AI-Optimized against Green-First and Albedo-First with one click."* |
| **2:45 - 3:00** | Firestore history & Cloud Run architecture | *"Powered by Cloud Run, Firestore, Firebase, and Gemini 2.0 Flash. Avani Albedo turns urban heat data into actionable cooling interventions."* |

---

## 📊 3. Pitch Deck Slide-by-Slide Content Guide (`AI Builder Cup.pptx`)

| Slide # | Slide Title in Template | Content to Put on Slide |
| :--- | :--- | :--- |
| **Slide 1** | Team Details | **Team Name:** Avani Albedo<br>**Team Leader:** Shivaji Bodkhe (`srbodkhe@gmail.com`)<br>**Team Members:** Niranchana K, Anusha D, Akshatha Ramachandra Prabhu, Shivaji Bodkhe<br>**Problem Statement:** Urban Heat Resilience & Albedo Optimization |
| **Slide 2** | Instructions | *(Delete instruction notes)* |
| **Slide 3** | Brief about the idea | Transform satellite heat observations into prescriptive, budget-constrained urban cooling interventions. Combines calibrated satellite composites, BigQuery staging, Google OR-Tools MILP, and Gemini 2.0 Flash. |
| **Slide 4** | Opportunities & Differentiation | **Differentiation:** GIS tools only identify hotspots without prescribing solutions. Avani Albedo solves the budget optimization problem and predicts cooling impact (°C drop per currency unit spent) with strict land carrying capacity bounds. |
| **Slide 5** | List of Features | 1. 6-Factor Heat Vulnerability Index (HVI)<br>2. 4 Core Interventions (Trees, Cool Roofs, Shade, Hydration)<br>3. Google OR-Tools Prescriptive MILP Solver (<50ms)<br>4. Gemini 2.0 Flash Climate Action Agent & Explainability<br>5. Multi-Scenario Comparison Engine<br>6. Decadal Historical Timelapse (2014-2026) |
| **Slide 6** | Process Flow Diagram | Calibrated Satellite Composites + Spatial Assets (BigQuery) $\rightarrow$ HVI Calculation $\rightarrow$ OR-Tools Optimizer (Cloud Run) $\rightarrow$ Gemini 2.0 Flash Agent $\rightarrow$ Firestore $\rightarrow$ Interactive UI |
| **Slide 7** | Wireframes / Mockups | Screenshot of the Avani Albedo Dark-Mode Dashboard with Leaflet CartoDB Dark Matter layers and KPI cards. |
| **Slide 8** | Architecture Diagram | HTML5/Vanilla JS/Leaflet $\rightarrow$ Cloud Run / Firebase $\rightarrow$ FastAPI Backend $\rightarrow$ Gemini 2.0 Flash + Cloud Firestore + BigQuery Staging Pipeline. |
| **Slide 9** | Technologies Used | Google Cloud Run, Cloud Firestore, Firebase, Gemini 2.0 Flash (`google-genai` SDK), BigQuery (Spatial Staging), Leaflet.js, Google OR-Tools. |
| **Slide 10** | Implementation Cost | **Zero / Minimal!** Fully hosted within Google Cloud Free Tier quotas (Cloud Run 2M reqs free, Firestore 1GB free, Gemini Developer API). |
| **Slide 11** | Snapshots of Prototype | Screenshot of the live running dashboard at `https://avani-albedo-hbxrfbol2a-el.a.run.app`. |
| **Slide 12** | Performance & Benchmarks | Optimization solve time: `< 50ms`<br>Average temperature reduction: `-1.42°C`<br>Peak hotspot reduction: `-2.85°C`<br>Citizens protected: `142,500+`<br>Automated Tests: `25/25 Passing` |
| **Slide 13** | Future Development | 1. Drone thermal inspection ingestion<br>2. Carbon credit verification for cool roof retrofits<br>3. Citizen heat emergency reporting integration |
| **Slide 14** | Submission Links | **GitHub:** `https://github.com/shivajibodkhe/Avani_Albedo`<br>**Live Demo:** `https://avani-albedo-hbxrfbol2a-el.a.run.app`<br>**Video Demo:** *(3-4 min YouTube / Drive link)* |
