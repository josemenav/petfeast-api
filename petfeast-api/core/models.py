from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    token_ubidots = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False, null=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'


class Pet(models.Model):
    name = models.CharField(max_length=255, null=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pets"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_pet_name_per_user')
        ]


class Dispenser(models.Model):
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.CASCADE, 
        related_name='dispensers', 
        null=False
    )
    name = models.CharField(max_length=255)


class DispenserConfig(models.Model):
    dispenser = models.ForeignKey(
        Dispenser,
        on_delete=models.CASCADE,
        related_name="configurations",
        null=False
    )
    time = models.TimeField() 
    amount = models.DecimalField(max_digits=5, decimal_places=2)


class FoodHabits(models.Model):
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.CASCADE, 
        related_name='food_habits', 
        null=False
    )
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.TimeField()
