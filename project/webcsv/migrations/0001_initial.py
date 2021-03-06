# Generated by Django 3.1.6 on 2021-02-22 01:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Schema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('delimiter', models.CharField(choices=[(',', 'Comma ( , )'), (';', 'Semicolon ( ; )'), ('\t', 'Tab ( \\t )'), ('|', 'Pipe ( , )')], default=(',', 'Comma ( , )'), max_length=1, verbose_name='Column separator')),
                ('quotechar', models.CharField(choices=[('"', 'Double-quote ( " )'), ("'", "Quote ( ' )")], default=('"', 'Double-quote ( " )'), max_length=1, verbose_name='String character')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Schema',
                'verbose_name_plural': 'Schemas',
            },
        ),
        migrations.CreateModel(
            name='SchemaCSV',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=100, verbose_name='Path')),
                ('ready', models.BooleanField(default=False, verbose_name='Status')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('schema', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webcsv.schema', verbose_name='Schema ID')),
            ],
            options={
                'verbose_name': 'Schema CSV file',
                'verbose_name_plural': 'Schema CSV files',
            },
        ),
        migrations.CreateModel(
            name='SchemaColumn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=100, verbose_name='Column name')),
                ('datatype', models.CharField(max_length=100, verbose_name='Type')),
                ('order', models.SmallIntegerField(db_index=True, default=0, verbose_name='Order')),
                ('extra', models.JSONField(blank=True, null=True, verbose_name='Extra')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('schema', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webcsv.schema', verbose_name='Schema ID')),
            ],
            options={
                'verbose_name': 'Schema column',
                'verbose_name_plural': 'Schema columns',
                'ordering': ['order', 'header'],
            },
        ),
    ]
