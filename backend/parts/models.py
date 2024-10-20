from django.db import models
from departments.models import Departments

from planes.models import Planes

# Create your models here.
class Parts(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)

class PartsInventory(models.Model):
    plane = models.ForeignKey(Planes, on_delete=models.CASCADE)
    part = models.ForeignKey(Parts, on_delete=models.CASCADE)
    inventory = models.IntegerField()