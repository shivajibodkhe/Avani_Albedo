# AI Builder Cup — 3 to 4 Minute Video Demonstration Script

> **Mandatory Rule Check:**  
> *Participants must submit a 3 to 4 minute video demonstration of their solution. The video must clearly demonstrate the working functionality of the submitted solution. Videos exceeding the prescribed duration may attract a penalty or may result in the submission not progressing further in the evaluation process.*  
> **Target Video Runtime:** **3 Minutes 30 Seconds (210 seconds)** — strictly inside the 3-to-4 minute window.

---

## ⏱️ Video Demonstration Timeline Overview

| Timestamp | Segment Name | What to Show on Screen | Key Talking Points |
| :---: | :--- | :--- | :--- |
| **0:00 – 0:30** | Problem & Mission | Title Slide $\rightarrow$ Landing Gateway | Urban Heat Islands, LST vs Air Temp, Avani Albedo mission |
| **0:30 – 1:05** | Auth & Interactive GIS Map | 1-Click Login $\rightarrow$ Dashboard & HVI Wards | 6-factor HVI, Peenya hotspot, satellite telemetry |
| **1:05 – 1:45** | Prescriptive Optimizer | Budget Slider (₹1 Crore) $\rightarrow$ Run Agent | OR-Tools SCIP solver in <50ms, 4 interventions, soil bound |
| **1:45 – 2:20** | Gemini Planning Agent | Action Plan Tab $\rightarrow$ 3 Phases | Gemini 2.0 Flash executive brief, thermodynamic rationale |
| **2:20 – 2:50** | Scenarios & Decadal Timelapse | 4-Scenario Comparison $\rightarrow$ Timelapse Tab | AI Pareto vs Green/Albedo First, 2014-2026 tree loss |
| **2:50 – 3:15** | AI Help Bot & Firestore | Floating Help Bot chat $\rightarrow$ Admin Portal | Real-time Gemini 2.0 Flash Help Bot, Firestore persistence |
| **3:15 – 3:30** | Tech Stack & Wrap-Up | Architecture Slide $\rightarrow$ Live Link & GitHub | Google Cloud Run, Gemini, Firestore, Firebase summary |

---

## 🎬 Detailed Second-by-Second Video Script

### **[0:00 – 0:30] Segment 1: The Problem & The Mission**
* **On Screen:** Start on the landing gateway (`https://avani-albedo-hbxrfbol2a-el.a.run.app`). Show the title **"AVANI ALBEDO v1.1.1"** and subtitle *"Optimizing Albedo, Cooling the Earth"*.
* **Voiceover:**
  > *"Hello judges! Welcome to Avani Albedo, built for the Google Cloud AI Builder Cup under the Sustainability & Social Impact track.*  
  > *Rapid urbanization has replaced natural soil and canopy with dark concrete, causing Land Surface Temperatures in cities like Bengaluru to spike above 42°C—over 10 degrees hotter than ambient air. While conventional GIS tools merely display heat maps without answers, Avani Albedo is a prescriptive climate resilience engine that tells city commissioners exactly what interventions to fund, where to deploy them, and how much cooling they will achieve."*

---

### **[0:30 – 1:05] Segment 2: 1-Click Auth & The 6-Factor HVI Map**
* **On Screen:** Click **"Judges One-Click Access"** (or sign in with Google). The dashboard smoothly reveals the interactive dark-mode GIS map with color-coded ward polygons. Click on the **Peenya Industrial Area** polygon to open its popup.
* **Voiceover:**
  > *"Logging in securely via Firebase Authentication, we enter the live city dashboard. Here, Bengaluru is mapped across 12 climate cells.*  
  > *Our backend leverages calibrated Landsat/Sentinel-2 composites to compute a normalized 6-factor Heat Vulnerability Index—combining Land Surface Temperature, vegetation deficit, concrete density, demographics, and proximity to hospitals and schools. Notice Peenya: marked critical red with an HVI of 80+ and 42.8°C surface temperature."*

---

### **[1:05 – 1:45] Segment 3: Google OR-Tools Prescriptive Optimization**
* **On Screen:** In the left sidebar, show the **Budget Slider** set to **₹1 Crore (₹10,000,000)**. Keep **AI Pareto-Optimized** selected and choose the **Municipal Commissioner** persona. Click the prominent button: **"🚀 Run Avani Climate Agent"**.
* **Voiceover:**
  > *"Now, let's prescribe action. We allocate a municipal budget of ₹1 Crore. In under 35 milliseconds, Google OR-Tools running on Google Cloud Run solves a Mixed-Integer Linear Program.*  
  > *It balances 4 core physical interventions: Urban Trees, Zero-Soil Cool Roofs, Tensile Shade Structures, and Smart Hydration Kiosks. Crucially, our engine enforces a physical 16 square meter root space constraint per tree. In hyper-dense concrete wards like Peenya, it automatically redirects funding to Zero-Soil High-Albedo Cool Roofs with an SRI above 85%, guaranteeing that every prescribed intervention can physically survive."*

---

### **[1:45 – 2:20] Segment 4: Gemini 2.0 Flash Planning Agent**
* **On Screen:** The **Action Plan** tab appears. Highlight the glowing badge: **"Gemini 2.0 Flash"** and **"OR-Tools SCIP • 28ms"**. Scroll through the Executive Summary and the 3 implementation phases.
* **Voiceover:**
  > *"Immediately, Gemini 2.0 Flash powered by the Google GenAI SDK translates the mathematical allocations into an executive municipal plan.*  
  > *Gemini provides thermodynamic justifications, ranking interventions by cooling efficiency per rupee. It breaks the deployment into three actionable phases: Phase 1 Rapid Relief targeting cool roofs on public schools and transit hubs, Phase 2 Systematic Resilience deploying tensile shade and water kiosks, and Phase 3 Long-Term Transformation for native tree planting during monsoon seasons."*

---

### **[2:20 – 2:50] Segment 5: Multi-Scenario Comparison & Decadal Earth Timelapse**
* **On Screen:** Click the **"4-Scenario Comparison"** tab to show the side-by-side cards. Then click the **"Decadal Timelapse"** tab and press **Play** on the 2014–2026 animation slider.
* **Voiceover:**
  > *"Municipal leaders can compare strategic policies with one click: AI Pareto-Optimized vs Green First, Albedo First, and Public Health First.*  
  > *Under the Decadal Timelapse tab, we visualize 12 years of historical Earth observations from 2014 to 2026, showing the real loss of 49,200 mature canopy trees as concrete expanded from 62% to 89%, and verifying our restorative replenishment targets."*

---

### **[2:50 – 3:15] Segment 6: Real-Time AI Help Bot & Google Cloud Firestore**
* **On Screen:** Click the floating **Help Bot** icon in the bottom-right corner. Type: *"What are the 4 climate interventions and unit costs?"*. Show the instant structured response. Then click the **Admin** shield icon in the top header.
* **Voiceover:**
  > *"For evaluators and city planners, our floating 24/7 AI Help Bot answers any scientific or mathematical question directly using Gemini 2.0 Flash.*  
  > *Every generated action plan and administrative audit log is automatically persisted in Google Cloud Firestore Native mode under the avani_scenarios collection, ensuring full continuity across cloud sessions."*

---

### **[3:15 – 3:30] Segment 7: Google Cloud Architecture & Conclusion**
* **On Screen:** Briefly show the **GCP Stack & Impact** modal highlighting Google Cloud Run, Gemini 2.0 Flash, Firestore, BigQuery, and Firebase. Show the live URL and GitHub repo link.
* **Voiceover:**
  > *"Avani Albedo is live, fully automated via CI/CD, and 100% powered by the Google Cloud ecosystem—Cloud Run, Gemini API, Firestore, BigQuery staging, and Firebase. Thank you for evaluating Avani Albedo: Optimizing Albedo, Cooling the Earth!"*

---

## 💡 Top 5 Recording Tips to Ensure Maximum Score

1. **Keep it between 3:00 and 3:45:** Never exceed 4 minutes! The sweet spot is 3:20 to 3:35.
2. **Pre-load the tabs:** Have the browser tab open with Google Cloud Run (`https://avani-albedo-hbxrfbol2a-el.a.run.app`) so there are zero loading delays.
3. **Use 1080p 60fps:** Record in 1920x1080 resolution with clear microphone audio.
4. **Show Live Clicks:** Do NOT show only PowerPoint slides! Judges want to see the live, working prototype in action (clicking wards, adjusting budget slider, running Gemini action plan).
5. **Upload to YouTube or Google Drive:** Ensure the link permissions are set to **"Anyone with the link can view"**!
