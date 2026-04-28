# FloodDigitalTwin

This repository contains the backend and digital twin logic for the FloodDigitalTwin project.

## Services Module (`backend/apps/simulation/services.py`)

The `services.py` module handles the core simulation engine steps, focusing on live data ingestion and executing the cellular automata-based flood physics across a 5x5km grid representing an area in Jakarta.

### Functions

#### `fetch_river_data()`
Fetches live water level XML data from the Jakarta flood monitoring portal (`poskobanjir.dsdadki.web.id`). It extracts and returns the water level (`TINGGI_AIR`) in centimeters specifically for the station whose name includes "P.A. KARET 1". If the request fails, it defaults to returning `0.0`.

#### `fetch_rainfall_data()`
Retrieves live weather data in JSON format from the OpenWeatherMap API using coordinates for Jakarta (Lat: -6.198, Lon: 106.810). It parses the response to find the `rain.1h` attribute, returning the rainfall amount in millimeters. It gracefully degrades by returning `0.0` upon encountering network or parsing errors.

#### `run_simulation_step()`
Executes a single time-step of the flood simulation model. The function performs several interconnected phases:

1. **State Loading:** 
   Reads all `GridCell` objects from the database and initializes a spatial dictionary for fast nearest-neighbor lookups.

2. **Data Ingestion:**
   Calls `fetch_river_data()` and `fetch_rainfall_data()` to collect environmental boundary conditions, converting rainfall to standard meters and calculating river overflow (if the river level exceeds 600cm).

3. **Inflow & Rainfall Application:**
   For cells with proximity to the river, applies overflow using an exponential decay model based on the cell's `distance_to_river`. Then, uniformly adds the measured rainfall to all cells across the grid.

4. **Flux Phase (Simplified Diffusive Wave):**
   Calculates water movement between each cell and its 8 adjacent neighbors (Moore neighborhood). Flow occurs exclusively from a higher hydraulic head to a lower head according to the equation `Flow = (Head_source - Head_target) * 0.1`.
   To strictly adhere to physical mass conservation laws, the module aggregates all calculated outflows from a source cell. If the planned total outflow exceeds the available `water_depth` in that cell, it proportionally scales down the flux to each neighbor.

5. **State Update:**
   Applies the calculated net fluxes (inflow - outflow) to each cell's `water_depth` attribute. Uses Django's `bulk_update` to push these state changes efficiently back to the PostGIS database. Returns a serialized mapping of `{grid_id: water_depth}` representing the new state of the simulation grid.

## How to Run the System

To initialize the digital twin and run the simulation, follow these steps:

1. **Initialize the Grid:**
   Generate the 5x5km grid and extract mean elevation for each cell from the local DEM file.
   ```bash
   python manage.py setup_grid
   ```

2. **Calculate River Proximity:**
   Calculate the distance of each cell to the nearest river feature (used for the inflow phase).
   ```bash
   python manage.py load_river
   ```

3. **Run a Simulation Step:**
   Execute a single iteration of the physics engine (Data Ingestion -> Simulation -> Output).
   ```bash
   python manage.py run_simulation
   ```

4. **View Results:**
   You can view the updated `water_depth` values for each cell in the Django Admin interface at `http://127.0.0.1:8000/admin/geography/gridcell/`.

## API Endpoints

The system also exposes a simple REST API for external interaction:

- **Get Simulation State:** `GET    `
  Returns a JSON mapping of all grid cells with their current `water_depth`, `elevation`, and `distance_to_river`.
- **Run Simulation Step:** `POST /api/v1/simulation/run/`
  Triggers one iteration of the simulation engine and returns the updated `water_depth` for all cells.

## Architectural Refactoring

The system has been refactored to enforce a strict separation of concerns, moving from a monolithic structure to distinct, purpose-built apps:

1. **`geography` App:**
   Remains responsible for spatial data management, specifically the `GridCell` models and PostGIS integration.

2. **`ingestion` App:**
   A dedicated application created to handle all external data acquisition. The `fetch_river_data` (XML parsing) and `fetch_rainfall_data` (JSON API) functions have been moved here from the simulation app. This cleanly separates third-party data polling from the core physics logic.

3. **`simulation` App:**
   Now focuses exclusively on the mathematical physics model and engine logic (`engine.py`). It relies on the `ingestion` app to gather boundary conditions before running the simplified diffusive wave formulas.

4. **`api` App:**
   All user-facing API routes (`SimulationRunView` and `SimulationStateView`) have been centralized here. Users now query the simulations through this dedicated API layer, decoupling the presentation and interface from the internal mechanics of the engine.
