import osmnx as ox
from django.core.management.base import BaseCommand
from apps.geography.models import GridCell
from django.contrib.gis.geos import GEOSGeometry

class Command(BaseCommand):
    help = 'Fetches official Ciliwung river geometry from OSM and updates grid distances'

    def handle(self, *args, **options):

        center_point = (-6.198, 106.818) 
        
        self.stdout.write("Fetching river geometry from OpenStreetMap...")
        
        tags = {'waterway': ['river', 'canal']}
        river_gdf = ox.features_from_point(center_point, tags, dist=3000)

        river_gdf = river_gdf.to_crs("EPSG:32748")
        
        combined_river_geom = river_gdf.unary_union
        django_river_geom = GEOSGeometry(combined_river_geom.wkt, srid=32748)

        self.stdout.write("Updating grid cell distances...")

        cells = GridCell.objects.all()
        for cell in cells:
            dist = cell.geometry.centroid.distance(django_river_geom)
            cell.distance_to_river = dist
            cell.save()

        self.stdout.write(self.style.SUCCESS(f"Official river loaded. Segments found: {len(river_gdf)}"))