"""
Serializer for pet API
"""
from rest_framework import serializers
from core.models import (
    Pet,
    Dispenser, 
    DispenserConfig,
    FoodHabits
)

class DispenserConfigSerializer(serializers.ModelSerializer):
    time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
    class Meta:
        model = DispenserConfig
        fields = ['id', 'time', 'amount']
        read_only_fields = ['id']


class DispenserSerializer(serializers.ModelSerializer):
    configurations = DispenserConfigSerializer(many=True)

    class Meta:
        model = Dispenser
        fields = ['id', 'name', 'configurations']
        read_only_fields = ['id']

    def create(self, validated_data):
        configurations_data = validated_data.pop('configurations', [])
        dispenser = Dispenser.objects.create(**validated_data)
        for config_data in configurations_data:
            DispenserConfig.objects.create(dispenser=dispenser, **config_data)
        return dispenser


class PetSerializer(serializers.ModelSerializer):
    dispensers = DispenserSerializer(many=True)

    class Meta:
        model = Pet
        fields = ['id', 'name', 'dispensers']
        read_only_fields = ['id']

    def create(self, validated_data):
        dispensers_data = validated_data.pop('dispensers', [])
        pet = Pet.objects.create(**validated_data)
        for dispenser_data in dispensers_data:
            configurations_data = dispenser_data.pop('configurations', [])
            dispenser = Dispenser.objects.create(pet=pet, **dispenser_data)
            for config_data in configurations_data:
                DispenserConfig.objects.create(dispenser=dispenser, **config_data)
        return pet
