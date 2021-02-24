from .models import Schema, SchemaCSV
from django.template.defaultfilters import stringformat
from .csv_datatypes import get_generator_by_dbcolumn as get_gen
from celery import shared_task
import pandas
import csv


@shared_task
def create_csv(schema_id, count, csv_id):
    try:
        genetate_csv(schema_id, count, csv_id)
        update_status_csv(csv_id)
    except Exception as e:
        # print(e,type(e))
        SchemaCSV.objects.get(pk=csv_id).delete()

def genetate_csv(schema_id, count, csv_id):
    schema_obj = Schema.objects.get(pk=schema_id)
    columns_obj = schema_obj.schemacolumn_set.all()
    columns = [column.header for column in columns_obj]

    data = {column.header: get_gen(column).generate(count, column.extra)
            for column in columns_obj}
    df = pandas.DataFrame(data, columns=columns)
    csv_obj = SchemaCSV.objects.get(pk=csv_id)
    df.to_csv(csv_obj.path, index=False, header=True, sep=schema_obj.delimiter, quotechar=schema_obj.quotechar,
              quoting=csv.QUOTE_MINIMAL)


def update_status_csv(csv_id):
    csv_obj = SchemaCSV.objects.get(pk=csv_id)
    csv_obj.ready = True
    csv_obj.save()
