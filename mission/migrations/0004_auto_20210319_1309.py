# Generated by Django 3.1.5 on 2021-03-19 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mission', '0003_mission_missionbonusreward'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='description',
            field=models.TextField(verbose_name='Mission description'),
        ),
    ]
