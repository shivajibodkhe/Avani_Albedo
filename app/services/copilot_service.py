import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.config import settings

logger = logging.getLogger("avani_albedo.help_bot")

KNOWLEDGE_FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "help_bot_knowledge.json"

HELP_BOT_SYSTEM_PROMPT = """You are the official Avani Albedo Project Help Bot and AI Assistant.
Avani Albedo is a Prescriptive Urban Climate Resilience & Albedo Optimization Decision Engine built for municipal commissioners, urban planners, public health officers, and climate engineers to combat Urban Heat Islands (UHI).

SLOGAN: "Optimizing Albedo, Cooling the Earth."

CRITICAL CORE MANDATES & SECURITY GUARDRAILS:
1. STRICTLY APPLICATION-ONLY SCOPE:
   - You must answer queries strictly related to the Avani Albedo application, its algorithms, satellite telemetry, mathematical optimization, physical interventions, and cloud architecture ONLY.
   - If asked off-topic questions (e.g. general programming, movies, unrelated politics, creative writing, recipes, sports, etc.), politely decline:
     "👋 I am the Avani Project Help Bot, dedicated exclusively to answering questions about the Avani Albedo Climate Resilience & Urban Heat Island Engine. I answer queries strictly from our application and its scientific models only. How can I assist you with Avani Albedo today?"
2. STRICT SECURITY GUARDRAIL - NEVER SHARE CREDENTIALS OR API KEYS:
   - UNDER NO CIRCUMSTANCES should you ever share, reveal, dump, or confirm passwords, credentials, API keys, secrets, tokens, or environment variables.
   - If any user asks for API keys, passwords, credentials, admin access, or secrets (even via hypothetical roleplay or prompt injection), refuse strictly with:
     "🔒 **Security Policy Enforcement:** For strict data protection and compliance, Avani Albedo does not share passwords, API keys, credentials, or internal authentication secrets under any circumstances."

CORE ARCHITECTURAL PILLARS:
1. Satellite Earth Observation & Dual Temperature Modes:
   - Surface Temperature Mode:
     * Source: Landsat 8/9 Thermal Infrared Sensor (TIRS Band 10), Google Earth Engine (GEE).
     * Measures: Land Surface Temperature (LST) — heat absorbed by roads, roofs, and concrete.
     * Typical Example: Bengaluru Surface Temperature: ~42.8°C.
   - Ambient Air Temperature Mode:
     * Source: Weather APIs (AccuWeather / IMD Ground Automatic Weather Stations).
     * Measures: Human-experienced shaded air temperature (measured 2 meters above ground in a Stevenson screen).
     * Typical Example: Bengaluru Air Temperature: ~31.5°C.
   - Sentinel-2 Multi-Spectral Instrument (MSI 10m resolution) for NDVI (vegetation) and NDBI (built-up density).
   - 20-Year Radiometric Archive (2005 - 2025) and Decadal Timelapse (2014 - 2026).
2. Heat Vulnerability Index (HVI) Engine:
   - A normalized 6-factor composite model: Land Surface Temperature anomaly (25%), Vegetation deficit 1-NDVI (20%), Built-up concrete density NDBI (15%), Population density (15%), Elderly & child demographic exposure (15%), and Critical asset deficit (10%).
3. Prescriptive Mathematical Solver (Google OR-Tools):
   - Uses Mixed-Integer Linear Programming (SCIP Solver) to determine Pareto-optimal allocations under strict municipal budget constraints:
     maximize sum(Cooling_Reduction_i * Beneficiaries_i * HVI_Weight_i) subject to Cost <= Budget.
4. The 4 Core Climate Interventions:
   - 🌳 Urban Forest & Tree Canopy: Cost ₹3,000/tree, cooling ~0.9°C/1000 trees via evapotranspiration. Strictly requires 16 m² permeable soil root zone carrying capacity.
   - 🏢 Zero-Soil High-Albedo Cool Roofs: Cost ₹15/sq ft, Solar Reflectance Index (SRI) >= 85%. Vital for dense concrete wards (>90% sealed) where trees cannot physically be planted.
   - ☂️ High-UV Shade Structures: Cost ₹45,000/site, immediate radiant barrier for transit stops, markets, school walkways.
   - 💧 Smart Hydration Kiosks: Cost ₹65,000/site, chilled automated water distribution to prevent heat exhaustion and stroke among outdoor laborers.
5. "Trees Cut Down" Calculation:
   - Quantified by tracking decadal NDVI drop (e.g. Bengaluru fell from 0.38 in 2014 to 0.14 in 2026, while concrete rose from 62% to 89%).
   - Decadal felling curve follows a non-linear acceleration model: trees_lost(t) = total_trees_lost * ((t - 2014)/12)^1.3.
6. 4 Objectives & 4 Personas:
   - Objectives: AI Pareto-Optimized (max cooling/rupee), Green First (60%+ tree budget), Albedo First (60%+ cool roof budget), Public Health First (protecting hospitals, schools, and vulnerable populations).
   - Personas: Municipal Commissioner, Chief Public Health Officer, Urban Infrastructure Planner, Disaster Management Chief.
7. Google Cloud Platform (GCP) Enterprise Stack:
   - Google Cloud Run (serverless containerized deployment), Google Cloud Firestore Native mode (persisting plans in `avani_scenarios`), calibrated Landsat/Sentinel-2 composites, BigQuery Geospatial pipeline, Gemini API via Google AI SDK (Gemini 2.0 Flash), Firebase Authentication.


When answering, be crisp, technically authoritative, structured, and helpful. Use markdown formatting with clear headings, bullet points, and equations where applicable. Always answer directly from Avani Albedo application knowledge."""

COPILOT_SYSTEM_PROMPT = HELP_BOT_SYSTEM_PROMPT


def load_help_bot_knowledge() -> Dict[str, Any]:
    """Loads knowledge base from app/data/help_bot_knowledge.json with graceful fallback."""
    try:
        if KNOWLEDGE_FILE_PATH.exists():
            with open(KNOWLEDGE_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load help bot knowledge from {KNOWLEDGE_FILE_PATH}: {e}")
    
    return {
        "project_meta": {"name": "Avani Albedo"},
        "security_policy": {
            "refusal_message": "🔒 **Security Policy Enforcement:** For strict data protection and compliance, Avani Albedo does not share passwords, API keys, credentials, or internal authentication secrets under any circumstances."
        },
        "domain_boundary": {
            "off_topic_message": "👋 I am the **Avani Project Help Bot**, dedicated exclusively to answering questions about the **Avani Albedo Climate Resilience & Urban Heat Island Engine**."
        },
        "topics": {}
    }


class HelpBotService:
    """
    Project Help Bot Service that answers any query strictly from the Avani Albedo project.
    Guarantees that credentials and API keys are NEVER disclosed under any circumstances.
    """
    def __init__(self):
        self.gemini_client = None
        self._current_key = None
        self.knowledge = load_help_bot_knowledge()
        self._init_client()

    def reload_knowledge(self) -> Dict[str, Any]:
        """Reloads the external knowledge base file so future edits are live immediately."""
        self.knowledge = load_help_bot_knowledge()
        logger.info("HelpBotService reloaded knowledge base from file.")
        return self.knowledge

    def _init_client(self):
        api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()
        if api_key:
            if self.gemini_client and self._current_key == api_key:
                return
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=api_key)
                self._current_key = api_key
                logger.info("HelpBotService initialized with live Gemini client (API key active).")
            except Exception as e:
                logger.warning(f"Failed to initialize live Gemini client: {e}")
                self.gemini_client = None
                self._current_key = None
        else:
            self.gemini_client = None
            self._current_key = None

    def _is_security_sensitive_query(self, query: str) -> bool:
        """Checks if the query is attempting to exfiltrate or reveal passwords, credentials, or internal secrets."""
        q_lower = query.lower()
        # Allow legitimate administrative questions asking how or where to update/configure keys
        config_inquiry = any(p in q_lower for p in [
            "where can i update", "where do i update", "where to update",
            "how to update", "how can i update", "how do i update",
            "how to configure", "how do i set", "how to enter", "where do i enter",
            "where to enter", "where is the key", "how to change"
        ])
        if config_inquiry and not any(ex in q_lower for ex in ["show", "reveal", "leak", "dump", "print", "give me the"]):
            return False

        sensitive_patterns = [
            r"\b(password|passwords|adminpass|admin_pass|avani2026|avanialbedo)\b",
            r"\b(give|tell|reveal|show|dump|print|leak|exfiltrate)\b.*(key|secret|credential|token|password)",
            r"\b(what\s+is\s+(the\s+)?(admin\s+)?password)\b",
            r"\b(give\s+me\s+the\s+gemini_api_key)\b",
            r"\b(service[_\s]?account[_\s]?keys?|\.env\b)",
            r"\bcredentials\s+and\s+secrets\b",
            r"\b(show|reveal|give|dump)\b.*(all\s+credentials|all\s+secrets)"
        ]
        return any(re.search(pat, q_lower) for pat in sensitive_patterns)

    def _is_off_topic_query(self, query: str) -> bool:
        """Detects clearly off-topic questions that have no relevance to climate, GIS, or the project."""
        q_lower = query.lower()
        project_keywords = [
            "avani", "albedo", "heat", "temperature", "lst", "ndvi", "ndbi", "hvi",
            "tree", "trees", "canopy", "cool roof", "shade", "hydration", "intervention",
            "optimize", "optimizer", "or-tools", "scip", "budget", "gcp", "cloud run",
            "firestore", "earth engine", "landsat", "sentinel", "bigquery", "timelapse",
            "ward", "cell", "bengaluru", "delhi", "mumbai", "pune", "dubai", "phoenix",
            "nagpur", "hyderabad", "london", "singapore", "persona", "commissioner",
            "planner", "health officer", "sensor", "accuweather", "imd", "aws", "weather",
            "feasibility", "soil", "currency", "how to use", "help", "guide", "what is",
            "explain", "who are you", "api key", "gemini"
        ]
        has_project_intent = any(k in q_lower for k in project_keywords)
        if has_project_intent:
            return False

        off_topic_signals = [
            "recipe", "cook", "movie", "song", "poem", "sports", "football",
            "cricket score", "president", "joke", "crypto", "bitcoin", "stock market",
            "write a python script for binary search", "translate to french"
        ]
        return any(sig in q_lower for sig in off_topic_signals)

    def ask(self, query: str, history: Optional[List[Dict[str, str]]] = None, city: str = "Bengaluru") -> Dict[str, Any]:
        """
        Answers queries strictly related to the Avani Albedo application.
        Strictly enforces security policies (never shares credentials or API keys).
        """
        clean_query = query.strip()
        if not clean_query:
            return {
                "status": "success",
                "response": "Please enter a question about the Avani Albedo project!",
                "model": "Avani Project Help Bot",
                "sources": ["Avani Albedo System"]
            }

        # 1. MANDATORY SECURITY GUARDRAIL CHECK
        if self._is_security_sensitive_query(clean_query):
            refusal = self.knowledge.get("security_policy", {}).get(
                "refusal_message",
                "🔒 **Security Policy Enforcement:** For strict data protection and compliance, Avani Albedo does not share passwords, API keys, credentials, or internal authentication secrets under any circumstances."
            )
            return {
                "status": "success",
                "response": refusal,
                "model": "Avani Project Help Bot (Security Policy)",
                "sources": ["Avani Albedo Security Policy"]
            }

        # 2. DOMAIN BOUNDARY GUARDRAIL CHECK
        if self._is_off_topic_query(clean_query):
            off_topic_msg = self.knowledge.get("domain_boundary", {}).get(
                "off_topic_message",
                "👋 I am the **Avani Project Help Bot**, dedicated exclusively to answering questions about the **Avani Albedo Climate Resilience & Urban Heat Island Engine**. I answer queries strictly from our application and its scientific models only. How can I assist you with Avani Albedo today?"
            )
            return {
                "status": "success",
                "response": off_topic_msg,
                "model": "Avani Project Help Bot (Domain Guardrail)",
                "sources": ["Avani Albedo Project Boundary"]
            }

        # Re-check client in case key was updated in settings/env
        current_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()
        if current_key and (not self.gemini_client or getattr(self, "_current_key", None) != current_key):
            self._init_client()

        # 3. LIVE GEMINI INVOCATION (Cascade: gemini-2.0-flash -> gemini-1.5-flash)
        if self.gemini_client:
            prompt = f"""SYSTEM CONTEXT:
{HELP_BOT_SYSTEM_PROMPT}

CURRENT ACTIVE CITY: {city}

USER QUESTION:
{clean_query}
"""
            for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                try:
                    response = self.gemini_client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text:
                        resp_text = response.text.strip()
                        # Post-check safety guardrail: Redact if any accidental secret token is caught
                        if any(s in resp_text.lower() for s in ["adminpass", "avani2026", "avanialbedo", "gemini_api_key="]):
                            resp_text = "🔒 **Security Notice:** Content redacted to comply with credential protection policies."
                        return {
                            "status": "success",
                            "response": resp_text,
                            "model": f"Gemini API ({model_name})",
                            "sources": ["Google GenAI Live SDK", "Avani Albedo System Context"]
                        }
                except Exception as e:
                    logger.warning(f"Live Gemini Help Bot call to {model_name} failed ({e}).")

        # 4. RESILIENT KNOWLEDGE BASE & TELEMETRY FALLBACK
        return self._generate_knowledge_base_answer(clean_query, city)

    def _generate_knowledge_base_answer(self, query: str, city: str) -> Dict[str, Any]:
        """Matches query against the extensible knowledge base loaded from app/data/help_bot_knowledge.json."""
        q_lower = query.lower()

        # A. Key Configuration Inquiries
        if any(w in q_lower for w in ["gemini key", "api key", "update key", "enter key", "configure key"]) and \
           any(w in q_lower for w in ["where", "how", "update", "set", "enter", "configure"]):
            topic = self.knowledge.get("topics", {}).get("gemini_api_key_configuration")
            if topic:
                return {
                    "status": "success",
                    "response": topic.get("content", ""),
                    "model": "Avani Project Help Bot (Admin Knowledge)",
                    "sources": ["Admin Settings Guide", "app/data/help_bot_knowledge.json"]
                }

        # B. Common Greetings / Who Are You
        greeting_signals = ["hello", "hi", "hey", "who are you", "what can you do", "who is avani", "greetings"]
        is_greeting = any(re.search(rf"\b{re.escape(g)}\b", q_lower) for g in greeting_signals)
        if is_greeting and len(q_lower.split()) <= 8:
            intro = f"""### 👋 Welcome to Avani Albedo Help Bot!
I am your dedicated AI climate copilot for **{city}** and metropolitan regions globally.

#### 💡 How can I help you today?
- 🛰️ **Satellite Telemetry:** Ask *"How do you measure Land Surface Temperature and NDVI?"*
- 🌡️ **Dual Temperature Modes:** Ask *"Explain Surface Temp vs Ambient Air Temp"*
- 🪓 **Trees Cut Down:** Ask *"How are trees cut down calculated?"*
- 🛠️ **Climate Interventions:** Ask *"What are the 4 climate interventions and unit costs?"*
- ⚙️ **Optimization Engine:** Ask *"How does Google OR-Tools optimize the budget?"*
- 📊 **HVI Scoring:** Ask *"What is the 6-factor HVI formula?"*
- 🔑 **API Key Configuration:** Ask *"Where can I update the Gemini key?"*"""
            return {
                "status": "success",
                "response": intro,
                "model": "Avani Project Help Bot (Assistant Engine)",
                "sources": ["Avani Albedo Assistant", "app/data/help_bot_knowledge.json"]
            }

        # C. City-Specific Telemetry Queries (e.g. "tell me about Nagpur", "how hot is Mumbai")
        try:
            from app.data.cities_heat_data import CITIES_REGISTRY, get_climate_cells_for_city
            matched_city = None
            for reg_city in CITIES_REGISTRY.keys():
                if reg_city.lower() in q_lower:
                    matched_city = reg_city
                    break

            if matched_city:
                cells = get_climate_cells_for_city(matched_city)
                if cells:
                    avg_lst = round(sum(c.lst for c in cells) / len(cells), 1)
                    max_lst = round(max(c.lst for c in cells), 1)
                    avg_ndvi = round(sum(c.ndvi for c in cells) / len(cells), 2)
                    critical_wards = [c.name for c in cells if c.lst >= 42.0 or (hasattr(c, "hvi_score") and c.hvi_score >= 70)]
                    hotspots_str = ", ".join(critical_wards[:3]) if critical_wards else cells[0].name
                    city_resp = f"""### 🏙️ Microclimate Analysis: {matched_city}

- **Average Land Surface Temperature (LST):** **{avg_lst}°C** (Peak thermal hotspot: **{max_lst}°C**)
- **Vegetation Density (NDVI):** **{avg_ndvi}** (Indicates substantial urban canopy deficit)
- **High-Risk Priority Wards:** {hotspots_str}
- **Recommended Interventions:** Prioritize **Zero-Soil High-Albedo Cool Roofs (SRI ≥ 85%)** on dense commercial/industrial roofs, and deploy **Urban Tree Canopies** in wards with available permeable soil (16 m² root space constraint).

*💡 Select **{matched_city}** in the top navigation bar to run the live OR-Tools optimizer for this city!*"""
                    return {
                        "status": "success",
                        "response": city_resp,
                        "model": "Avani Project Help Bot (GIS Telemetry Engine)",
                        "sources": [f"{matched_city} Earth Observation Telemetry", "Landsat 8/9 TIRS & Sentinel-2 MSI"]
                    }
        except Exception as city_err:
            logger.debug(f"City telemetry lookup skipped: {city_err}")

        # D. Keyword & Token Matching Across Knowledge Topics
        topics = self.knowledge.get("topics", {})
        best_topic = None
        best_score = 0

        # Extract meaningful query tokens
        stop_words = {"the", "is", "at", "which", "on", "a", "an", "do", "how", "what", "tell", "me", "about", "can", "you", "and", "or", "in", "for", "to", "of", "with"}
        q_tokens = [w for w in re.findall(r"\w+", q_lower) if len(w) > 2 and w not in stop_words]

        for key, topic in topics.items():
            keywords = topic.get("keywords", [])
            score = 0
            for kw in keywords:
                kw_low = kw.lower()
                # Exact phrase match gets high weight
                if kw_low in q_lower:
                    score += 4
                # Word-token overlap gets 1 point
                else:
                    for t in q_tokens:
                        if t in kw_low:
                            score += 1
            if score > best_score:
                best_score = score
                best_topic = topic

        if best_topic and best_score >= 2:
            return {
                "status": "success",
                "response": best_topic.get("content", ""),
                "model": "Avani Project Help Bot (Knowledge Base Engine)",
                "sources": [best_topic.get("title", "Project Knowledge"), "app/data/help_bot_knowledge.json"]
            }

        # E. General project overview answer
        general_answer = f"""### 🌍 Avani Albedo: Prescriptive Climate Resilience Engine

**Avani Albedo** is an agentic urban-climate decision platform that models, calculates, and prescribes budget-constrained interventions to counter Urban Heat Islands (UHI) in **{city}** and metropolitan regions globally.

#### 💡 Core Capabilities:
1. **Multi-Spectral Satellite Telemetry:** Uses Landsat 8/9 TIRS Band 10 (Land Surface Temperature) and Sentinel-2 MSI 10m (NDVI vegetation & NDBI concrete).
2. **Dual Temperature Modes:** Sourced from Landsat 8/9 & GEE (Surface Temperature Mode, ~42.8°C) and Weather APIs (Ambient Air Temperature Mode, ~31.5°C).
3. **6-Factor HVI Engine:** Combines thermal load, vegetation deficit, concrete density, demographics, and critical infrastructure into a normalized 0–100 vulnerability score.
4. **Google OR-Tools Solver:** Solves a Mixed-Integer Linear Program (SCIP) to identify the Pareto-optimal distribution of **Trees, Cool Roofs, Shade Canopies, and Hydration Kiosks** within municipal budget constraints.
5. **Decadal Satellite Timelapse (2014–2026):** Visualizes decadal canopy depletion and surface warming trends.
6. **Physical Land Feasibility:** Enforces 16 m² root space per tree, redirecting excess load to Zero-Soil Cool Roofs.

*💡 Ask me specifically about "Surface vs Ambient Temperature", "Trees Cut Down calculation", "The 4 interventions and costs", "OR-Tools optimizer", "HVI formula", or "GCP Cloud architecture"!*"""

        return {
            "status": "success",
            "response": general_answer,
            "model": "Avani Project Help Bot (Knowledge Base Engine)",
            "sources": ["Avani Albedo System Overview", "app/data/help_bot_knowledge.json"]
        }


help_bot_service = HelpBotService()
copilot_service = help_bot_service
CopilotService = HelpBotService
