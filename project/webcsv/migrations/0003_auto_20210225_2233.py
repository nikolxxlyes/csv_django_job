# Generated by Django 3.1.6 on 2021-02-25 20:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webcsv', '0002_auto_20210225_1745'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SchemaColumn',
            new_name='Column',
        ),
        migrations.RenameModel(
            old_name='SchemaCSV',
            new_name='CSV',
        ),
    ]
