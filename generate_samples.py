"""
Generate Sample Images for Demo & Testing
==========================================
Produces test drone orthomosaics into sample_data/ for instant upload testing.
"""

import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from vision_engine import VisionEngine

def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")
    os.makedirs(output_dir, exist_ok=True)

    ve = VisionEngine()

    scenarios = [
        ("field_midwest_corn_stressed.png", "stressed"),
        ("field_punjab_saline_degraded.png", "saline_degraded"),
        ("field_healthy_canopy.png", "healthy"),
    ]

    for filename, mode in scenarios:
        data = ve.generate_synthetic_farm_image(mode)
        path = os.path.join(output_dir, filename)
        with open(path, "wb") as f:
            f.write(data)
        print(f"[Sample Generator] Created: {path}")

if __name__ == "__main__":
    main()
