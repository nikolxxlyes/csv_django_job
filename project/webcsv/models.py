from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
import os.path


# Create your models here.
class Schema(models.Model):
    DELIMITER_CHOICES = (
        (',', "Comma ( , )"),
        (';', "Semicolon ( ; )"),
        ('\t', "Tab ( \\t )"),
        ('|', "Pipe ( | )"),
    )
    QUOTE_CHOICES = (
        ('"', 'Double-quote ( " )'),
        ("'", 'Quote ( \' )'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    name = models.CharField(max_length=100, verbose_name='Name')
    delimiter = models.CharField(max_length=1, choices=DELIMITER_CHOICES,
                                 default=DELIMITER_CHOICES[0], verbose_name='Column separator')
    quotechar = models.CharField(max_length=1, choices=QUOTE_CHOICES,
                                 default=QUOTE_CHOICES[0], verbose_name='String character')
    modified = models.DateTimeField(auto_now=True, verbose_name='Modified')

    class Meta:
        verbose_name = 'Schema'
        verbose_name_plural = 'Schemas'

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        for csv_obj in self.csv_set.only('path'):
            try:
                os.remove(csv_obj.path)
            except FileNotFoundError:
                pass
        return super().delete(*args, **kwargs)


class Column(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, verbose_name='Schema ID')
    header = models.CharField(max_length=100, verbose_name='Column name')
    datatype = models.CharField(max_length=100, verbose_name='Type')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Order')
    extra = models.JSONField(null=True, blank=True, verbose_name='Extra')
    modified = models.DateTimeField(auto_now=True, verbose_name='Modified')

    class Meta:
        verbose_name = 'Schema column'
        verbose_name_plural = 'Schema columns'
        ordering = ['order', 'header']

    def __str__(self):
        return f'[{self.order}] {self.header}'


class CSV(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, verbose_name='Schema ID')
    path = models.CharField(max_length=100, verbose_name='Path')
    ready = models.BooleanField(default=False, null=True, db_index=True, verbose_name='Status')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        verbose_name = 'Schema CSV file'
        verbose_name_plural = 'Schema CSV files'

    def __str__(self):
        return self.path

    @classmethod
    def create_fp(cls, schema_obj):
        timestamp = int(datetime.now().timestamp())
        schema_name = schema_obj.name.strip().replace(' ', '_').lower()
        filename = f'{schema_name}_{timestamp}.csv'
        path = os.path.join(settings.MEDIA_ROOT, filename)
        return cls(schema=schema_obj, path=path)

    @property
    def filename(self):
        return os.path.basename(self.path)
