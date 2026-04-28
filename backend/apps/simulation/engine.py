import math
from apps.geography.models import GridCell

# --- Constants ---
CELL_SIZE = 1000.0  # meters
CELL_AREA = CELL_SIZE * CELL_SIZE
DT = 900  # seconds (15 minutes)
MANNING_N = 0.012
INFILTRATION_RATE = 0.0

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]

# --- Helper Functions ---

def _parse_grid_id(grid_id):
    """Converts 'cell_1_2' to (1, 2)."""
    parts = grid_id.split('_')
    return int(parts[1]), int(parts[2])

def apply_rainfall(cell_map, rainfall_m):
    """Adds rainfall uniformly to all cells."""
    for c in cell_map.values():
        c.water_depth += rainfall_m

def apply_river_inflow(cell_map, overflow_m):
    """Adds overflow to cells within 50m of the river centerline."""
    if overflow_m <= 0:
        return
    for c in cell_map.values():
        dist = getattr(c, "distance_to_river", float('inf'))
        if dist is not None and dist < 50.0:
            c.water_depth += overflow_m

def apply_infiltration(cell_map):
    """Subtracts water loss due to soil absorption."""
    if INFILTRATION_RATE <= 0:
        return
    loss = INFILTRATION_RATE * DT
    for c in cell_map.values():
        c.water_depth = max(0.0, c.water_depth - loss)

def run_flux_phase(cell_map):
    """
    Moves water between cells based on gravity and Manning's formula.
    """
    net_flux = {k: 0.0 for k in cell_map.keys()}

    for (i, j), src in cell_map.items():
        if src.water_depth <= 0.0001:
            continue

        eta_src = src.elevation + src.water_depth

        for di, dj in DIRECTIONS:
            ni, nj = i + di, j + dj
            if (ni, nj) not in cell_map:
                continue

            tgt = cell_map[(ni, nj)]
            eta_tgt = tgt.elevation + tgt.water_depth

            # Water only flows downhill (based on total water surface height)
            d_eta = eta_src - eta_tgt
            if d_eta <= 0:
                continue

            # Calculate distance (dx)
            dx = CELL_SIZE * (math.sqrt(2) if di != 0 and dj != 0 else 1.0)
            
            # Manning's Physics
            slope = max(d_eta / dx, 1e-6)
            h = max(src.water_depth, 1e-6)

            # Velocity (m/s)
            velocity = (1.0 / MANNING_N) * (h ** (2.0 / 3.0)) * math.sqrt(slope)
            
            # Volumetric Discharge (m3/s) = Velocity * Area (depth * width)
            discharge = velocity * (h * CELL_SIZE)

            # Volume moved (m3) and converted back to depth (m)
            flow_depth = (discharge * DT) / CELL_AREA
            
            # Stability: Limit flow so a cell doesn't 'drain' more than it has
            flow_depth = min(flow_depth, src.water_depth * 0.125)

            net_flux[(i, j)] -= flow_depth
            net_flux[(ni, nj)] += flow_depth

    # Update depth values in the object instances
    for (i, j), c in cell_map.items():
        c.water_depth = max(0.0, c.water_depth + net_flux[(i, j)])

# --- Main Entry Point ---

def execute_simulation_step(overflow_m, rainfall_m):
    """
    Main logic loop. Note: 'water_depth' is treated as a temporary 
    in-memory attribute to avoid Database FieldDoesNotExist errors.
    """
    # Fetch grid data from DB
    cells = list(GridCell.objects.only("grid_id", "elevation", "distance_to_river"))

    cell_map = {}
    for c in cells:
        c.water_depth = 0.0  # Initialize temporary memory attribute
        try:
            i, j = _parse_grid_id(c.grid_id)
            cell_map[(i, j)] = c
        except (ValueError, IndexError):
            continue

    # Pipeline
    apply_rainfall(cell_map, rainfall_m)
    apply_river_inflow(cell_map, overflow_m)
    apply_infiltration(cell_map)
    run_flux_phase(cell_map)

    # Return results as a dictionary
    return {
        c.grid_id: {
            "water_depth": round(c.water_depth, 4),
            "elevation": round(c.elevation or 0.0, 4),
            "distance_to_river": round(c.distance_to_river or 0.0, 4),
        }
        for c in cells
    }