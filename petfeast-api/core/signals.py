from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from datetime import datetime, timedelta
from django.utils import timezone
import pytz  
from pet.tasks import dispense_food
from core.models import DispenserConfig, Pet
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import logging

logger = logging.getLogger(__name__)

MEXICO_TZ = pytz.timezone('America/Mexico_City')

@receiver(post_save, sender=DispenserConfig)
def schedule_daily_dispense_task(sender, instance, created, **kwargs):
    logger.info(f"DispenserConfig saved, scheduling task for {instance}")
    
    # Obtener la hora del dispensador (sin zona horaria)
    time = instance.time  # Esto es un objeto `datetime.time`

    # Obtener la fecha actual en la zona horaria local
    now_local = timezone.now().astimezone(MEXICO_TZ)
    logger.info('pytz time: %s', str(now_local))

    # Crear un objeto `datetime` combinando la fecha actual con la hora del dispensador
    dispense_time_local = datetime(
        year=now_local.year,
        month=now_local.month,
        day=now_local.day,
        hour=time.hour,
        minute=time.minute,
        second=0,
        microsecond=0,
        tzinfo=MEXICO_TZ,  # Establecer la zona horaria
    )

    # Si la hora de dispensado ya pasó, programarla para el día siguiente
    if dispense_time_local <= now_local:
        dispense_time_local += timedelta(days=1)

    # Convertir dispense_time_local a UTC para programar la tarea
    dispense_time_utc = dispense_time_local.astimezone(pytz.UTC)

    # Nombre de la tarea que se ejecutará
    task_name = f'feed-pet-every-day-{instance.id}'

    # Crear o actualizar la programación de cron para la tarea
    crontab, created = CrontabSchedule.objects.get_or_create(
        minute=dispense_time_local.minute,
        hour=dispense_time_local.hour,
        day_of_week='*',  # Ejecuta todos los días
        day_of_month='*',  # Ejecuta todos los días del mes
        month_of_year='*'  # Ejecuta todos los meses
    )

    # Crear o actualizar la tarea periódica en django-celery-beat
    periodic_task, task_created = PeriodicTask.objects.get_or_create(
        name=task_name,
        defaults={
            'task': 'pet.tasks.dispense_food',
            'crontab': crontab,
            'args': f'["{instance.dispenser.pet.name}", "{instance.dispenser.name}"]',  # Celery espera una cadena JSON
        }
    )
    
    if not task_created:
        # Si la tarea ya existía, actualizamos la programación
        periodic_task.crontab = crontab
        periodic_task.save()

    logger.info(f"Task {task_name} scheduled for {dispense_time_local} local time ({dispense_time_utc} UTC)")

@receiver(pre_delete, sender=DispenserConfig)
def delete_dispense_task(sender, instance, **kwargs):
    logger.info(f"DispenserConfig deleted, removing task for {instance}")

    # Nombre de la tarea a eliminar
    task_name = f'feed-pet-every-day-{instance.id}'

    # Intentar encontrar la tarea periódica
    try:
        periodic_task = PeriodicTask.objects.get(name=task_name)
        periodic_task.delete()
        logger.info(f"Task {task_name} removed from beat schedule")
    except PeriodicTask.DoesNotExist:
        logger.warning(f"Task {task_name} not found in beat schedule")
