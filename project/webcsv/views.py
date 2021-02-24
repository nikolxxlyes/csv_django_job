from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponseNotAllowed, HttpResponse, JsonResponse
from django.views.generic import ListView, View
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Schema, SchemaCSV, SchemaColumn
from .forms import SchemaForm, SchemaColumnForm, CountForm, SchemaColumnFormSet
from . import csv_datatypes as csv_data
from django.forms import formset_factory, inlineformset_factory, modelformset_factory
from django.views.generic.edit import UpdateView
from . import tasks
import json
from django.template.loader import render_to_string


# Create your views here.
class SchemasView(LoginRequiredMixin, ListView):
    template_name = 'webcsv/schemas.html'
    context_object_name = 'schemas'
    login_url = '/login/'
    redirect_field_name = '/next/'
    allow_empty = True

    def get_queryset(self):
        return Schema.objects.filter(user=self.request.user)


@login_required(login_url='login')
def new_schema(request):
    prefix = 'cform'
    if request.method == 'POST':
        schema_form = SchemaForm(data=request.POST)
        SchemaColumnFormSet = formset_factory(form=SchemaColumnForm, can_order=True,
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
                        if new_column.datatype in csv_data.with_extra:
                            new_column.extra = {}
                            for k_form, k_model in csv_data.with_extra[new_column.datatype].extra_params.items():
                                new_column.extra[k_model] = form.cleaned_data[k_form]
                        new_column.save()
                return redirect('webcsv:schemas')
    else:
        schema_form = SchemaForm()
        SchemaColumnFormSet = formset_factory(form=SchemaColumnForm, can_order=True)
        formset = SchemaColumnFormSet(prefix=prefix)
    context = {
        'schema_form': schema_form,
        'formset': formset,
        'with_extra': {'value': list(csv_data.with_extra.keys())},
        'base_prefix': {'value': prefix},
    }
    return render(request, 'webcsv/new_schema.html', context=context)


@login_required(login_url='login')
def delete_schema(request, schema_id):
    if request.method == 'GET':
        get_object_or_404(Schema, pk=schema_id, user=request.user).delete()
        return redirect('webcsv:schemas')


@login_required(login_url='login')
def edit_schema(request, schema_id):
    prefix = 'cform'
    schema_obj = get_object_or_404(Schema, pk=schema_id, user=request.user)

    if request.method == 'POST':
        schema_form = SchemaForm(data=request.POST, instance=schema_obj)
        formset = SchemaColumnFormSet(request.POST, prefix=prefix, instance=schema_obj,
                                      hide_fields=['DELETE', 'schema', 'id'])
        if schema_form.is_valid():
            schema_form.save()
            if formset.is_valid():
                formset.save()
                return redirect('webcsv:schemas')
    else:
        schema_form = SchemaForm(instance=schema_obj)
        formset = SchemaColumnFormSet(prefix=prefix, instance=schema_obj,
                                      hide_fields=['DELETE', 'schema', 'id'])
    context = {
        'schema_form': schema_form,
        'formset': formset,
        'with_extra': {'value': list(csv_data.with_extra.keys())},
        'base_prefix': {'value': prefix},
    }
    return render(request, 'webcsv/edit_schema.html', context=context)


class SchemaDatasView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'next'

    def get(self, request, schema_id):
        schema = get_object_or_404(Schema, pk=schema_id, user=request.user)
        csvs = schema.schemacsv_set.all()
        form = CountForm(initial={"count": 500})
        context = {
            'title': 'Generate csv',
            'form': form,
            'schema': {'value': schema.pk, 'name': schema.name},
            'csvs': csvs,
            'status_id_': 'status-csv-',
            'status_id': {'frmt': 'status-csv-'},
        }
        return render(request, 'webcsv/csvs.html', context=context)


@require_POST
def generate_csv(request, schema_id):
    status = {'error': True, 'result': ''}
    if request.is_ajax():
        try:
            req_data = json.loads(request.body.decode())
            count = int(req_data['count'])
            last_number = int(req_data['lastNumber'])

            schema_obj = Schema.objects.get(pk=schema_id)
            csv_obj = SchemaCSV.create_fp(schema_obj=schema_obj)
            csv_obj.save()
            tasks.create_csv.delay(schema_id, count, csv_obj.pk)
            template = render_to_string('webcsv/_csv.html', request=request,
                                        context={
                                            'csv': csv_obj,
                                            'status_id': {'frmt': 'status-csv-'},
                                            'forloop': {'counter': last_number + 1}})
            response = {
                'error': False,
                'status': 'Http column',
                'result': template,
            }
            return JsonResponse(response)
        except Exception as e:
            status['status'] = '{} {}'.format(type(e), e)
    else:
        status['status'] = 'Not allowed method'
    return JsonResponse(status)


@require_POST
def check_csv(request, schema_id):
    status = {'error': True, 'result': ''}
    if request.is_ajax():
        try:
            req_data = json.loads(request.body.decode())
            wait_ids = req_data['pendingCSV']

            db_wait_ids = Schema.objects.get(pk=schema_id).schemacsv_set.filter(ready=False).only("id")
            ready_csv = [csv_id for csv_id in wait_ids if not int(csv_id) in db_wait_ids]
            response = {
                'error': False,
                'status': 'Http ready column',
                'result': {'ready': ready_csv},
            }
            return JsonResponse(response)
        except Exception as e:
            status['status'] = '{} {}'.format(type(e), e)
    else:
        status['status'] = 'Not allowed method'
    return JsonResponse(status)


@login_required(login_url='login')
@require_GET
def download_csv(request, csv_id):
    if request.method == 'GET':
        csv_odj = get_object_or_404(SchemaCSV, pk=csv_id, schema__user=request.user)
        path = csv_odj.path
        return FileResponse(open(path, 'rb'), as_attachment=True)
    return HttpResponseNotAllowed(['GET'])
