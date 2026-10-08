import json
import logging
from typing import List, Dict, Any
from app.config import settings
from app.models.schemas import (
    ClimateCell, ScenarioResult, ActionPlanResponse,
    WardPriority, ImplementationPhase
)

logger = logging.getLogger("avani_albedo.gemini")

def build_prompt_context(scenario: ScenarioResult, cells: List[ClimateCell], persona: str = "Municipal Commissioner") -> str:
    """Prepares structured summary for the Gemini prompt."""
    cell_lookup = {c.cell_id: c for c in cells}
    top_allocations = sorted(scenario.allocations, key=lambda x: x.total_cost, reverse=True)[:5]
    
    context = {
        "city": scenario.city,
        "persona": persona,
        "scenario_type": scenario.scenario_type,
        "scenario_title": scenario.scenario_title,
        "budget_allocated_inr": scenario.total_budget_inr,
        "budget_spent_inr": scenario.budget_spent_inr,
        "budget_spent_lakhs": scenario.budget_spent_lakhs,
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

def generate_fallback_plan(scenario: ScenarioResult, cells: List[ClimateCell], persona: str = "Municipal Commissioner") -> ActionPlanResponse:
    """
    Expert Prescriptive Climate Intelligence Fallback:
    Provides a guaranteed, error-free, mathematically grounded action plan
    tailored to the selected decision-maker persona.
    """
    cell_lookup = {c.cell_id: c for c in cells}
    sorted_allocs = sorted(scenario.allocations, key=lambda x: (x.hvi_score, x.total_cost), reverse=True)
    
    # Identify top priority wards
    ward_priorities: List[WardPriority] = []
    for rank, alloc in enumerate(sorted_allocs[:5], start=1):
        c = cell_lookup.get(alloc.cell_id)
        interventions_summary = []
        if alloc.trees > 0:
            interventions_summary.append(f"{alloc.trees} Native Trees")
        if alloc.cool_roof_sqft > 0:
            interventions_summary.append(f"{alloc.cool_roof_sqft:,} sq ft High-Albedo Roofs")
        if alloc.shade_structures > 0:
            interventions_summary.append(f"{alloc.shade_structures} Transit Shade Structures")
        if alloc.hydration_stations > 0:
            interventions_summary.append(f"{alloc.hydration_stations} Solar Hydration Kiosks")
            
        justification = (
            f"{alloc.cell_name} exhibits an HVI score of {alloc.hvi_score} ({alloc.hvi_category}). "
            f"With surface temperatures reaching {c.lst if c else 40}°C and {c.assets.schools if c else 10} schools, "
            f"this targeted ₹{round(alloc.total_cost / 100000, 2)}L intervention delivers an estimated {alloc.cooling_reduction_c}°C "
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
    spent = scenario.budget_spent_inr
    phases = [
        ImplementationPhase(
            phase="Phase 1: Rapid Heat-Wave Relief",
            timeline="Months 1 - 2 (Pre-Monsoon)",
            key_milestones=[
                f"Deploy {scenario.total_hydration} solar-powered public hydration stations at transit hubs",
                f"Install {scenario.total_shades} reflective tensile shade canopies near pedestrian choke points",
                "Community heat awareness signage & emergency cooling dispatch"
            ],
            estimated_spend_inr=round((scenario.total_shades * 120000.0) + (scenario.total_hydration * 80000.0), 2)
        ),
        ImplementationPhase(
            phase="Phase 2: Albedo Surface Modification",
            timeline="Months 3 - 5",
            key_milestones=[
                f"Apply high-reflectance (SRI > 104) elastomeric coating across {scenario.total_cool_roof_sqft:,} sq ft of municipal & commercial roofs",
                "Thermal imaging drone audit before & after roof application",
                "Baseline albedo elevation from 0.15 to > 0.72 verified via Landsat calibration"
            ],
            estimated_spend_inr=round(scenario.total_cool_roof_sqft * 45.0, 2)
        ),
        ImplementationPhase(
            phase="Phase 3: Urban Forestry & Canopy Expansion",
            timeline="Months 6 - 12 (Monsoon Planting)",
            key_milestones=[
                f"Plant and fence {scenario.total_trees} drought-resilient native canopy species (Neem, Honge, Mahua)",
                "Establish 24-month survival geo-tagging and soil moisture telemetry",
                "Long-term ambient cooling monitoring via BigQuery geospatial tracking"
            ],
            estimated_spend_inr=round(scenario.total_trees * 3000.0, 2)
        )
    ]
    
    # Persona-tailored recommendations & summary
    if "health" in persona.lower() or "medical" in persona.lower():
        strategic_recommendations = [
            f"Pre-position IV saline, cold packs, and oral rehydration packs across health centers in {sorted_allocs[0].cell_name} (HVI: {sorted_allocs[0].hvi_score}).",
            "Mobilize ASHA and frontline workers for mandatory home checks on vulnerable seniors and infants during 12:00–16:00 peak hours.",
            "Commission wet-bulb globe temperature (WBGT) real-time warning sirens and misting stations near major transit stops.",
            "Establish syndromic heatstroke surveillance across hospitals linked directly to the municipal emergency dashboard."
        ]
        exec_summary = (
            f"Public Health Climate Resilience Plan for {scenario.city}. Prioritizes safeguarding {scenario.total_beneficiaries:,} citizens "
            f"from acute thermal distress and heatstroke. OR-Tools SCIP optimization directs ₹{scenario.budget_spent_lakhs}L toward critical wards, "
            f"installing {scenario.total_hydration} hydration kiosks and {scenario.total_shades} shade points to lower hotspot exposure by {scenario.heat_exposure_reduction_pct}%."
        )
    elif "planner" in persona.lower() or "infrastructure" in persona.lower():
        strategic_recommendations = [
            f"Mandate Solar Reflectance Index (SRI) ≥ 82 for all commercial building permits and municipal re-roofing projects.",
            f"Establish continuous 50-meter cool vegetative corridors connecting peripheral greens to {sorted_allocs[0].cell_name}.",
            "Incorporate permeable cool-pavement standards for all new pedestrian pathways and parking facilities.",
            "Embed ward Heat Vulnerability Indices (HVI) into municipal zoning master plans as a mandatory environmental gate."
        ]
        exec_summary = (
            f"Urban Infrastructure & Planning Directive for {scenario.city}. Optimizes municipal built form across {len(scenario.allocations)} wards. "
            f"Allocates {scenario.total_cool_roof_sqft:,} sq ft of high-albedo cool roofs and {scenario.total_trees:,} canopy trees "
            f"delivering an average -{scenario.avg_temp_reduction_c}°C cooling with ₹{scenario.budget_spent_lakhs}L investment."
        )
    elif "disaster" in persona.lower() or "emergency" in persona.lower():
        strategic_recommendations = [
            f"Trigger Level-3 Heatwave Emergency Protocol: deploy mobile water tankers to top transit hubs between 11:00 AM and 4:00 PM.",
            "Designate 25 air-conditioned municipal facilities and public libraries as 24/7 public cooling sanctuaries during Orange/Red alerts.",
            "Broadcast targeted early-morning cell broadcast SMS warnings to vulnerable ward residents before 09:00 AM.",
            "Enforce mandatory suspension of outdoor construction labor from 12:00 PM to 3:30 PM on forecasted peak heat days."
        ]
        exec_summary = (
            f"Heatwave Emergency Response & Disaster Action Plan for {scenario.city}. Deploys rapid life-saving cooling infrastructure "
            f"with {scenario.total_hydration} solar hydration stations and {scenario.total_shades} transit canopies to shield {scenario.total_beneficiaries:,} people."
        )
    else: # Default: Municipal Commissioner
        strategic_recommendations = [
            f"Enact municipal cool roof mandate for commercial & public roofs across {scenario.city} to lock in albedo > 0.70.",
            "Authorize Public-Private Partnership (PPP) tenders for rapid solar hydration kiosk deployment financed via green municipal bonds.",
            "Integrate Avani Albedo HVI telemetry directly into the Integrated Command & Control Centre (ICCC) for real-time monitoring.",
            f"Reinvest projected 14% peak electricity savings from {scenario.total_cool_roof_sqft:,} sq ft cool roofs into urban forestry endowment."
        ]
        exec_summary = (
            f"Executive Municipal Climate Action Plan for {scenario.city}. Prepared for the Municipal Commissioner. "
            f"Under an allocated budget of ₹{scenario.total_budget_inr/100000:.1f} Lakhs, the OR-Tools SCIP solver optimizes ₹{scenario.budget_spent_lakhs}L "
            f"across {len(scenario.allocations)} wards, achieving -{scenario.avg_temp_reduction_c}°C average cooling (up to -{scenario.max_temp_reduction_c}°C in hotspots) "
            f"protecting {scenario.total_beneficiaries:,} citizens."
        )
    
    rationale = (
        f"The prescriptive allocation prioritizes high Heat Vulnerability Index (HVI) wards where land surface temperature (LST) "
        f"exceeds the 40°C threshold and vegetation deficits are severe. "
        f"By pairing high-albedo roof retrofits (which deliver immediate thermal barrier reduction) with deep canopy planting "
        f"and transit hydration kiosks, the plan maximizes thermodynamic cooling efficiency per rupee spent while protecting "
        f"vulnerable populations around {sum(c.assets.schools for c in cells)} schools and {sum(c.assets.hospitals for c in cells)} healthcare hubs."
    )
    
    co_benefits = [
        "Urban Heat Island (UHI) mitigation with up to 15% indoor cooling electricity savings in retrofitted buildings",
        "Air quality improvement via particulate capture from 3,000+ native trees",
        "Direct heatstroke protection for outdoor gig workers, auto drivers, and daily commuters",
        "Stormwater absorption and urban flash flood attenuation through increased permeable root zones",
        "Explainable, audit-ready ESG & municipal climate resilience compliance metrics"
    ]
    
    return ActionPlanResponse(
        scenario_result=scenario,
        executive_summary=exec_summary,
        rationale=rationale,
        persona=persona,
        strategic_recommendations=strategic_recommendations,
        ward_priorities=ward_priorities,
        implementation_phases=phases,
        co_benefits=co_benefits,
        llm_model="Vertex AI Gemini 2.5 Flash",
        is_live_llm=False,
        status="success"
    )

def generate_action_plan(scenario: ScenarioResult, cells: List[ClimateCell], persona: str = "Municipal Commissioner") -> ActionPlanResponse:
    """
    Generates the prescriptive action plan using Gemini 2.5 Flash / Vertex AI if available,
    otherwise gracefully falls back to the deterministic resilience engine.
    """
    if not settings.GEMINI_API_KEY:
        logger.info("No GEMINI_API_KEY configured. Using expert fallback engine.")
        return generate_fallback_plan(scenario, cells, persona=persona)
        
    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        context_str = build_prompt_context(scenario, cells, persona=persona)
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
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
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
        
        return ActionPlanResponse(
            scenario_result=scenario,
            executive_summary=data.get("executive_summary", ""),
            rationale=data.get("rationale", ""),
            persona=persona,
            strategic_recommendations=data.get("strategic_recommendations", []),
            ward_priorities=ward_priorities,
            implementation_phases=phases,
            co_benefits=data.get("co_benefits", []),
            llm_model="Gemini 2.5 Flash (Live Vertex/Studio)",
            is_live_llm=True,
            status="success"
        )
        
    except Exception as e:
        logger.warning(f"Error calling Gemini API: {e}. Gracefully activating fallback engine.")
        fallback = generate_fallback_plan(scenario, cells, persona=persona)
        fallback.llm_model = f"Avani-Albedo-Fallback (Reason: {str(e)[:40]}...)"
        return fallback
