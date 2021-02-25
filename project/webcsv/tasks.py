from .models import CSV
from .lib.generator_csv import GeneratorCSV
from celery import shared_task


@shared_task
def create_csv(schema_id, count, csv_id):
    csv_obj = CSV.objects.get(pk=csv_id)
    try:
        GeneratorCSV(schema_id, count).to_csv(csv_obj.path)
    except Exception as e:
        # print(e,type(e))
        csv_obj.ready = None
        csv_obj.save()
    else:
        csv_obj.ready = True
        csv_obj.save()


@shared_task
def get_file_data(path,csv_id):
    try:
        with open(path, 'r') as file:
            file_obj = file.read()
        return file_obj
    except:
        csv_obj = CSV.objects.get(pk=csv_id)
        csv_obj.ready = None
        csv_obj.save()
