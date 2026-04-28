import geopandas as gpd
from shapely.geometry import box
import numpy as np

minx, miny = 697756, 9312093
maxx, maxy = 702797, 9317072

cell_size = 1000  # 1km

polygons = []
ids = []

x_coords = np.arange(minx, maxx, cell_size)
y_coords = np.arange(miny, maxy, cell_size)

for i, x in enumerate(x_coords):
    for j, y in enumerate(y_coords):
        geom = box(x, y, x + cell_size, y + cell_size)
        polygons.append(geom)
        ids.append(f"{i}_{j}")

grid = gpd.GeoDataFrame({
    "grid_id": ids,
    "geometry": polygons
}, crs="EPSG:32748")

grid.to_file("grid.shp")