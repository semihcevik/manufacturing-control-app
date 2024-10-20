
from django.contrib.auth.models import AbstractUser
from django.db import models
from departments.models import Departments

class CustomUser(AbstractUser):
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username
