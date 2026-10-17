# 🌿 Avani Albedo — Urban Heat Resilience Intelligence Platform

Welcome to the **Avani Albedo** Project Wiki. 

**Avani Albedo** is a planetary-scale urban heat mitigation and algorithmic resource allocation platform. It ingests multi-spectral satellite telemetry and climate reanalysis data into Google Cloud to detect urban heat islands (UHIs), evaluate heat vulnerability across demographic wards, and compute mathematically optimal cooling intervention plans using constraint optimization.

---

## ⚡ Quick Navigation

| Wiki Section | Description |
| :--- | :--- |
| 🏛️ **[[Architecture & GCP Infrastructure]]** | Cloud Run, BigQuery, Firestore, Gemini 2.0 Flash (Google AI SDK), Cloud Storage |
| 🛰️ **[[Climate Datasets & BigQuery Pipeline]]** | 8 real climate datasets, ECMWF ERA5, Landsat/Sentinel, zero-cost batch staging |
| 🧮 **[[Mathematical Optimizer & Heat Mitigation]]** | Google OR-Tools SCIP solver, albedo physics, cool roofs, tree canopy allocation |
| 🔐 **[[Security & User Management]]** | Firebase Google 1-Click Auth, Judge bypass, Firestore live persistence |
| 🏙️ **[[City Onboarding Guide]]** | Step-by-step guide to adding new municipal cities and microclimate wards |

---

## 🏆 Hackathon Highlights
- **AI Builder Cup 2026 Submission**
- **Production URL**: [https://avani-albedo-hbxrfbol2a-el.a.run.app](https://avani-albedo-hbxrfbol2a-el.a.run.app)
- **Zero-Cost GCP Architecture**: Fully utilizes Google Cloud Free Tiers across Cloud Run, Firestore, and BigQuery batch loads.
- **Microclimate Coverage**: Bengaluru, Delhi, Mumbai, Ahmedabad, Chennai, Hyderabad, Kolkata, Dubai, and Nagpur (Maharashtra).

---

## 💻 Tech Stack Overview

```
Frontend: Vanilla HTML5 / Modern CSS Glassmorphism / Vanilla JS (ES6+) / Leaflet.js
Backend:  FastAPI (Python 3.12) / Pydantic v2 / Uvicorn
Solvers:  Google OR-Tools 9.10 (SCIP Mixed-Integer Linear Programming)
AI / ML:  Google Gemini 2.0 Flash (via google-genai SDK)
GCP:      Cloud Run, Cloud Firestore Native, BigQuery, Cloud Storage (GCS)
Auth:     Firebase Authentication + JWT Bearer Tokens
```
