from django.db import models
from planes.models import Planes


# Create your models here.
class AssemblyHistory(models.Model):
    used_parts = models.TextField()
    date = models.DateField(auto_now_add=True)
    plane =  models.ForeignKey(Planes, on_delete=models.CASCADE)

