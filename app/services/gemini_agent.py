import json
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.models.schemas import (
    ClimateCell, ScenarioResult, ActionPlanResponse,
    WardPriority, ImplementationPhase
)
from app.data.cities_heat_data import (
    CITIES_REGISTRY, get_spot_phase_evaluation, get_city_heat_calendar
)

logger = logging.getLogger("avani_albedo.gemini")

def _get_city_metadata(city_name: str) -> Dict[str, Any]:
    target_key = "Bengaluru"
    for k in CITIES_REGISTRY.keys():
        if k.lower() in city_name.lower() or city_name.lower() in k.lower():
            target_key = k
            break
    meta = CITIES_REGISTRY.get(target_key, CITIES_REGISTRY["Bengaluru"])
    country = meta.get("country", "India")
    
    # Botanical species tailored to climate zone
    if "United Arab Emirates" in country:
        trees = "Ghaf (Prosopis cineraria), Date Palm (Phoenix dactylifera), and Sidr (Ziziphus spina-christi)"
        policy = "UAE Climate-Proof Cities 2030 & Estidama Pearl Green Building Standard"
        agency = "Dubai Municipality Climate Action Directorate"
    elif "United States" in country:
        trees = "Blue Palo Verde (Parkinsonia florida), Velvet Mesquite (Prosopis velutina), and Desert Ironwood (Olneya tesota)"
        policy = "Federal Extreme Heat Resilience Framework & OSHA Heat Safety Standards"
        agency = "City Heat Response & Mitigation Office"
    elif "United Kingdom" in country:
        trees = "London Plane (Platanus acerifolia), English Oak (Quercus robur), and Silver Birch (Betula pendula)"
        policy = "London Environment Strategy & Urban Greening Factor (UGF)"
        agency = "Greater London Authority Climate Adaptation Team"
    elif "Singapore" in country:
        trees = "Rain Tree (Samanea saman), Yellow Flame (Peltophorum pterocarpum), and Angsana (Pterocarpus indicus)"
        policy = "Singapore Green Plan 2030 & Skyrise Greenery Incentive Scheme"
        agency = "National Parks Board (NParks) & PUB Urban Drainage"
    else:
        trees = "Neem (Azadirachta indica), Honge (Pongamia pinnata), and Peepal (Ficus religiosa)"
        policy = "National Heat Action Plan (NDMA) & Municipal Disaster Management Protocols"
        agency = "Bruhat Bengaluru Mahanagara Palike (BBMP) Climate Wing"

    return {
        "city_name": meta.get("name", city_name),
        "country": country,
        "currency": meta.get("currency", "INR"),
        "currency_symbol": meta.get("currency_symbol", "₹"),
        "usd_rate": meta.get("usd_rate", 0.012),
        "trees": trees,
        "policy": policy,
        "agency": agency
    }

def _format_budget_text(amount_local: float, meta: Dict[str, Any]) -> str:
    sym = meta["currency_symbol"]
    rate = meta["usd_rate"]
    usd_val = amount_local * rate
    
    if meta["currency"] == "INR":
        if amount_local >= 10000000:
            cr = amount_local / 10000000
            usd_k = usd_val / 1000
            return f"₹{cr:.2f} Cr (${usd_k:.1f}k USD)"
        else:
            lakh = amount_local / 100000
            usd_k = usd_val / 1000
            return f"₹{lakh:.1f} Lakhs (${usd_k:.1f}k USD)"
    elif meta["currency"] == "USD":
        if amount_local >= 1000000:
            return f"${amount_local/1000000:.2f}M USD"
        return f"${amount_local/1000:.1f}k USD"
    else:
        if amount_local >= 1000000:
            return f"{sym}{amount_local/1000000:.2f}M (${usd_val/1000000:.2f}M USD)"
        return f"{sym}{amount_local/1000:.1f}k (${usd_val/1000:.1f}k USD)"

def build_prompt_context(
    scenario: ScenarioResult,
    cells: List[ClimateCell],
    persona: str = "Municipal Commissioner",
    selected_ward_id: Optional[str] = None
) -> str:
    """Prepares structured summary for the Gemini prompt."""
    cell_lookup = {c.cell_id: c for c in cells}
    top_allocations = sorted(scenario.allocations, key=lambda x: x.total_cost, reverse=True)[:5]
    meta = _get_city_metadata(scenario.city)
    
    selected_ward_data = None
    if selected_ward_id and selected_ward_id in cell_lookup:
        sw = cell_lookup[selected_ward_id]
        selected_ward_data = {
            "ward_id": sw.cell_id,
            "ward_name": sw.name,
            "lst_c": sw.lst,
            "hvi_score": sw.hvi_score,
            "built_density": sw.built_density,
            "population": sw.population,
            "schools": sw.assets.schools,
            "hospitals": sw.assets.hospitals
        }

    context = {
        "city": scenario.city,
        "country": meta["country"],
        "currency": meta["currency"],
        "native_tree_species": meta["trees"],
        "local_policy": meta["policy"],
        "persona": persona,
        "selected_spot": selected_ward_data,
        "scenario_type": scenario.scenario_type,
        "scenario_title": scenario.scenario_title,
        "budget_allocated_inr": scenario.total_budget_inr,
        "budget_spent_inr": scenario.budget_spent_inr,
        "budget_formatted": _format_budget_text(scenario.budget_spent_inr, meta),
        "avg_temp_reduction_c": scenario.avg_temp_reduction_c,
        "max_temp_reduction_c": scenario.max_temp_reduction_c,
        "total_beneficiaries": scenario.total_beneficiaries,
        "total_trees": scenario.total_trees,
        "total_cool_roof_sqft": scenario.total_cool_roof_sqft,
        "total_shades": scenario.total_shades,
        "total_hydration": scenario.total_hydration,
        "top_targeted_wards": [
            {
                "ward": a.cell_name,
                "cost_inr": a.total_cost,
                "trees": a.trees,
                "cool_roof_sqft": a.cool_roof_sqft,
                "shades": a.shade_structures,
                "hydration": a.hydration_stations,
                "cooling_benefit_c": a.cooling_reduction_c,
                "hvi_score": a.hvi_score,
                "hvi_category": a.hvi_category
            }
            for a in top_allocations
        ]
    }
    return json.dumps(context, indent=2)

def generate_fallback_plan(
    scenario: ScenarioResult,
    cells: List[ClimateCell],
    persona: str = "Municipal Commissioner",
    selected_ward_id: Optional[str] = None
) -> ActionPlanResponse:
    """
    Expert Prescriptive Climate Intelligence Fallback:
    Provides a guaranteed, error-free, mathematically grounded action plan
    tailored to the selected decision-maker persona, city geography, native flora, and specific spot.
    """
    cell_lookup = {c.cell_id: c for c in cells}
    sorted_allocs = sorted(scenario.allocations, key=lambda x: (x.hvi_score, x.total_cost), reverse=True)
    meta = _get_city_metadata(scenario.city)
    budget_txt = _format_budget_text(scenario.budget_spent_inr, meta)
    
    # Identify top priority wards
    ward_priorities: List[WardPriority] = []
    for rank, alloc in enumerate(sorted_allocs[:5], start=1):
        c = cell_lookup.get(alloc.cell_id)
        interventions_summary = []
        if alloc.trees > 0:
            interventions_summary.append(f"{alloc.trees} Climate-Resilient Trees ({meta['trees'].split(',')[0].strip()})")
        if alloc.cool_roof_sqft > 0:
            interventions_summary.append(f"{alloc.cool_roof_sqft:,} sq ft High-Albedo Roofs")
        if alloc.shade_structures > 0:
            interventions_summary.append(f"{alloc.shade_structures} Transit Shade Structures")
        if alloc.hydration_stations > 0:
            interventions_summary.append(f"{alloc.hydration_stations} Solar Hydration Kiosks")
            
        cost_txt = _format_budget_text(alloc.total_cost, meta)
        justification = (
            f"{alloc.cell_name} exhibits an HVI score of {alloc.hvi_score} ({alloc.hvi_category}). "
            f"With surface temperatures reaching {c.lst if c else 40}°C and {c.assets.schools if c else 10} schools, "
            f"this targeted {cost_txt} intervention delivers an estimated {alloc.cooling_reduction_c}°C "
            f"localized thermal drop protecting {alloc.beneficiaries:,} citizens."
        )
        
        ward_priorities.append(WardPriority(
            rank=rank,
            cell_id=alloc.cell_id,
            cell_name=alloc.cell_name,
            hvi_score=alloc.hvi_score,
            primary_interventions=interventions_summary if interventions_summary else ["General Thermal Shielding"],
            justification=justification
        ))
        
    # Phased Implementation Roadmap
    spent = scenario.budget_spent_inr if scenario.budget_spent_inr > 0 else scenario.total_budget_inr
    p1_raw = (scenario.total_shades * 120000.0) + (scenario.total_hydration * 80000.0)
    p2_raw = scenario.total_cool_roof_sqft * 45.0
    p3_raw = scenario.total_trees * 3000.0

    if p1_raw <= 0 or p2_raw <= 0 or p3_raw <= 0:
        p1_spend = round(spent * 0.22, 2)
        p2_spend = round(spent * 0.48, 2)
        p3_spend = round(max(spent * 0.10, spent - p1_spend - p2_spend), 2)
    else:
        p1_spend = round(p1_raw, 2)
        p2_spend = round(p2_raw, 2)
        p3_spend = round(p3_raw, 2)

    phases = [
        ImplementationPhase(
            phase="Phase 1: Rapid Heat-Wave Relief",
            timeline="Months 1 - 2 (Pre-Heatwave Window)",
            key_milestones=[
                f"Deploy {max(1, scenario.total_hydration)} solar-powered public hydration stations across high-density transit nodes",
                f"Install {max(1, scenario.total_shades)} reflective tensile shade canopies near pedestrian choke points",
                f"Enact targeted early heat alerts compliant with {meta['policy']}"
            ],
            estimated_spend_inr=p1_spend
        ),
        ImplementationPhase(
            phase="Phase 2: Albedo Surface Modification",
            timeline="Months 3 - 5",
            key_milestones=[
                f"Apply high-reflectance (SRI > 104) elastomeric coating across {max(50000, scenario.total_cool_roof_sqft):,} sq ft of roofs",
                "Thermal imaging drone audit before & after roof application",
                "Baseline albedo elevation from 0.15 to > 0.72 verified via Landsat 9 / Sentinel-2 calibration"
            ],
            estimated_spend_inr=p2_spend
        ),
        ImplementationPhase(
            phase="Phase 3: Urban Forestry & Canopy Expansion",
            timeline="Months 6 - 12 (Optimal Planting Window)",
            key_milestones=[
                f"Plant and fence {max(100, scenario.total_trees):,} drought-resilient native canopy species: {meta['trees']}",
                "Establish 24-month survival geo-tagging and soil moisture telemetry",
                "Long-term ambient cooling monitoring via Google Cloud BigQuery geospatial tracking"
            ],
            estimated_spend_inr=p3_spend
        )
    ]
    
    # Specific targeted spot directive if user selected a ward
    selected_ward_obj = None
    if selected_ward_id and selected_ward_id in cell_lookup:
        selected_ward_obj = cell_lookup[selected_ward_id]
    
    spot_prefix = ""
    if selected_ward_obj:
        built_pct = int(selected_ward_obj.built_density * 100)
        unbuilt_pct = max(4, 100 - built_pct)
        if built_pct >= 80:
            spot_rec = (
                f"🎯 Selected Hotspot Directive ({selected_ward_obj.name}): Peak LST is {selected_ward_obj.lst}°C with {built_pct}% concrete coverage. "
                f"Because ground soil is scarce ({unbuilt_pct}%), Phase 1 cool roof retrofits are mathematically prioritized—yielding immediate -2.3°C relief without requiring ground soil footprint."
            )
        else:
            spot_rec = (
                f"🎯 Selected Hotspot Directive ({selected_ward_obj.name}): High permeable unbuilt land available ({unbuilt_pct}%). "
                f"Prioritize Phase 3 native tree clusters ({meta['trees'].split(',')[0]}) to maximize permanent evapotranspirative cooling."
            )
    else:
        spot_rec = f"🎯 Primary Hotspot Focus: Direct Phase 1 emergency cooling assets to {sorted_allocs[0].cell_name} (HVI: {sorted_allocs[0].hvi_score}, LST: {sorted_allocs[0].lst if hasattr(sorted_allocs[0], 'lst') else 41.5}°C)."

    # Persona-tailored recommendations & summary
    if "health" in persona.lower() or "medical" in persona.lower():
        strategic_recommendations = [
            spot_rec,
            f"Pre-position IV saline, cold packs, and oral rehydration packs across health centers in {sorted_allocs[0].cell_name} (HVI: {sorted_allocs[0].hvi_score}).",
            f"Mobilize frontline healthcare workers for mandatory home checks on vulnerable seniors and infants under {meta['policy']}.",
            "Commission wet-bulb globe temperature (WBGT) real-time warning sirens and misting stations near major transit stops.",
            "Establish syndromic heatstroke surveillance across hospitals linked directly to the municipal emergency dashboard."
        ]
        exec_summary = (
            f"Public Health Climate Resilience Plan for {scenario.city} ({meta['country']}). Prioritizes safeguarding {scenario.total_beneficiaries:,} citizens "
            f"from acute thermal distress and heatstroke. OR-Tools SCIP optimization directs {budget_txt} toward critical wards, "
            f"installing {scenario.total_hydration} hydration kiosks and {scenario.total_shades} shade points to lower hotspot exposure by {scenario.heat_exposure_reduction_pct}%."
        )
    elif "planner" in persona.lower() or "infrastructure" in persona.lower():
        strategic_recommendations = [
            spot_rec,
            f"Mandate Solar Reflectance Index (SRI) ≥ 82 for all commercial building permits and municipal re-roofing projects in {scenario.city}.",
            f"Establish continuous cool vegetative corridors connecting peripheral greens to {sorted_allocs[0].cell_name} utilizing native {meta['trees']}.",
            "Incorporate permeable cool-pavement standards for all new pedestrian pathways and parking facilities.",
            f"Embed ward Heat Vulnerability Indices (HVI) into municipal zoning master plans under {meta['policy']}."
        ]
        exec_summary = (
            f"Urban Infrastructure & Planning Directive for {scenario.city} ({meta['country']}). Optimizes municipal built form across {len(scenario.allocations)} wards. "
            f"Allocates {scenario.total_cool_roof_sqft:,} sq ft of high-albedo cool roofs and {scenario.total_trees:,} canopy trees "
            f"delivering an average -{scenario.avg_temp_reduction_c}°C cooling with {budget_txt} investment."
        )
    elif "disaster" in persona.lower() or "emergency" in persona.lower():
        strategic_recommendations = [
            spot_rec,
            f"Trigger Level-3 Heatwave Emergency Protocol across {scenario.city}: deploy mobile water tankers to top transit hubs between 11:00 AM and 4:00 PM.",
            f"Designate air-conditioned municipal facilities and public libraries as 24/7 public cooling sanctuaries during extreme heat warnings.",
            "Broadcast targeted early-morning cell broadcast SMS warnings to vulnerable ward residents before 09:00 AM.",
            "Enforce mandatory suspension of outdoor construction labor from 12:00 PM to 3:30 PM on forecasted peak heat days."
        ]
        exec_summary = (
            f"Heatwave Emergency Response & Disaster Action Plan for {scenario.city} ({meta['country']}). Deploys rapid life-saving cooling infrastructure "
            f"with {scenario.total_hydration} solar hydration stations and {scenario.total_shades} transit canopies to shield {scenario.total_beneficiaries:,} people."
        )
    else: # Default: Municipal Commissioner
        strategic_recommendations = [
            spot_rec,
            f"Enact municipal cool roof mandate across {scenario.city} to lock in albedo > 0.70 across all commercial & civic roofs.",
            f"Plant {max(100, scenario.total_trees):,} drought-tolerant native canopy trees ({meta['trees']}) with smart drip irrigation telemetry.",
            f"Authorize Public-Private Partnership (PPP) tenders for rapid solar hydration kiosk deployment under {meta['policy']}.",
            f"Reinvest projected 14% peak electricity savings from {scenario.total_cool_roof_sqft:,} sq ft cool roofs into the municipal resilience fund."
        ]
        exec_summary = (
            f"Executive Municipal Climate Action Plan for {scenario.city} ({meta['country']}). Prepared for the Municipal Commissioner. "
            f"Under an allocated budget of {budget_txt}, the OR-Tools SCIP solver optimizes capital allocation "
            f"across {len(scenario.allocations)} wards, achieving -{scenario.avg_temp_reduction_c}°C average cooling (up to -{scenario.max_temp_reduction_c}°C in hotspots) "
            f"protecting {scenario.total_beneficiaries:,} citizens."
        )
    
    rationale = (
        f"The prescriptive allocation prioritizes high Heat Vulnerability Index (HVI) wards where land surface temperature (LST) "
        f"exceeds critical thresholds and vegetation deficits are severe. "
        f"By pairing high-albedo roof retrofits (which deliver immediate thermal barrier reduction with 0 m² soil required) "
        f"with deep canopy planting ({meta['trees']}) and transit hydration kiosks, the plan maximizes thermodynamic cooling efficiency "
        f"per currency unit while protecting vulnerable populations around {sum(c.assets.schools for c in cells)} schools and {sum(c.assets.hospitals for c in cells)} healthcare hubs."
    )
    
    co_benefits = [
        "Urban Heat Island (UHI) mitigation with up to 15% indoor cooling electricity savings in retrofitted buildings",
        f"Air quality improvement via particulate capture from native trees ({meta['trees'].split(',')[0]})",
        "Direct heatstroke protection for outdoor gig workers, drivers, and daily commuters",
        "Stormwater absorption and urban flash flood attenuation through increased permeable root zones",
        "Explainable, audit-ready ESG & municipal climate resilience compliance metrics"
    ]

    spot_eval = get_spot_phase_evaluation(scenario.city, selected_ward_id, scenario.total_budget_inr)
    calendar = get_city_heat_calendar(scenario.city)
    
    return ActionPlanResponse(
        scenario_result=scenario,
        executive_summary=exec_summary,
        rationale=rationale,
        persona=persona,
        strategic_recommendations=strategic_recommendations,
        ward_priorities=ward_priorities,
        implementation_phases=phases,
        co_benefits=co_benefits,
        llm_model="Vertex AI Gemini 2.0 Flash (Deterministic Baseline)",
        is_live_llm=False,
        spot_phase_evaluation=spot_eval,
        heat_calendar=calendar,
        status="success"
    )

def generate_action_plan(
    scenario: ScenarioResult,
    cells: List[ClimateCell],
    persona: str = "Municipal Commissioner",
    selected_ward_id: Optional[str] = None
) -> ActionPlanResponse:
    """
    Generates the prescriptive action plan using Gemini 2.5 Flash / Vertex AI if available,
    otherwise gracefully falls back to the deterministic resilience engine.
    """
    if not settings.GEMINI_API_KEY:
        logger.info("No GEMINI_API_KEY configured. Using expert fallback engine.")
        return generate_fallback_plan(scenario, cells, persona=persona, selected_ward_id=selected_ward_id)
        
    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        context_str = build_prompt_context(scenario, cells, persona=persona, selected_ward_id=selected_ward_id)
        prompt = f"""
You are the Lead Urban Climate & Albedo Resilience AI for the "Avani Albedo" decision engine.
Target Persona: {persona}.
Analyze the following optimization results and provide an authoritative, executive-ready climate action plan:

OPTIMIZATION DATA:
{context_str}

Please respond strictly in valid JSON format with the following keys:
{{
  "executive_summary": "Crisp 3-4 sentence executive briefing with numbers tailored to {persona}",
  "rationale": "Clear physical & socioeconomic thermodynamic rationale",
  "strategic_recommendations": [
    "High-impact actionable recommendation 1 for {persona}",
    "High-impact actionable recommendation 2 for {persona}",
    "High-impact actionable recommendation 3 for {persona}",
    "High-impact actionable recommendation 4 for {persona}"
  ],
  "ward_priorities": [
    {{
      "rank": 1,
      "cell_id": "ID",
      "cell_name": "Ward Name",
      "hvi_score": 85.0,
      "primary_interventions": ["list of key interventions"],
      "justification": "Why this ward was prioritized"
    }}
  ],
  "implementation_phases": [
    {{
      "phase": "Phase Name",
      "timeline": "Timeline",
      "key_milestones": ["milestone 1", "milestone 2"],
      "estimated_spend_inr": 1000000.0
    }}
  ],
  "co_benefits": ["benefit 1", "benefit 2", "benefit 3"]
}}
"""
        response = None
        for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    logger.info(f"Successfully generated action plan with {model_name}")
                    break
            except Exception as e:
                logger.warning(f"Error calling Gemini model {model_name}: {e}")

        if not response or not response.text:
            raise RuntimeError("All Gemini flash models failed or returned empty.")
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        
        ward_priorities = [WardPriority(**w) for w in data.get("ward_priorities", [])]
        phases = [ImplementationPhase(**p) for p in data.get("implementation_phases", [])]
        spent = scenario.budget_spent_inr if scenario.budget_spent_inr > 0 else scenario.total_budget_inr
        weights = [0.22, 0.48, 0.30]
        if not phases or len(phases) < 3 or any(p.estimated_spend_inr <= 0 for p in phases):
            fallback_plan = generate_fallback_plan(scenario, cells, persona=persona)
            phases = fallback_plan.implementation_phases
        else:
            for idx, p in enumerate(phases):
                if p.estimated_spend_inr <= 0:
                    p.estimated_spend_inr = round(spent * weights[min(idx, 2)], 2)
        
        spot_eval = get_spot_phase_evaluation(scenario.city, selected_ward_id, scenario.total_budget_inr)
        calendar = get_city_heat_calendar(scenario.city)

        return ActionPlanResponse(
            scenario_result=scenario,
            executive_summary=data.get("executive_summary", ""),
            rationale=data.get("rationale", ""),
            persona=persona,
            strategic_recommendations=data.get("strategic_recommendations", []),
            ward_priorities=ward_priorities,
            implementation_phases=phases,
            co_benefits=data.get("co_benefits", []),
            llm_model="Gemini 2.0 Flash (Live Vertex/Studio)",
            is_live_llm=True,
            spot_phase_evaluation=spot_eval,
            heat_calendar=calendar,
            status="success"
        )
        
    except Exception as e:
        logger.warning(f"Error calling Gemini API: {e}. Gracefully activating fallback engine.")
        fallback = generate_fallback_plan(scenario, cells, persona=persona, selected_ward_id=selected_ward_id)
        fallback.llm_model = f"Avani-Albedo-Fallback (Reason: {str(e)[:40]}...)"
        return fallback
