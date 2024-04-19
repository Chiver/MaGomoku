from django.db import models

# Create your models here.

class PlaceEvent(models.Model):
    prev = models.TextField()
    curr = models.TextField()
    x = models.IntegerField()
    y = models.IntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    consumed = models.BooleanField(default=False)
