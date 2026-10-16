# 🔄 Avani Albedo — System State & Resumption Handbook
> **Saved on:** October 8, 2026  
> **Repository:** `/Users/itsd-shivaji/Documents/Avani_Albedo_Dev`  
> **Git Branch:** `main` (clean working directory, pushed to GitHub remote `origin/main`)  
> **Status:** All 16 unit & integration tests passing (`16 passed in 3.8s`)

---

## ⚡ 1. How to Start the App Locally

### 🚀 Option A: 1-Step Instant Launch (Recommended)
```bash
cd /Users/itsd-shivaji/Documents/Avani_Albedo_Dev
./run.sh
```
*(This auto-activates `.venv`, checks dependencies, and launches the server with hot-reload.)*

---

### 🛠️ Option B: Step-by-Step Manual Launch
```bash
# 1. Navigate to project root
cd /Users/itsd-shivaji/Documents/Avani_Albedo_Dev

# 2. Activate Python virtual environment
source .venv/bin/activate

# 3. (Optional) Run test suite to verify health
pytest -v

# 4. Start the local server
python run.py
# (Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000)
```

---

### 🌐 Access URLs
- **Web App Dashboard:** [http://localhost:8000/](http://localhost:8000/)
- **Swagger Interactive API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Status / Health Check:** [http://localhost:8000/api/status](http://localhost:8000/api/status)

### 🔑 Demo & Admin Credentials
- **Judge / Evaluator Login:**
  - **Emails:** `srbodkhe@gmail.com`, `judge@hackathon.com`, `evaluator@ai-builder.cup`
  - **Password:** `avani2026`
- **Admin Portal Login** (Header top-right **🔒 Admin Portal**):
  - **Email:** `admin@avani.eco`
  - **Password:** `AdminPass123!`

### 🛑 To Stop Server
Press **`Ctrl + C`** in your terminal.

---

## 🧩 2. Complete Summary of What Has Been Built & Saved

### A. Dual Temperature Modes: Surface vs Ambient Air Temperature (Completed & Cross-Checked)
- **1. Surface Temperature Mode:**
  - **Source:** Landsat 8/9 Thermal Infrared Sensor (TIRS Band 10), Google Earth Engine (GEE).
  - **Measures:** Land Surface Temperature (LST) — Heat absorbed by roads, roofs, and concrete under solar flux ($\sim 950\,\text{W/m}^2$).
  - **Typical Example:** Bengaluru Surface Temperature: **~42.8°C** (hotspots like Peenya reaching 43.5°C+).
- **2. Ambient Air Temperature Mode:**
  - **Source:** Weather APIs (AccuWeather / IMD Ground Automatic Weather Stations).
  - **Measures:** Human-experienced shaded air temperature recorded in a standard 2-meter Stevenson screen.
  - **Typical Example:** Bengaluru Air Temperature: **~31.5°C**.
- **Interactive UI Toggle & Dual Comparison Showcase:**
  - Integrated into the **📈 Thermal Timeline & Forecast** tab with live toggle buttons:
    - `[🛰️ Surface Temperature Mode]` (Orange theme, LST baseline)
    - `[🌤️ Ambient Air Temperature Mode]` (Cyan theme, AccuWeather/IMD baseline)
  - Live feature comparison cards highlighting Source, Measures, and Typical Example for both modes with click-to-switch capability.
  - Dynamic Diurnal Chart (Chart.js) redraws seamlessly with corresponding curves, threshold lines, and 7-day forecast cards.
  - Ward Inspector card displays both readings side-by-side: Surface LST vs Ambient Air Temp with $\Delta +11.3^\circ\text{C}$ thermal gap.
  - Dual mode metadata exposed via API schema (`/api/temperature-timeline` returns `surface_mode` and `ambient_mode`).

### B. Cascading Geography & Multi-Currency Engine
- **Cascading Geography:** `Country` (India, UAE, United States, United Kingdom, Singapore) $\rightarrow$ `State/Province` $\rightarrow$ `City` $\rightarrow$ `Ward/District`.
- **Multi-Currency System:**
  - Real-time conversions for ₹ INR, $ USD, AED, GBP, SGD.
  - Interactive top-bar toggle: `[Dual Display ₹ / $]` vs `[Local Only]` vs `[USD Only]`.
  - Budget slider and all intervention cost cards auto-convert.

### C. Firebase Auth & Administrator Control Portal
- **Modal / Portal:** Accessible via header button.
- **Admin Controls:**
  - View real-time active users.
  - Suspend / Unsuspend user accounts.
  - Configure Gemini API Quota limits (e.g. 15,000 req/day).
  - Toggle BigQuery, Earth Engine, and Gemini live/simulation fallback flags.

### D. Historical Google Earth Timelapse (2005 – 2025 Archive)
- **20-Year Historical Analysis:**
  - Tracks temperature increase ($+2.3^\circ\text{C}$ to $+3.8^\circ\text{C}$), cumulative tree canopy loss (e.g. $-38,400$ trees), and built-up concrete surge ($+43\%$).
  - Interactive 5-step timeline scrubber with autoplay animation on the GIS map.
  - Physical data sources clearly documented (Landsat 5 TM, Landsat 7 ETM+, Landsat 8/9 OLI/TIRS, Sentinel-2).

### E. Physical Land Feasibility & Spot-Specific Phase Evaluator
- **Land Feasibility Audit:** Root-zone physical bounding (16 m² per tree) ensures trees are only recommended on open parks, road medians, and schoolyards; excess cooling demand is rerouted to high-albedo cool roofs requiring zero ground soil.
- **Spot Phase Evaluator:** Compares **Phase 1: Rapid Heat-Wave Relief**, **Phase 2: Systematic Resilience**, and **Phase 3: Long-Term Transformation** for any selected ward hotspot.
- **12-Month Heat Calendar:** Precaution preparation windows (Jan–Feb), Peak heatwave emergency windows (Mar–May), and Sapling planting windows (Jul–Sep).

### F. Avani Project Help Bot & Extensible Knowledge Base (Completed)
- **Floating Help Bot Widget:** Prominent bottom-right corner button `🤖 Avani Help Bot` with animated sparkle badge, quick-question chips, and smooth chat window.
- **App-Only Boundary Guardrail:** Responds strictly to questions about Avani Albedo application logic, algorithms, climate science, and architecture. Politely deflects off-topic queries.
- **Strict Security Guardrail (Zero Credential Leakage):** Hardened against credential extraction; strictly refuses to share API keys, secrets, passwords, or tokens under all circumstances.
- **Dedicated Future-Proof Knowledge Base:** Stored in [`app/data/help_bot_knowledge.json`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/app/data/help_bot_knowledge.json) so the team can continuously add and edit project topics and FAQs in standard JSON without modifying source code.
- **API Endpoints:** `POST /api/help-bot/chat` (AI & fallback Q&A) and `GET /api/help-bot/knowledge` (knowledge inspection).

---

## 📁 3. Key Files & Project Map

| File | Purpose |
| :--- | :--- |
| [`app/static/index.html`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/app/static/index.html) | Complete frontend layout, GIS container, tabs, admin modal, timelapse scrubber |
| [`app/static/js/app.js`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/app/static/js/app.js) | Frontend client: Leaflet map, Chart.js diurnal curves, currency engine, timeline toggle |
| [`app/data/cities_heat_data.py`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/app/data/cities_heat_data.py) | Comprehensive multi-city database, 20-year satellite records, heat calendars |
| [`app/models/schemas.py`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/app/models/schemas.py) | Pydantic data schemas for action plans, timelines, and scenarios |
| [`app/api/routes.py`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/app/api/routes.py) | FastAPI endpoints for `/api/action-plan`, `/api/cells`, `/api/temperature-timeline`, etc. |
| [`PAID_GCP_HOSTING_AND_INFRA_GUIDE.md`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/PAID_GCP_HOSTING_AND_INFRA_GUIDE.md) | Step-by-step instructions for hosting on your paid GCP project with Cloud Run |
| [`.env`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/.env) | Environment configuration with Gemini API keys, Firebase project settings, and GCP IDs |

---

## 🚀 4. Roadmap & Next Steps When You Return

When you restart and resume, here are the next high-impact tasks we can tackle:
1. **Cloud Run Deployment:** Follow [`PAID_GCP_HOSTING_AND_INFRA_GUIDE.md`](file:///Users/itsd-shivaji/Documents/Avani_Albedo_Dev/PAID_GCP_HOSTING_AND_INFRA_GUIDE.md) to deploy the app to your paid GCP project and get a public live URL.
2. **Demo Video Recording / Presentation Deck:** Prepare slides and script highlighting the hackathon themes: *Sustainability, Climate Resilience, Google Gemini 2.5 Flash on Vertex AI, and Earth Engine integration*.
3. **Live Vertex AI Tuning:** Test custom Gemini prompt engineering for localized city municipal policy briefs.

Everything is saved, committed, and safely pushed to your GitHub repository!
