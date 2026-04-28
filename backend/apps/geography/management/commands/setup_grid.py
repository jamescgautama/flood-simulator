import os
import numpy as np
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon
from rasterstats import zonal_stats
from apps.geography.models import GridCell

class Command(BaseCommand):
    help = 'Generates 5x5 grid and extracts elevation from DEM'

    def handle(self, *args, **options):
        minx, miny = 697756, 9312093
        maxx, maxy = 702797, 9317072
        cell_size = 1000 
        
        dem_path = '/home/james/Programming/4sem/flooddigitaltwin/backend/data/dem_utm.tif'
        
        self.stdout.write("Generating grid and extracting elevation...")

        x_coords = np.arange(minx, minx + (5 * cell_size), cell_size)
        y_coords = np.arange(miny, miny + (5 * cell_size), cell_size)

        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                coords = (
                    (x, y),
                    (x + cell_size, y),
                    (x + cell_size, y + cell_size),
                    (x, y + cell_size),
                    (x, y)
                )
                poly = Polygon(coords, srid=32748)
                
                stats = zonal_stats(poly.wkt, dem_path, stats="mean")
                mean_elev = stats[0]['mean'] if stats[0]['mean'] else 0

                grid_id = f"cell_{i}_{j}"
                GridCell.objects.update_or_create(
                    grid_id=grid_id,
                    defaults={
                        'geometry': poly,
                        'elevation': mean_elev,
                        'water_depth': 0.0
                    }
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated 25 grid cells!'))