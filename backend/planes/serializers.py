# serializers.py

from rest_framework import serializers
from .models import Planes, PlanesInventory


class PlanesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planes
        fields = ['id', 'name', 'required_parts']

class PlanesInventorySerializer(serializers.ModelSerializer):
    plane = PlanesSerializer()

    class Meta:
        model = PlanesInventory
        fields = ['id', 'plane', 'inventory']
