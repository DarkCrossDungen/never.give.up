"""
TerraPulse Self-Diagnostic & Verification Suite
================================================
Verifies all core AI, CV, and agrometeorology modules locally.
"""

import os
import sys

# Ensure backend directory is in path
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from vision_engine import VisionEngine
from weather_engine import WeatherEngine
from claude_agent import ClaudeAgronomyAgent

def run_tests():
    print("=" * 60)
    print("  TERRAPULSE SYSTEM VERIFICATION PASS")
    print("=" * 60)

    # 1. Test Vision Engine
    print("\n[1/3] Testing OpenCV Spectral Decomposition Engine...")
    ve = VisionEngine()
    test_image_bytes = ve.generate_synthetic_farm_image("stressed")
    vm = ve.process_field_image(test_image_bytes)
    assert "canopy_coverage_pct" in vm, "Missing canopy_coverage_pct"
    assert "anomaly_clusters_count" in vm, "Missing anomaly_clusters_count"
    assert "visualizations" in vm, "Missing visualizations"
    print(f"  ✓ Vision Engine OK:")
    print(f"    - Canopy Coverage: {vm['canopy_coverage_pct']}%")
    print(f"    - Healthy Vegetation: {vm['healthy_vegetation_pct']}%")
    print(f"    - Stressed / Chlorotic: {vm['stressed_vegetation_pct']}%")
    print(f"    - Detected Stunted Anomalies: {vm['anomaly_clusters_count']} clusters")

    # 2. Test Weather & Soil Telemetry
    print("\n[2/3] Testing Agrometeorological & Soil Telemetry Engine...")
    we = WeatherEngine()
    telemetry = we.get_agri_telemetry(41.8780, -93.0977) # Iowa Corn Belt
    assert "soil_layers" in telemetry, "Missing soil_layers"
    assert "soil_chemistry" in telemetry, "Missing soil_chemistry"
    print(f"  ✓ Weather & Soil Telemetry OK:")
    print(f"    - Surface Moisture (0-7cm): {telemetry['soil_layers']['moisture_surface_0_7cm_m3m3']} m3/m3")
    print(f"    - Deep Moisture (28-100cm): {telemetry['soil_layers']['moisture_deep_28_100cm_m3m3']} m3/m3")
    print(f"    - Soil pH: {telemetry['soil_chemistry']['soil_ph']}")
    print(f"    - Nitrogen: {telemetry['soil_chemistry']['nitrogen_g_per_kg']} g/kg")
    print(f"    - Drought Risk Index: {telemetry['climate_risk_indices']['drought_vulnerability_index']}/100")

    # 3. Test Claude Agronomy Due Diligence Agent
    print("\n[3/3] Testing Claude Agronomy Due Diligence Agent...")
    ca = ClaudeAgronomyAgent()
    diligence = ca.generate_diligence_report(
        vision_metrics=vm,
        telemetry=telemetry,
        field_name="Iowa Corn Belt Parcel #101",
        intended_crop="Corn / Maize",
        intent="Pre-Purchase Due Diligence",
        land_area_ha=35.0,
    )
    assert "viability_score" in diligence, "Missing viability_score"
    assert "zonal_fertilizer_schedule" in diligence, "Missing fertilizer schedule"
    print(f"  ✓ Diligence Agent OK:")
    print(f"    - Viability Score: {diligence['viability_score']} ({diligence['viability_grade']})")
    print(f"    - Executive Verdict: {diligence['executive_verdict']}")
    print(f"    - Fertilizer Prescriptions: {len(diligence['zonal_fertilizer_schedule'])} zones formulated")
    print(f"    - Carbon Sequestration: {diligence['carbon_sequestration_potential_tons_co2e']} tons CO2e")

    print("\n" + "=" * 60)
    print("  ALL SUBSYSTEMS VERIFIED AND READY FOR HACKATHON JUDGING!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
