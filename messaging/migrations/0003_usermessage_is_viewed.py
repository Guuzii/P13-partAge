# Generated by Django 3.1.5 on 2021-03-11 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0002_usermessage_is_support'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermessage',
            name='is_viewed',
            field=models.BooleanField(default=False),
        ),
    ]
