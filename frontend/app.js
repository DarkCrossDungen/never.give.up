/**
 * TerraPulse Application Client Controller
 * ========================================
 * Coordinates Leaflet geospatial mapping, image uploading, API communication,
 * and dynamic radiometric visualization rendering.
 */

class TerraPulseApp {
  constructor() {
    this.apiBase = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
      ? ""
      : ""; // Relies on same-origin or reverse-proxy

    this.currentData = null;
    this.selectedFile = null;
    this.activeTab = "annotated";

    this.initElements();
    this.initMap();
    this.initEventListeners();
  }

  initElements() {
    // Navigation Tabs & Views
    this.navTabs = document.querySelectorAll(".nav-tab");
    this.views = {
      studio: document.getElementById("view-studio"),
      "farmer-impact": document.getElementById("view-farmer-impact"),
      "how-it-works": document.getElementById("view-how-it-works"),
      benchmarks: document.getElementById("view-benchmarks"),
    };

    // Inputs
    this.scenarioSelector = document.getElementById("scenario-selector");
    this.inputLat = document.getElementById("input-lat");
    this.inputLon = document.getElementById("input-lon");
    this.coordDisplay = document.getElementById("coord-display");
    this.inputCrop = document.getElementById("input-crop");
    this.inputArea = document.getElementById("input-area");
    this.inputIntent = document.getElementById("input-intent");

    // Upload Drop Zone
    this.dropZone = document.getElementById("drop-zone");
    this.fileInput = document.getElementById("file-input");
    this.dropZonePrompt = document.getElementById("drop-zone-prompt");
    this.dropZonePreview = document.getElementById("drop-zone-preview");
    this.previewImg = document.getElementById("preview-img");
    this.previewFilename = document.getElementById("preview-filename");

    // Action Button
    this.btnRun = document.getElementById("btn-run-analysis");

    // State Containers
    this.stateEmpty = document.getElementById("state-empty");
    this.stateLoading = document.getElementById("state-loading");
    this.stateResults = document.getElementById("state-results");
    this.loadingStepText = document.getElementById("loading-step-text");
    this.dossierTimestamp = document.getElementById("dossier-timestamp");

    // KPI Elements
    this.valViabilityScore = document.getElementById("val-viability-score");
    this.valViabilityGrade = document.getElementById("val-viability-grade");
    this.valVerdict = document.getElementById("val-verdict");
    this.valCanopyPct = document.getElementById("val-canopy-pct");
    this.valAnomaliesCount = document.getElementById("val-anomalies-count");
    this.valSoilMoisture = document.getElementById("val-soil-moisture");
    this.valMoistureStatus = document.getElementById("val-moisture-status");
    this.valDroughtIndex = document.getElementById("val-drought-index");
    this.valDroughtCat = document.getElementById("val-drought-cat");

    // Visualizer Elements
    this.displayImage = document.getElementById("display-image");
    this.tabButtons = document.querySelectorAll(".spectrum-tabs .tab-btn");

    // Diligence Elements
    this.valDiagnosis = document.getElementById("val-diagnosis");
    this.valSoilAudit = document.getElementById("val-soil-audit");
    this.valSoilPh = document.getElementById("val-soil-ph");
    this.valSoilN = document.getElementById("val-soil-n");
    this.valSoilSoc = document.getElementById("val-soil-soc");
    this.valSoilClay = document.getElementById("val-soil-clay");
    this.fertilizerTbody = document.getElementById("fertilizer-tbody");
    this.valIrrigation = document.getElementById("val-irrigation");
    this.valRemediationCost = document.getElementById("val-remediation-cost");
    this.valCarbonSeq = document.getElementById("val-carbon-seq");
    this.valEngineTag = document.getElementById("val-engine-tag");
  }

  initMap() {
    const defaultLat = parseFloat(this.inputLat.value) || 30.9010;
    const defaultLon = parseFloat(this.inputLon.value) || 75.8573;

    this.map = L.map("leaflet-map", {
      zoomControl: true,
      attributionControl: false,
    }).setView([defaultLat, defaultLon], 10);

    // Dark-themed satellite/terrain basemap
    L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      { maxZoom: 18 }
    ).addTo(this.map);

    // Draggable marker
    this.marker = L.marker([defaultLat, defaultLon], { draggable: true }).addTo(this.map);

    this.marker.on("dragend", (e) => {
      const pos = e.target.getLatLng();
      this.updateCoordinates(pos.lat, pos.lng);
    });

    this.map.on("click", (e) => {
      this.marker.setLatLng(e.latlng);
      this.updateCoordinates(e.latlng.lat, e.latlng.lng);
    });

    // Invalidate size to ensure Leaflet renders tile geometry properly
    setTimeout(() => {
      if (this.map) this.map.invalidateSize();
    }, 250);
  }

  updateCoordinates(lat, lon) {
    const fixedLat = parseFloat(lat).toFixed(4);
    const fixedLon = parseFloat(lon).toFixed(4);
    this.inputLat.value = fixedLat;
    this.inputLon.value = fixedLon;
    this.coordDisplay.innerText = `${fixedLat}° N, ${fixedLon}° E`;
  }

  switchView(viewName) {
    // Update nav tab buttons active state
    if (this.navTabs) {
      this.navTabs.forEach((tab) => {
        if (tab.getAttribute("data-view") === viewName) {
          tab.classList.add("active");
        } else {
          tab.classList.remove("active");
        }
      });
    }

    // Toggle view containers visibility
    Object.keys(this.views).forEach((key) => {
      const el = this.views[key];
      if (!el) return;
      if (key === viewName) {
        el.classList.remove("hidden");
      } else {
        el.classList.add("hidden");
      }
    });

    // Invalidate map geometry when switching back to studio
    if (viewName === "studio" && this.map) {
      setTimeout(() => {
        this.map.invalidateSize();
      }, 150);
    }

    // Smooth scroll to top of page
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  initEventListeners() {
    // Coordinate input manual changes
    const handleCoordChange = () => {
      const lat = parseFloat(this.inputLat.value);
      const lon = parseFloat(this.inputLon.value);
      if (!isNaN(lat) && !isNaN(lon)) {
        this.marker.setLatLng([lat, lon]);
        this.map.panTo([lat, lon]);
        this.coordDisplay.innerText = `${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E`;
      }
    };
    this.inputLat.addEventListener("change", handleCoordChange);
    this.inputLon.addEventListener("change", handleCoordChange);

    // Preset benchmark selector
    this.scenarioSelector.addEventListener("change", (e) => {
      const val = e.target.value;
      if (val) this.loadScenario(val);
    });

    // File Drag & Drop
    this.dropZone.addEventListener("click", () => this.fileInput.click());
    this.fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        this.handleFileSelected(e.target.files[0]);
      }
    });

    ["dragenter", "dragover"].forEach((eventName) => {
      this.dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        this.dropZone.classList.add("drag-over");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      this.dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        this.dropZone.classList.remove("drag-over");
      });
    });

    this.dropZone.addEventListener("drop", (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.handleFileSelected(e.dataTransfer.files[0]);
      }
    });

    // Run Full Analysis Trigger
    this.btnRun.addEventListener("click", () => this.executeAnalysis());

    // Navigation Switcher Tabs
    if (this.navTabs) {
      this.navTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
          const targetView = tab.getAttribute("data-view");
          if (targetView) this.switchView(targetView);
        });
      });
    }

    // Spectrum Tabs
    this.tabButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        this.tabButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        this.activeTab = btn.getAttribute("data-tab");
        this.updateSpectrumView();
      });
    });
  }

  handleFileSelected(file) {
    this.selectedFile = file;
    this.previewFilename.innerText = file.name;

    const reader = new FileReader();
    reader.onload = (e) => {
      this.previewImg.src = e.target.result;
      this.dropZonePrompt.classList.add("hidden");
      this.dropZonePreview.classList.remove("hidden");
    };
    reader.readAsDataURL(file);

    // Reset scenario dropdown since user uploaded custom image
    this.scenarioSelector.value = "";
  }

  async loadScenario(scenarioId) {
    this.scenarioSelector.value = scenarioId;
    this.showLoading("LOADING BENCHMARK TELEMETRY & FIELD ANOMALIES...");

    try {
      const formData = new FormData();
      formData.append("scenario_id", scenarioId);

      const resp = await fetch(`${this.apiBase}/api/analyze-scenario`, {
        method: "POST",
        body: formData,
      });

      if (!resp.ok) {
        throw new Error(`Server returned HTTP ${resp.status}`);
      }

      const data = await resp.json();
      this.renderResults(data);

      // Sync map coordinates
      const coords = data.field_metadata.coordinates;
      this.updateCoordinates(coords.latitude, coords.longitude);
      this.marker.setLatLng([coords.latitude, coords.longitude]);
      this.map.setView([coords.latitude, coords.longitude], 11);

      if (data.field_metadata.intended_crop) {
        this.inputCrop.value = data.field_metadata.intended_crop;
      }
      if (data.field_metadata.land_area_ha) {
        this.inputArea.value = data.field_metadata.land_area_ha;
      }
    } catch (err) {
      console.error("Scenario load failure:", err);
      alert(`Could not load scenario: ${err.message}. Please verify the backend server is running.`);
      this.showEmpty();
    }
  }

  async executeAnalysis() {
    // If no file uploaded and a scenario is picked, run scenario
    if (!this.selectedFile && this.scenarioSelector.value) {
      return this.loadScenario(this.scenarioSelector.value);
    }

    if (!this.selectedFile) {
      alert("Please upload field imagery or select a preset benchmark scenario to analyze.");
      return;
    }

    this.showLoading("EXECUTING OPENCV VARI DECOMPOSITION & TELEMETRY QUERY...");

    try {
      const formData = new FormData();
      formData.append("file", this.selectedFile);
      formData.append("latitude", this.inputLat.value);
      formData.append("longitude", this.inputLon.value);
      formData.append("field_name", `Farmland Parcel [${this.inputLat.value}, ${this.inputLon.value}]`);
      formData.append("intended_crop", this.inputCrop.value);
      formData.append("intent", this.inputIntent.value);
      formData.append("land_area_ha", this.inputArea.value);

      const resp = await fetch(`${this.apiBase}/api/analyze-field`, {
        method: "POST",
        body: formData,
      });

      if (!resp.ok) {
        throw new Error(`Server returned HTTP ${resp.status}`);
      }

      const data = await resp.json();
      this.renderResults(data);
    } catch (err) {
      console.error("Analysis execution error:", err);
      alert(`Analysis failed: ${err.message}. Please check console logs.`);
      this.showEmpty();
    }
  }

  renderResults(data) {
    this.currentData = data;
    const vm = data.vision_metrics;
    const tel = data.telemetry;
    const dr = data.diligence_report;

    // Timestamp
    this.dossierTimestamp.innerText = `Dossier #TP-${Date.now().toString().slice(-6)} • ${new Date().toLocaleDateString()}`;

    // Top KPIs
    this.valViabilityScore.innerText = dr.viability_score;
    this.valViabilityGrade.innerText = `[${dr.viability_grade}]`;
    this.valVerdict.innerText = dr.executive_verdict;

    // Style verdict color
    if (dr.viability_score >= 70) {
      this.valViabilityScore.className = "kpi-number text-emerald";
    } else if (dr.viability_score >= 50) {
      this.valViabilityScore.className = "kpi-number text-amber";
    } else {
      this.valViabilityScore.className = "kpi-number text-red";
    }

    this.valCanopyPct.innerText = `${vm.canopy_coverage_pct}%`;
    this.valAnomaliesCount.innerText = vm.anomaly_clusters_count;

    const surfaceMoisture = tel.soil_layers.moisture_surface_0_7cm_m3m3;
    this.valSoilMoisture.innerText = `${surfaceMoisture} m³/m³`;
    this.valMoistureStatus.innerText = tel.climate_risk_indices.soil_moisture_status;

    this.valDroughtIndex.innerText = `${tel.climate_risk_indices.drought_vulnerability_index}/100`;
    this.valDroughtCat.innerText = tel.climate_risk_indices.drought_category;

    // Visualizer View
    this.updateSpectrumView();

    // Diligence Dossier Details
    this.valDiagnosis.innerText = dr.growth_stunting_diagnosis;
    this.valSoilAudit.innerText = dr.soil_chemical_audit;

    const sc = tel.soil_chemistry;
    this.valSoilPh.innerText = sc.soil_ph;
    this.valSoilN.innerText = `${sc.nitrogen_g_per_kg} g/kg`;
    this.valSoilSoc.innerText = `${sc.organic_carbon_g_per_kg} g/kg`;
    this.valSoilClay.innerText = `${sc.clay_fraction_pct}%`;

    // Populate Fertilizer Table
    this.fertilizerTbody.innerHTML = "";
    (dr.zonal_fertilizer_schedule || []).forEach((item) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td style="font-weight:600; color:var(--text-main); font-size:13px;">${item.nutrient}</td>
        <td class="font-mono text-emerald" style="font-weight:700; font-size:13px;">${item.rate_kg_per_ha}</td>
        <td style="color:var(--text-secondary); font-size:12.5px;">${item.application_window}</td>
        <td style="color:var(--color-apple-blue); font-weight:600; font-size:12.5px;">${item.target_zone}</td>
        <td style="font-size:12px; color:var(--text-secondary); line-height:1.45;">${item.ecological_purpose}</td>
      `;
      this.fertilizerTbody.appendChild(row);
    });

    this.valIrrigation.innerText = dr.irrigation_and_climate_roadmap;
    this.valRemediationCost.innerText = `$${dr.estimated_remediation_cost_usd_per_ha} / ha`;
    this.valCarbonSeq.innerText = `${dr.carbon_sequestration_potential_tons_co2e} tons CO₂e`;
    if (dr.model_engine) {
      this.valEngineTag.innerText = dr.model_engine;
    }

    this.showResults();
  }

  updateSpectrumView() {
    if (!this.currentData || !this.currentData.vision_metrics) return;
    const viz = this.currentData.vision_metrics.visualizations;

    if (this.activeTab === "annotated") {
      this.displayImage.src = viz.annotated_field_b64;
    } else if (this.activeTab === "heatmap") {
      this.displayImage.src = viz.stress_heatmap_b64;
    } else if (this.activeTab === "mask") {
      this.displayImage.src = viz.canopy_mask_b64;
    }
  }

  showEmpty() {
    this.stateEmpty.classList.remove("hidden");
    this.stateLoading.classList.add("hidden");
    this.stateResults.classList.add("hidden");
  }

  showLoading(stepMessage) {
    this.loadingStepText.innerText = stepMessage;
    this.stateEmpty.classList.add("hidden");
    this.stateLoading.classList.remove("hidden");
    this.stateResults.classList.add("hidden");
  }

  showResults() {
    this.stateEmpty.classList.add("hidden");
    this.stateLoading.classList.add("hidden");
    this.stateResults.classList.remove("hidden");
  }
}

// Instantiate upon DOM load
document.addEventListener("DOMContentLoaded", () => {
  window.app = new TerraPulseApp();
});
