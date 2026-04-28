from django.contrib.gis.db import models

class GridCell(models.Model):
    grid_id = models.CharField(max_length=20, unique=True)
    geometry = models.PolygonField(srid=32748)
    elevation = models.FloatField(null=True)
    distance_to_river = models.FloatField(null=True)

    def __str__(self):
        return self.grid_id