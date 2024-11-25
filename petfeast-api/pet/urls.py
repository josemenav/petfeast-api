"""
Urls for the pet API
"""
from django.urls import path
from pet.views import PetViewSet

app_name = 'pet'

urlpatterns = [
    path('', PetViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('update/', PetViewSet.as_view({'put': 'update', 'patch': 'patch'})),
    path('delete/', PetViewSet.as_view({'delete': 'destroy'})),
]
