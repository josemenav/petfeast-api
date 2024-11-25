from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Pet, DispenserConfig, Dispenser
from pet.serializers import PetSerializer
from pet.tasks import dispense_food
import logging

class PetViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        pets = Pet.objects.filter(user=request.user)
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = PetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request):
        pet_name = request.data.get('name')
        if not pet_name:
            return Response({'error': 'Pet name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pet = Pet.objects.get(user=request.user, name=pet_name)
        except Pet.DoesNotExist:
            return Response({'error': 'Pet not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PetSerializer(pet, data=request.data, partial=False, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pet_name = request.data.get('name')
        if not pet_name:
            return Response({'error': 'Pet name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pet = Pet.objects.get(user=request.user, name=pet_name)
        except Pet.DoesNotExist:
            return Response({'error': 'Pet not found'}, status=status.HTTP_404_NOT_FOUND)

        dispenser_config_data = request.data.get('dispenser_config', None)
        if dispenser_config_data:
            dispenser_name = dispenser_config_data.get('dispenser_name')
            feeding_time = dispenser_config_data.get('feeding_time')

            if not dispenser_name or not feeding_time:
                return Response({'error': 'Dispenser name and feeding time are required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                dispenser = Dispenser.objects.get(name=dispenser_name)
            except Dispenser.DoesNotExist:
                return Response({'error': 'Dispenser not found'}, status=status.HTTP_404_NOT_FOUND)

            dispenser_config, created = DispenserConfig.objects.update_or_create(
                pet=pet,
                dispenser=dispenser,
                defaults={'time': feeding_time}
            )

        serializer = PetSerializer(pet, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request):
        pet_name = request.data.get('name')
        if not pet_name:
            return Response({'error': 'Pet name is required'}, status=status.HTTP_400_BAD_REQUEST)

        pets = Pet.objects.filter(user=request.user, name=pet_name)
        if not pets.exists():
            return Response({'error': 'Pet not found'}, status=status.HTTP_404_NOT_FOUND)

        pets_deleted = pets.count()
        pets.delete()

        return Response(
            {'message': f'{pets_deleted} pet(s) named {pet_name} deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
