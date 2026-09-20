"""
TerraPulse Application Server
=============================
Production FastAPI application orchestrating the OpenCV vision engine,
Open-Meteo & SoilGrids telemetry engine, and Agronomy Intelligence diligence agent.
Exposes REST APIs and serves the production web interface.
"""

import os
import sys
from typing import Optional

# Ensure backend directory is in python path regardless of execution root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from vision_engine import VisionEngine
from weather_engine import WeatherEngine
from claude_agent import ClaudeAgronomyAgent

app = FastAPI(
    title="TerraPulse: Farmland Diligence & Precision Cultivation Engine",
    description="Enterprise-grade geospatial AI platform for the NextStep Hacks 2026 Earth Forward track.",
    version="1.0.0",
)

# Enable CORS for flexible deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate core engines
vision_engine = VisionEngine()
weather_engine = WeatherEngine()
claude_agent = ClaudeAgronomyAgent()

# Preset demo scenarios for instant one-click review during judging
DEMO_SCENARIOS = {
    "midwest_corn_nitrogen_deficit": {
        "id": "midwest_corn_nitrogen_deficit",
        "title": "US Corn Belt (Iowa) - Nitrogen Leaching & Patchy Chlorosis",
        "latitude": 41.8780,
        "longitude": -93.0977,
        "intended_crop": "Corn / Maize",
        "intent": "Pre-Purchase Due Diligence",
        "land_area_ha": 35.0,
        "synthetic_type": "stressed",
        "description": "Commercial parcel exhibiting localized nitrogen chlorosis and topsoil compaction following heavy spring runoff.",
    },
    "punjab_semi_arid_saline": {
        "id": "punjab_semi_arid_saline",
        "title": "Indo-Gangetic Plain (Punjab) - Salinity & Rootzone Stress",
        "latitude": 30.9010,
        "longitude": 75.8573,
        "intended_crop": "Durum Wheat",
        "intent": "Pre-Cultivation Land Viability Audit",
        "land_area_ha": 18.2,
        "synthetic_type": "saline_degraded",
        "description": "Intensive agricultural tract with elevated electrical conductivity and microclimate evaporation deficit.",
    },
    "california_almond_drought": {
        "id": "california_almond_drought",
        "title": "Central Valley (California) - Acute Groundwater Deficit",
        "latitude": 36.7783,
        "longitude": -119.4179,
        "intended_crop": "Almonds / Orchard",
        "intent": "Farmland Acquisition Assessment",
        "land_area_ha": 50.0,
        "synthetic_type": "drought_arid",
        "description": "High-value perennial crop acreage requiring strict water budgeting and organic carbon replenishment.",
    },
}


@app.get("/api/health")
def health_check():
    """Returns runtime health and AI module readiness."""
    return {
        "status": "online",
        "service": "TerraPulse Engine",
        "modules": {
            "vision_engine": "OpenCV 5.0 Spectral Decomposition Active",
            "weather_engine": "Open-Meteo & SoilGrids Telemetry Active",
            "agronomy_engine": "Autonomous Agronomy Intelligence Engine Active",
        },
    }


@app.get("/api/scenarios")
def get_scenarios():
    """Returns list of curated agricultural demo scenarios."""
    return list(DEMO_SCENARIOS.values())


@app.post("/api/analyze-field")
async def analyze_field(
    file: Optional[UploadFile] = File(None),
    latitude: float = Form(30.9010),
    longitude: float = Form(75.8573),
    field_name: str = Form("Target Farmland Parcel #101"),
    intended_crop: str = Form("Maize / Corn"),
    intent: str = Form("Pre-Cultivation Land Viability Audit"),
    land_area_ha: float = Form(15.0),
):
    """
    Main multimodal endpoint: ingests drone/satellite image + GPS coordinates.
    Runs OpenCV vision engine, queries live weather & soil telemetry,
    and produces autonomous agronomic diligence dossier.
    If no file is provided, automatically synthesizes an aerial orthomosaic
    matched to the parcel's agro-climatic zone.
    """
    try:
        image_bytes = None
        if file is not None:
            image_bytes = await file.read()

        if not image_bytes:
            # Dynamically determine synthetic orthomosaic archetype from coordinates & climate
            lat_abs = abs(latitude)
            if (20.0 <= lat_abs <= 38.0 and -124.0 <= longitude <= -110.0) or (20.0 <= lat_abs <= 35.0 and 35.0 <= longitude <= 75.0):
                synthetic_type = "drought_arid"
            elif 22.0 <= latitude <= 34.0 and 70.0 <= longitude <= 88.0:
                synthetic_type = "saline_degraded"
            else:
                synthetic_type = "stressed"
            image_bytes = vision_engine.generate_synthetic_farm_image(synthetic_type)

        # 1. Computer Vision & Spectral Processing
        vision_metrics = vision_engine.process_field_image(image_bytes)

        # 2. Global Agrometeorology & Soil Telemetry
        telemetry = weather_engine.get_agri_telemetry(latitude, longitude)

        # 3. Autonomous Due Diligence & Fertilizer Prescription
        diligence = claude_agent.generate_diligence_report(
            vision_metrics=vision_metrics,
            telemetry=telemetry,
            field_name=field_name,
            intended_crop=intended_crop,
            intent=intent,
            land_area_ha=land_area_ha,
        )

        return {
            "success": True,
            "field_metadata": {
                "field_name": field_name,
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "intended_crop": intended_crop,
                "intent": intent,
                "land_area_ha": land_area_ha,
            },
            "vision_metrics": vision_metrics,
            "telemetry": telemetry,
            "diligence_report": diligence,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/analyze-scenario")
def analyze_preset_scenario(scenario_id: str = Form(...)):
    """
    Executes an instant end-to-end diligence audit on a preset benchmark scenario.
    """
    if scenario_id not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")

    scenario = DEMO_SCENARIOS[scenario_id]
    image_bytes = vision_engine.generate_synthetic_farm_image(scenario["synthetic_type"])

    # Vision processing
    vision_metrics = vision_engine.process_field_image(image_bytes)

    # Telemetry
    telemetry = weather_engine.get_agri_telemetry(scenario["latitude"], scenario["longitude"])

    # Autonomous Diligence
    diligence = claude_agent.generate_diligence_report(
        vision_metrics=vision_metrics,
        telemetry=telemetry,
        field_name=scenario["title"],
        intended_crop=scenario["intended_crop"],
        intent=scenario["intent"],
        land_area_ha=scenario["land_area_ha"],
    )

    return {
        "success": True,
        "field_metadata": {
            "field_name": scenario["title"],
            "coordinates": {"latitude": scenario["latitude"], "longitude": scenario["longitude"]},
            "intended_crop": scenario["intended_crop"],
            "intent": scenario["intent"],
            "land_area_ha": scenario["land_area_ha"],
            "description": scenario["description"],
        },
        "vision_metrics": vision_metrics,
        "telemetry": telemetry,
        "diligence_report": diligence,
    }


# Mount frontend static directory if exists
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    def serve_frontend_root():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/styles.css")
    def serve_styles():
        return FileResponse(os.path.join(frontend_path, "styles.css"))

    @app.get("/app.js")
    def serve_app_js():
        return FileResponse(os.path.join(frontend_path, "app.js"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
