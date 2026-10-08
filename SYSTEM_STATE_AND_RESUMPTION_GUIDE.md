# 🔄 Avani Albedo — System State & Resumption Handbook
> **Saved on:** October 8, 2026  
> **Repository:** `/Users/itsd-shivaji/Documents/Avani_Albedo_Dev`  
> **Git Branch:** `main` (clean working directory, pushed to GitHub remote `origin/main`)  
> **Status:** All 16 unit & integration tests passing (`16 passed in 3.8s`)

---

## ⚡ 1. Quick-Start Guide (After System Restart)

Once your machine boots back up and cools down, open your terminal and run these commands to resume:

```bash
# 1. Navigate to project root
cd /Users/itsd-shivaji/Documents/Avani_Albedo_Dev

# 2. Activate Python virtual environment
source .venv/bin/activate

# 3. Verify all test suites
pytest -v

# 4. Start the local server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Web App URL:** [http://localhost:8000/](http://localhost:8000/)
- **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Admin Portal:** Click the **🔒 Admin Portal** button on top-right in the header, or log in with:
  - **Email:** `admin@avani.eco`
  - **Password:** `AdminPass123!`

---

## 🧩 2. Complete Summary of What Has Been Built & Saved

### A. Dual Temperature Sensor & AccuWeather Resolution (Completed)
- **Problem Solved:** Explained the physical difference between **Satellite Radiometric Land Surface Temperature (LST / Skin Temp: ~42.8°C)** from Landsat 8/9 TIRS Band 10 and **2-Meter Shaded Ambient Air Temperature ($T_{\text{air}}$: ~31.5°C)** from AccuWeather/IMD.
- **Interactive UI Toggle:** Added live switch in the **📈 Thermal Timeline & Forecast** tab:
  - `[🛰️ Surface Skin LST (Peak Heat)]` → 42.8°C baseline with high solar absorption.
  - `[🌤️ Ambient Air Temp (Weather App)]` → 31.5°C baseline matching AccuWeather, changing diurnal curves to cyan and scaling 7-day forecast cards.
- **Dynamic City Switching Fix:**
  - Fixed tab switching so selecting new cities (Bengaluru, Delhi, Phoenix, Dubai, London, Singapore) no longer kicks you out of the timeline tab.
  - Reset `selectedWardId` properly on city changes.
  - Dynamically redraws Chart.js diurnal curves for whichever city or ward is selected.

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
