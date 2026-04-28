from apps.simulation.engine import execute_simulation_step
from apps.ingestion.services import fetch_river_data, fetch_rainfall_data

def run_simulation_step(rain_mm=None, height_mm=None):
    river_level_mm = float(height_mm) if height_mm is not None else fetch_river_data()
    rainfall_mm = float(rain_mm) if rain_mm is not None else fetch_rainfall_data()

    overflow_m = max(0.0, (river_level_mm - 6000) / 1000.0)
    rainfall_m = rainfall_mm / 1000.0

    return {
        "source": "custom" if height_mm is not None or rain_mm is not None else "irl",
        "rain_mm": rainfall_mm,
        "height_mm": river_level_mm,
        "results": execute_simulation_step(overflow_m, rainfall_m),
    }
