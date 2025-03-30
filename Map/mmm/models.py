import warnings
warnings.filterwarnings("ignore")
from django.contrib.gis.db import models


class PointData(models.Model):
    gid = models.BigIntegerField(primary_key=True)
    x = models.FloatField()
    y = models.FloatField()
    direction = models.IntegerField()
    velocity = models.IntegerField()
    dt = models.DateTimeField()
    status = models.IntegerField()
    vehicle_id = models.BigIntegerField()
    vehicle_class = models.CharField(max_length=2)
    zone_id = models.BigIntegerField()
    trip_id = models.BigIntegerField()
    fid = models.BigIntegerField()
    ts_insert = models.DateTimeField()

    class Meta:
        db_table = '"data"."data"'  # Schema "data", Table "data"
        indexes = [
            models.Index(fields=["vehicle_id"]),
            models.Index(fields=["trip_id"]),
            models.Index(fields=["zone_id"])
        ]

    def __str__(self):
        return f"PointData {self.gid} - {self.vehicle_id} at ({self.velocity}, {self.zone_id})"
