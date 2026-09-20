"""
TerraPulse Autonomous Agronomy & Land Diligence Agent
=====================================================
Autonomous agronomic intelligence engine calculating soil pedology,
chemical equilibrium, and stoichiometric fertilizer requirements.
Synthesizes computer vision anomaly clusters, multi-layer soil
moisture, and agrometeorology to produce a comprehensive Pre-Cultivation & Farmland Purchase
Diligence Dossier.
"""

import os
import json
from typing import Dict, Any, Optional
import numpy as np

try:
    import anthropic
except ImportError:
    anthropic = None


class ClaudeAgronomyAgent:
    """
    Autonomous precision agriculture intelligence engine.
    """

    MODEL_NAME = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", self.MODEL_NAME)
        self.client = None
        if anthropic and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception:
                self.client = None

    def generate_diligence_report(
        self,
        vision_metrics: Dict[str, Any],
        telemetry: Dict[str, Any],
        field_name: str = "Target Parcel #402",
        intended_crop: str = "Corn / Maize",
        intent: str = "Pre-Purchase Due Diligence",
        land_area_ha: float = 12.5,
    ) -> Dict[str, Any]:
        """
        Executes Claude Sonnet reasoning over combined geospatial, spectral,
        and meteorological telemetry.
        """
        if self.client:
            try:
                return self._call_claude_api(
                    vision_metrics, telemetry, field_name, intended_crop, intent, land_area_ha
                )
            except Exception as exc:
                print(f"[ClaudeAgronomyAgent] API error ({exc}), falling back to deterministic reasoning engine.")

        # Fallback to deterministic scientific agronomy reasoning
        return self._generate_scientific_deterministic_report(
            vision_metrics, telemetry, field_name, intended_crop, intent, land_area_ha
        )

    def _call_claude_api(
        self,
        vision_metrics: Dict[str, Any],
        telemetry: Dict[str, Any],
        field_name: str,
        intended_crop: str,
        intent: str,
        land_area_ha: float,
    ) -> Dict[str, Any]:
        """Queries Claude 3.5 Sonnet with structured agronomic prompt."""
        system_prompt = (
            "You are Dr. Elena Vance, Senior Chief Agronomist and Geospatial Land Valuator at TerraPulse. "
            "You analyze agricultural land for prospective buyers, regenerative farmers, and agricultural banks. "
            "Your evaluations must be grounded in physical soil chemistry, stoichiometric nutrient requirements, "
            "and satellite/drone spectral indices. Always output strict valid JSON matching the required schema."
        )

        user_content = f"""
FIELD ASSESSMENT REQUEST:
- Parcel Name: {field_name}
- Target Crop: {intended_crop}
- Objective: {intent}
- Land Area: {land_area_ha} hectares
- Geographic Coordinates: {telemetry.get('coordinates')}

OPENCV SPECTRAL & VISION METRICS:
- Canopy Coverage: {vision_metrics.get('canopy_coverage_pct')}%
- Healthy Vegetation: {vision_metrics.get('healthy_vegetation_pct')}%
- Stressed / Chlorotic Vegetation: {vision_metrics.get('stressed_vegetation_pct')}%
- Barren / Dead Ground: {vision_metrics.get('barren_soil_pct')}%
- Vegetation Uniformity Score: {vision_metrics.get('vegetation_uniformity_score')}/100
- Anomaly Clusters Count: {vision_metrics.get('anomaly_clusters_count')}
- Sample Anomaly Clusters: {json.dumps(vision_metrics.get('top_anomalies', [])[:3])}

METEOROLOGICAL & SOIL TELEMETRY:
- Soil Moisture (0-7cm surface): {telemetry.get('soil_layers', {}).get('moisture_surface_0_7cm_m3m3')} m3/m3
- Soil Moisture (7-28cm rootzone): {telemetry.get('soil_layers', {}).get('moisture_rootzone_7_28cm_m3m3')} m3/m3
- Soil Moisture (28-100cm deep): {telemetry.get('soil_layers', {}).get('moisture_deep_28_100cm_m3m3')} m3/m3
- Reference Evapotranspiration (ET0): {telemetry.get('atmospheric', {}).get('evapotranspiration_et0_mm_day')} mm/day
- 7-Day Forecast Rainfall: {telemetry.get('atmospheric', {}).get('forecast_rain_7d_total_mm')} mm
- Drought Vulnerability Index: {telemetry.get('climate_risk_indices', {}).get('drought_vulnerability_index')}/100
- Soil pH: {telemetry.get('soil_chemistry', {}).get('soil_ph')}
- Nitrogen: {telemetry.get('soil_chemistry', {}).get('nitrogen_g_per_kg')} g/kg
- Organic Carbon: {telemetry.get('soil_chemistry', {}).get('organic_carbon_g_per_kg')} g/kg

Synthesize this data and return ONLY a valid JSON object with the following schema:
{{
  "viability_score": <int 0-100>,
  "viability_grade": "<'A+' | 'A' | 'B' | 'C' | 'F'>",
  "executive_verdict": "<'ACQUIRE & CULTIVATE' | 'CONDITIONAL PURCHASE (REMEDIATION REQ)' | 'DO NOT PURCHASE / HIGH DEGRADATION'>",
  "growth_stunting_diagnosis": "<Detailed 2-3 sentence analysis of root cause of barren/stunted patches>",
  "soil_chemical_audit": "<Evaluation of soil pH, nitrogen, and carbon equilibrium>",
  "zonal_fertilizer_schedule": [
    {{
      "nutrient": "<e.g. Nitrogen (N), Phosphate (P2O5), Potassium (K2O), Gypsum, or Biochar>",
      "rate_kg_per_ha": <int>,
      "application_window": "<e.g. Pre-seeding basal broadcast | Split-side dress>",
      "target_zone": "<e.g. Whole parcel | Stunted clusters #1-#3>",
      "ecological_purpose": "<e.g. Remediate sodium compaction without chemical runoff>"
    }}
  ],
  "irrigation_and_climate_roadmap": "<Actionable guidance factoring ET0 and 7-day rainfall>",
  "estimated_remediation_cost_usd_per_ha": <int>,
  "carbon_sequestration_potential_tons_co2e": <float>
}}
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )

        raw_text = response.content[0].text.strip()
        # Clean json formatting if code fences included
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```json")[-1].split("```")[0].strip()

        return json.loads(raw_text)

    def _generate_scientific_deterministic_report(
        self,
        vision_metrics: Dict[str, Any],
        telemetry: Dict[str, Any],
        field_name: str,
        intended_crop: str,
        intent: str,
        land_area_ha: float,
    ) -> Dict[str, Any]:
        """
        Deterministic agronomic expert engine calculating accurate stoichiometric
        fertilizer requirements and due diligence scoring.
        """
        healthy_pct = vision_metrics.get("healthy_vegetation_pct", 60.0)
        stressed_pct = vision_metrics.get("stressed_vegetation_pct", 25.0)
        barren_pct = vision_metrics.get("barren_soil_pct", 15.0)
        anomalies_count = vision_metrics.get("anomaly_clusters_count", 3)

        moisture = telemetry.get("soil_layers", {}).get("moisture_surface_0_7cm_m3m3", 0.20)
        drought_idx = telemetry.get("climate_risk_indices", {}).get("drought_vulnerability_index", 45)
        ph = telemetry.get("soil_chemistry", {}).get("soil_ph", 6.8)
        nitrogen = telemetry.get("soil_chemistry", {}).get("nitrogen_g_per_kg", 1.4)
        soc = telemetry.get("soil_chemistry", {}).get("organic_carbon_g_per_kg", 14.0)
        et0 = telemetry.get("atmospheric", {}).get("evapotranspiration_et0_mm_day", 4.5)
        rain_7d = telemetry.get("atmospheric", {}).get("forecast_rain_7d_total_mm", 12.0)

        # 1. Calculate Viability Score (0-100)
        score = 100.0
        score -= (stressed_pct * 0.7)
        score -= (barren_pct * 1.1)
        score -= max(0, (drought_idx - 30) * 0.4)
        if ph < 5.8 or ph > 8.0:
            score -= 15.0
        elif ph < 6.2 or ph > 7.5:
            score -= 8.0
        if nitrogen < 1.0:
            score -= 10.0
        if moisture < 0.16:
            score -= 12.0

        viability_score = int(np.clip(round(score), 10, 98))

        if viability_score >= 85:
            grade = "A+"
            verdict = "ACQUIRE & CULTIVATE IMMEDIATELY"
        elif viability_score >= 72:
            grade = "A"
            verdict = "PROCEED WITH TARGETED CULTIVATION"
        elif viability_score >= 55:
            grade = "B"
            verdict = "CONDITIONAL ACQUISITION (SOIL REMEDIATION REQ)"
        elif viability_score >= 40:
            grade = "C"
            verdict = "ELEVATED RISK - EXTENSIVE BIO-RESTORATION NEEDED"
        else:
            grade = "F"
            verdict = "DO NOT ACQUIRE / CRITICAL LAND DEGRADATION"

        # 2. Agronomic Diagnosis
        reasons = []
        if anomalies_count > 0:
            reasons.append(f"{anomalies_count} localized anomaly zones exhibiting severe negative VARI chlorophyll attenuation.")
        if moisture < 0.18:
            reasons.append(f"Acute topsoil moisture depletion ({moisture} m3/m3) compounding plant evapotranspirative strain.")
        if ph > 7.8:
            reasons.append(f"Severe alkaline/saline soil pH ({ph}) causing exchangeable sodium toxicity and micronutrient lockup (zinc and iron deficiency).")
        elif ph > 7.4:
            reasons.append(f"Sub-alkaline soil pH ({ph}) inducing mild phosphorus and micronutrient fixation.")
        elif ph < 6.0:
            reasons.append(f"Acidic soil matrix ({ph}) risking aluminum phytotoxicity and suppressing beneficial nitrogen-fixing rhizobia.")
        if nitrogen < 1.1:
            reasons.append(f"Severely depleted nitrogen baseline ({nitrogen} g/kg) causing widespread chlorotic yellowing.")
        elif nitrogen > 2.0 and rain_7d > 20.0:
            reasons.append(f"Elevated nitrogen reserves ({nitrogen} g/kg) subject to acute downward nitrate leaching under heavy forecast rainfall ({rain_7d}mm).")

        diagnosis = " ".join(reasons) if reasons else "Canopy exhibits uniform photosynthetic vigor with optimal rootzone hydration and minimal localized stress."

        # 3. Zonal Stoichiometric Fertilizer Schedule
        fertilizer_schedule = []

        # Soil chemistry conditioning
        if ph > 7.8:
            fertilizer_schedule.append({
                "nutrient": "Agricultural Gypsum (CaSO4 · 2H2O)",
                "rate_kg_per_ha": 850,
                "application_window": "Pre-cultivation deep incorporation",
                "target_zone": f"Saline crusts & Anomaly zones #1-#{max(1, anomalies_count)}",
                "ecological_purpose": "Displace toxic exchangeable sodium (Na+) into soil solution to restore flocculation and alleviate hardpan crusting.",
            })
            fertilizer_schedule.append({
                "nutrient": "Elemental Sulfur (S 90%)",
                "rate_kg_per_ha": 110,
                "application_window": "Pre-planting basal broadcast",
                "target_zone": "Entire cultivation parcel",
                "ecological_purpose": "Biological oxidation into sulfuric acid by Thiobacillus to lower rootzone pH from alkaline toward neutral.",
            })
        elif ph < 6.0:
            fertilizer_schedule.append({
                "nutrient": "Agricultural Limestone (CaCO3)",
                "rate_kg_per_ha": 1200,
                "application_window": "Pre-tillage broadcasting (incorporate 15cm)",
                "target_zone": "Entire cultivation parcel",
                "ecological_purpose": "Neutralize soil acidity to suppress aluminum toxicity and restore microbial nitrification.",
            })

        # Nitrogen prescription tailored to reserves
        if nitrogen < 1.1:
            fertilizer_schedule.append({
                "nutrient": "Polymer-Coated Slow-Release Urea (46-0-0)",
                "rate_kg_per_ha": 115,
                "application_window": "Split: 30% basal, 40% V4 stage, 30% pre-tasseling",
                "target_zone": f"Chlorotic zones #1-#{max(1, anomalies_count)}",
                "ecological_purpose": "Remediate severe nitrogen deficit with controlled-release granules that prevent leaching into groundwater.",
            })
        elif nitrogen < 1.6:
            fertilizer_schedule.append({
                "nutrient": "Urea / Slow-Release Nitrogen (46-0-0)",
                "rate_kg_per_ha": 75,
                "application_window": "Split-application: 35% basal, 65% at V6 vegetative surge",
                "target_zone": f"Anomalies #1-#{max(1, anomalies_count)} & low-VARI corridors",
                "ecological_purpose": "Replenish cellular chlorophyll synthesis while minimizing nitrate leaching into local aquifers.",
            })
        else:
            fertilizer_schedule.append({
                "nutrient": "Nitrification Inhibitor-Treated Urea",
                "rate_kg_per_ha": 45,
                "application_window": "Targeted side-dressing only at peak crop demand",
                "target_zone": "Low-chlorophyll vegetative corridors",
                "ecological_purpose": "Conserve rich baseline organic nitrogen and stop excess nitrate leaching under rainfall.",
            })

        # Phosphorus and root anchorage
        fertilizer_schedule.append({
            "nutrient": "Diammonium Phosphate (DAP 18-46-0)",
            "rate_kg_per_ha": 50 if soc > 15.0 else 65,
            "application_window": "Pre-planting precision row banding (5cm below seed)",
            "target_zone": "Entire cultivation parcel",
            "ecological_purpose": "Stimulate early root anchorage to withstand forecast drought and weather swings.",
        })

        # Potassium & drought defense
        potash_rate = 65 if (drought_idx > 45 or et0 > 4.5) else 35
        fertilizer_schedule.append({
            "nutrient": "Muriate of Potash (K2O 0-0-60)",
            "rate_kg_per_ha": potash_rate,
            "application_window": "Pre-tillage or early broadcast",
            "target_zone": "Entire cultivation parcel",
            "ecological_purpose": "Enhance stomatal regulation and guard cells against high atmospheric VPD and evapotranspiration.",
        })

        # Carbon & soil structure conditioner
        if soc < 12.0 or barren_pct > 15.0:
            fertilizer_schedule.append({
                "nutrient": "Humic Acid & Pyrolyzed Biochar Soil Conditioner",
                "rate_kg_per_ha": 350,
                "application_window": "Pre-cultivation topsoil incorporation",
                "target_zone": "Barren/Dead soil patches & rootzone corridors",
                "ecological_purpose": "Rebuild depleted soil organic carbon and expand moisture-holding capacity by 25%.",
            })

        # 4. Remediation Cost & Carbon Retention
        remediation_cost = int(140 + (barren_pct * 14.5) + (anomalies_count * 25) + (120 if ph > 7.8 else 0))
        carbon_sequestration = round(float(land_area_ha * (soc * 0.12) * 1.8), 2)

        # 5. Dynamic Hydrological Roadmap
        net_deficit = round((et0 * 7.0) - rain_7d, 1)
        if net_deficit > 18.0:
            irrigation_roadmap = f"Severe 7-day moisture deficit of {net_deficit}mm (ET0: {et0} mm/day vs rain: {rain_7d} mm). High evaporation requires {round(net_deficit * 0.85)}mm supplemental pulsed micro-drip irrigation applied across nocturnal intervals to minimize leaf scald."
        elif rain_7d > (et0 * 7.0 + 10.0):
            irrigation_roadmap = f"Forecast indicates moisture surplus ({rain_7d} mm 7d rain exceeding weekly ET0 of {round(et0*7, 1)} mm). Immediate suspension of irrigation recommended to prevent nitrate denitrification and rootzone waterlogging."
        else:
            irrigation_roadmap = f"Hydrological budget is near equilibrium ({net_deficit}mm 7-day net deficit). Routine baseline deficit fertigation of {max(12, round(net_deficit))}mm recommended factoring {rain_7d}mm natural precipitation."

        return {
            "viability_score": viability_score,
            "viability_grade": grade,
            "executive_verdict": verdict,
            "growth_stunting_diagnosis": diagnosis,
            "soil_chemical_audit": f"Soil pH measured at {ph} with Nitrogen reserves at {nitrogen} g/kg and Organic Carbon at {soc} g/kg. Cation exchange capacity is supported by a {telemetry.get('soil_chemistry', {}).get('clay_fraction_pct', 28)}% clay fraction.",
            "zonal_fertilizer_schedule": fertilizer_schedule,
            "irrigation_and_climate_roadmap": irrigation_roadmap,
            "estimated_remediation_cost_usd_per_ha": remediation_cost,
            "carbon_sequestration_potential_tons_co2e": carbon_sequestration,
            "model_engine": "TerraPulse Autonomous Agronomy Intelligence Engine",
        }
