from django.views.generic import ListView, View
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponseNotAllowed, JsonResponse
from django.forms import formset_factory
from .lib.generator_csv import GeneratorCSV
from .forms import SchemaForm, ColumnForm, CountForm, ColumnFormSet
from .models import Schema, CSV
from . import tasks
import json
import os

# HEROKU_FIX_FILE_CELERY
from django.conf import settings as django_setting
from django.core.files.base import ContentFile


# Create your views here.
class SchemasView(LoginRequiredMixin, ListView):
    template_name = 'webcsv/schemas.html'
    context_object_name = 'schemas'
    login_url = '/login/'
    redirect_field_name = '/next/'
    allow_empty = True

    def get_queryset(self):
        return Schema.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = 'Schemas'
        return context_data


@login_required(login_url='login')
def new_schema(request):
    prefix = 'cform'
    if request.method == 'POST':
        schema_form = SchemaForm(data=request.POST)
        SchemaColumnFormSet = formset_factory(form=ColumnForm, can_order=True,
                                              min_num=1, validate_min=True)
        formset = SchemaColumnFormSet(request.POST, prefix=prefix)
        if schema_form.is_valid():
            current_schema = schema_form.save(commit=False)
            current_schema.user = request.user
            if formset.is_valid():
                current_schema.save()
                for form in formset:
                    if form.cleaned_data:
                        new_column = form.save(commit=False)
                        new_column.schema = current_schema
                        new_column.order = form.cleaned_data['ORDER']
                        if new_column.datatype in GeneratorCSV.with_extra:
                            extra = {}
                            datatype_obj = GeneratorCSV.get_datatype_obj(new_column.datatype)
                            for param in datatype_obj.extra_params:
                                extra[param] = form.cleaned_data[param]

                            new_column.extra = extra

                        new_column.save()
                return redirect('webcsv:schemas')
    else:
        schema_form = SchemaForm()
        SchemaColumnFormSet = formset_factory(form=ColumnForm, can_order=True)
        formset = SchemaColumnFormSet(prefix=prefix)
    context = {
        'title': 'New schema',
        'schema_form': schema_form,
        'formset': formset,
        'with_extra': GeneratorCSV.with_extra,
        'base_prefix': prefix,
    }
    return render(request, 'webcsv/new_schema.html', context=context)


@login_required(login_url='login')
def delete_schema(request, schema_id):
    if request.method == 'GET':
        schema_obj = get_object_or_404(Schema, pk=schema_id, user=request.user)
        schema_obj.delete()
        return redirect('webcsv:schemas')


@login_required(login_url='login')
def edit_schema(request, schema_id):
    prefix = 'cform'
    schema_obj = get_object_or_404(Schema, pk=schema_id, user=request.user)

    if request.method == 'POST':
        schema_form = SchemaForm(data=request.POST, instance=schema_obj)
        formset = ColumnFormSet(request.POST, prefix=prefix, instance=schema_obj,
                                      hide_fields=['DELETE', 'schema', 'id'])
        if schema_form.is_valid():
            schema_form.save()
            if formset.is_valid():
                formset.save()
                return redirect('webcsv:schemas')
    else:
        schema_form = SchemaForm(instance=schema_obj)
        formset = ColumnFormSet(prefix=prefix, instance=schema_obj,
                                      hide_fields=['DELETE', 'schema', 'id'])
    context = {
        'title': 'Edit schema',
        'schema_form': schema_form,
        'formset': formset,
        'with_extra': GeneratorCSV.with_extra,
        'base_prefix': prefix,
    }
    return render(request, 'webcsv/edit_schema.html', context=context)


class SchemaDatasView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'next'

    def get(self, request, schema_id):
        schema_obj = get_object_or_404(Schema, pk=schema_id, user=request.user)
        csvs = schema_obj.csv_set.all()
        form = CountForm(initial={"count": 200})

        context = {
            'title': 'Generate csv',
            'form': form,
            'schema_obj': schema_obj,
            'csvs': csvs,
            'status_pending': 'pending',
        }
        return render(request, 'webcsv/csvs.html', context=context)


@require_POST
def generate_csv(request, schema_id):
    status = {'error_ajax': True, 'result': ''}
    if request.is_ajax():
        try:
            req_data = json.loads(request.body.decode())
            count = int(req_data['count'])
            last_number = int(req_data['lastNumber'])

            schema_obj = Schema.objects.get(pk=schema_id)
            csv_obj = CSV.create_fp(schema_obj=schema_obj)
            csv_obj.save()

            tasks.create_csv.delay(schema_id, count, csv_obj.pk)
            new_csv_template = render_to_string('webcsv/_csv.html', request=request,
                                                context={
                                                    'csv': csv_obj,
                                                    'status_pending': 'pending',
                                                    'forloop': {'counter': last_number + 1}})
            response = {
                'error_ajax': False,
                'csv_id': csv_obj.id,
                'status': 'new csv template',
                'result': new_csv_template,
            }
            return JsonResponse(response)
        except:
            status['status'] = 'Internal error'
    else:
        status['status'] = 'Not allowed method'
    return JsonResponse(status)


@require_POST
def check_csv(request, schema_id):
    status = {'error_ajax': True, 'result': ''}
    if request.is_ajax():
        try:
            req_data = json.loads(request.body.decode())
            ajax_csv = req_data['pendingCSV']
            if not isinstance(ajax_csv[0], int):
                ajax_csv = list(map(lambda i: int(i), ajax_csv))

            csvs_objs = Schema.objects.get(pk=schema_id).csv_set.all()

            ready_csv = []
            pending_csv = []
            error_csv = []
            for csv_obj in csvs_objs.filter(pk__in=ajax_csv):
                if csv_obj.ready == True:
                    ready_csv.append(csv_obj.id)
                elif csv_obj.ready == False:
                    pending_csv.append(csv_obj.id)
                elif csv_obj.ready == None:
                    error_csv.append(csv_obj.id)

            response = {
                'error_ajax': False,
                'status': 'Http ready column',
                'result': {'ready_csv': ready_csv, 'pending_csv': pending_csv, 'error_csv': error_csv},
            }
            return JsonResponse(response)
        except Exception as e:
            # print(e,type(e))
            status['status'] = 'Internal error'
    else:
        status['status'] = 'Not allowed method'
    return JsonResponse(status)


@login_required(login_url='login')
@require_GET
def download_csv(request, csv_id):
    if request.method == 'GET':
        csv_obj = get_object_or_404(CSV, pk=csv_id, schema__user=request.user)
        path = csv_obj.path

        if django_setting.HEROKU_FIX_FILE_CELERY:
            try:
                data = tasks.get_file_data.delay(path, csv_id).get(timeout=5)
                if not data:
                    raise FileNotFoundError
            except:
                return redirect('webcsv:csvs', csv_obj.schema.pk)
            data = data.encode()
            file_obj = ContentFile(data, name=csv_obj.filename).open('rb')
        else:
            try:
                file_obj = open(path, 'rb')
            except FileNotFoundError:
                csv_obj.ready = None
                csv_obj.save()
                return redirect('webcsv:csvs', csv_obj.schema.pk)

        return FileResponse(file_obj, as_attachment=True)
    return HttpResponseNotAllowed(['GET'])
