# Generated by Django 3.2.25 on 2024-11-26 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_pet_unique_pet_name_per_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='token_ubidots',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
