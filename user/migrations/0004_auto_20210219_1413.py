# Generated by Django 3.1.5 on 2021-02-19 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20210219_1403'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='id_wallet',
            new_name='wallet',
        ),
    ]
