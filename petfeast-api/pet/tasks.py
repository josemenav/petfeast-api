from celery import shared_task
from core.models import Pet, Dispenser
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import logging
from app.celery import celery_app

logger = logging.getLogger(__name__)

@shared_task(queue='celery')
def dispense_food(pet_name, dispenser_name):
    try:
        pet = Pet.objects.get(name=pet_name)
        dispenser = Dispenser.objects.get(name=dispenser_name, pet=pet)
        logger.info(f"Alimentando a {pet.name} con el dispensador {dispenser.name} a las {timezone.now()}!")
        logger.info(f"Alimentado {pet_name} con {dispenser_name} a las {timezone.now()}")
        return
    except ObjectDoesNotExist as e:
        logger.info(f"Error: {e}")
        return f"Error al intentar alimentar a {pet_name} con {dispenser_name}. No se encontró la mascota o el dispensador."
