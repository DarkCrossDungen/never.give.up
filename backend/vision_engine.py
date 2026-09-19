"""
TerraPulse Vision Engine
========================
High-performance computer vision and spectral decomposition module for agricultural
and forest land diligence. Computes vegetation indices (VARI, ExG, GLI), isolates
crop canopy from background soil, detects stunted/dead growth clusters via contour
analysis, and renders radiometric stress heatmaps.
"""

import cv2
import numpy as np
import base64
from typing import Dict, Any, Tuple, List


class VisionEngine:
    """
    OpenCV-powered multispectral and RGB vegetation index analyzer.
    """

    def __init__(self):
        # Stress threshold parameters
        self.vari_healthy_threshold = 0.15
        self.vari_stressed_threshold = -0.05
        self.min_anomaly_contour_area = 150  # pixels

    def process_field_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process raw image bytes from drone/satellite/field photography.
        Returns metrics and base64-encoded visual overlays.
        """
        # Decode image from buffer
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_bgr is None:
            raise ValueError("Invalid image format or corrupted image buffer.")

        # Standardize working resolution while preserving aspect ratio
        h, w = img_bgr.shape[:2]
        max_dim = 1200
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
            h, w = img_bgr.shape[:2]

        # Convert to RGB float32 normalized [0.0, 1.0]
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_float = img_rgb.astype(np.float32) / 255.0

        r = img_float[:, :, 0]
        g = img_float[:, :, 1]
        b = img_float[:, :, 2]

        # 1. Compute Spectral Indices
        # VARI: (G - R) / (G + R - B + eps)
        # Visible Atmospherically Resistant Index - sensitive to chlorophyll, mitigates atmospheric haze
        eps = 1e-6
        vari = (g - r) / (g + r - b + eps)
        vari = np.clip(vari, -1.0, 1.0)

        # ExG: Excess Green Index (2G - R - B)
        # Distinguishes green vegetation from soil background
        exg = 2.0 * g - r - b

        # GLI: Green Leaf Index (2G - R - B) / (2G + R + B + eps)
        gli = (2.0 * g - r - b) / (2.0 * g + r + b + eps)
        gli = np.clip(gli, -1.0, 1.0)

        # 2. Vegetation Canopy Segmentation
        # Normalised ExG mask for canopy isolation
        canopy_mask = (exg > 0.05).astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        canopy_mask_cleaned = cv2.morphologyEx(canopy_mask, cv2.MORPH_OPEN, kernel)
        canopy_mask_cleaned = cv2.morphologyEx(canopy_mask_cleaned, cv2.MORPH_CLOSE, kernel)

        # 3. Zonal Health Classification
        # Healthy: Canopy with high VARI
        healthy_mask = (canopy_mask_cleaned > 0) & (vari >= self.vari_healthy_threshold)
        # Stressed/Stunted: Canopy with low/negative VARI
        stressed_mask = (canopy_mask_cleaned > 0) & (vari < self.vari_healthy_threshold)
        # Barren/Dead Soil: Non-canopy area
        barren_mask = canopy_mask_cleaned == 0

        total_pixels = float(h * w)
        healthy_pct = round((np.count_nonzero(healthy_mask) / total_pixels) * 100.0, 2)
        stressed_pct = round((np.count_nonzero(stressed_mask) / total_pixels) * 100.0, 2)
        barren_pct = round((np.count_nonzero(barren_mask) / total_pixels) * 100.0, 2)

        # 4. Anomaly Contour Extraction (Locating Stunted & Dead Patches)
        # We find contours on the combined stressed + barren patches
        anomaly_map = ((stressed_mask | barren_mask).astype(np.uint8)) * 255
        anomaly_cleaned = cv2.morphologyEx(anomaly_map, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(anomaly_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        annotated_bgr = img_bgr.copy()
        anomaly_clusters: List[Dict[str, Any]] = []

        for idx, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area >= self.min_anomaly_contour_area:
                x, y, cw, ch = cv2.boundingRect(cnt)
                # Compute severity based on mean VARI in this region
                roi_vari = vari[y : y + ch, x : x + cw]
                mean_vari = float(np.mean(roi_vari))

                severity = "SEVERE" if mean_vari < -0.1 else ("MODERATE" if mean_vari < 0.05 else "MILD")
                color = (0, 0, 230) if severity == "SEVERE" else ((0, 140, 255) if severity == "MODERATE" else (0, 220, 220))

                # Draw bounding box and label
                cv2.rectangle(annotated_bgr, (x, y), (x + cw, y + ch), color, 2)
                tag = f"ANOMALY #{len(anomaly_clusters) + 1} [{severity}]"
                cv2.putText(
                    annotated_bgr,
                    tag,
                    (x, max(y - 6, 14)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    color,
                    1,
                    cv2.LINE_AA,
                )

                anomaly_clusters.append({
                    "id": len(anomaly_clusters) + 1,
                    "bbox": [int(x), int(y), int(cw), int(ch)],
                    "area_pixels": int(area),
                    "area_pct": round((area / total_pixels) * 100.0, 2),
                    "mean_vari": round(mean_vari, 4),
                    "severity": severity,
                })

        # Sort clusters by area descending
        anomaly_clusters.sort(key=lambda item: item["area_pixels"], reverse=True)

        # 5. Generate Radiometric Heatmap Overlay
        # Normalize VARI to [0, 255] for colormap
        vari_norm = np.clip((vari + 0.3) / 0.8, 0.0, 1.0)  # Map [-0.3, 0.5] to [0, 1]
        vari_uint8 = (vari_norm * 255.0).astype(np.uint8)
        heatmap_bgr = cv2.applyColorMap(vari_uint8, cv2.COLORMAP_VIRIDIS)

        # Blend heatmap with original image for spatial context
        blended_heatmap = cv2.addWeighted(img_bgr, 0.45, heatmap_bgr, 0.55, 0)

        # 6. Encode outputs to Base64 PNGs
        annotated_b64 = self._encode_image_b64(annotated_bgr)
        heatmap_b64 = self._encode_image_b64(blended_heatmap)
        mask_b64 = self._encode_image_b64(cv2.cvtColor(canopy_mask_cleaned, cv2.COLOR_GRAY2BGR))

        # 7. Aggregate Metrics
        vegetation_uniformity_score = max(0.0, min(100.0, round(100.0 - (stressed_pct * 1.2 + barren_pct * 0.8), 1)))

        return {
            "image_dimensions": {"width": w, "height": h},
            "canopy_coverage_pct": round(100.0 - barren_pct, 2),
            "healthy_vegetation_pct": healthy_pct,
            "stressed_vegetation_pct": stressed_pct,
            "barren_soil_pct": barren_pct,
            "vegetation_uniformity_score": vegetation_uniformity_score,
            "anomaly_clusters_count": len(anomaly_clusters),
            "top_anomalies": anomaly_clusters[:8],
            "visualizations": {
                "annotated_field_b64": f"data:image/png;base64,{annotated_b64}",
                "stress_heatmap_b64": f"data:image/png;base64,{heatmap_b64}",
                "canopy_mask_b64": f"data:image/png;base64,{mask_b64}",
            },
        }

    @staticmethod
    def _encode_image_b64(cv2_img: np.ndarray) -> str:
        """Helper to convert cv2 image to PNG base64 string."""
        success, buffer = cv2.imencode(".png", cv2_img)
        if not success:
            raise RuntimeError("Failed to encode image to PNG.")
        return base64.b64encode(buffer).decode("utf-8")

    def generate_synthetic_farm_image(self, scenario: str = "stressed") -> bytes:
        """
        Generates realistic synthetic agricultural imagery for instant zero-dependency testing
        and zero-friction demo presentations.
        """
        w, h = 800, 600
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

        # Base soil tone (warm sandy-brown)
        canvas[:] = [45, 75, 110]  # BGR

        # Draw crop field rows
        row_height = 14
        for y in range(0, h, row_height * 2):
            # Healthy crop color
            color = [35, 140, 50]  # BGR Lush Green
            cv2.rectangle(canvas, (0, y), (w, y + row_height), color, -1)

        # Add Gaussian texture noise for realism
        noise = np.random.normal(0, 12, (h, w, 3)).astype(np.int16)
        textured = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        if scenario == "stressed":
            # Simulate stunted dead patch in center-right
            cv2.ellipse(textured, (520, 280), (140, 90), 25, 0, 360, (30, 60, 95), -1)
            # Simulate water-deficient chlorosis patch on bottom-left
            cv2.ellipse(textured, (220, 420), (90, 60), -15, 0, 360, (50, 110, 130), -1)
        elif scenario == "saline_degraded":
            # Multiple patchy barren areas
            for center, axes in [((300, 200), (80, 50)), ((580, 400), (110, 70)), ((180, 450), (60, 40))]:
                cv2.ellipse(textured, center, axes, 0, 0, 360, (40, 65, 100), -1)

        # Smooth slightly to mimic drone aerial optics
        textured = cv2.GaussianBlur(textured, (3, 3), 0)

        success, buffer = cv2.imencode(".png", textured)
        return buffer.tobytes()
