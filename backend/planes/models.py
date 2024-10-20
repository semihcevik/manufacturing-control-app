from django.db import models

# Create your models here.
class Planes(models.Model):
    name = models.CharField(max_length=100)
    required_parts = models.TextField()


class PlanesInventory(models.Model):
    plane = models.ForeignKey(Planes, on_delete=models.CASCADE)
    inventory = models.IntegerField()

