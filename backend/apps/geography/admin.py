from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from .models import GridCell

@admin.register(GridCell)
class GridCellAdmin(gis_admin.GISModelAdmin):
    list_display = ('grid_id', 'elevation', 'distance_to_river')