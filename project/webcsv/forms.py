from django import forms
from .models import Schema, Column
from .lib.generator_csv import GeneratorCSV


# Create your forms here.
class SchemaForm(forms.ModelForm):
    class Meta:
        model = Schema
        fields = ['name', 'delimiter', 'quotechar']


class ColumnForm(forms.ModelForm):
    from_column = forms.IntegerField(min_value=0, label='From', required=False)
    to_column = forms.IntegerField(min_value=0, label='To', required=False)
    datatype = forms.ChoiceField(choices=GeneratorCSV.choices, label='Type')

    class Meta:
        model = Column
        fields = ['header', 'datatype', 'from_column', 'to_column']


class CountForm(forms.Form):
    count = forms.IntegerField(min_value=0, label='Rows')


BaseFormSet = forms.inlineformset_factory(parent_model=Schema, model=Column, form=ColumnForm,
                                          can_order=True, can_delete=True,
                                          extra=1, min_num=1, validate_min=True)


class ColumnFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        hide_fields = kwargs.pop('hide_fields') if 'hide_fields' in kwargs else []
        super().__init__(*args, **kwargs)

        for form in self.forms:
            form.schema = kwargs['instance']
            self.hide_formset_fields(form, hide_fields)

            if not form.data and form.instance and form.instance.extra:
                self.unpack_extra_params(form)

    def is_valid(self, *args, **kwargs):
        valid = super().is_valid(*args, **kwargs)

        for form in self.forms:
            if form.cleaned_data:
                self.pack_extra_params(form)
                form.instance.order = form.cleaned_data['ORDER']
        return valid

    def hide_formset_fields(self, form, hide_fields):
        for hfield in hide_fields:
            form[hfield].hidden = True
            form[hfield].css_classes = lambda: 'sr-only'
            form[hfield].field.required = False

    def pack_extra_params(self, form):
        new_column = form.instance
        datatype = new_column

        extra = {}
        if datatype in GeneratorCSV.with_extra:
            datatype_obj = GeneratorCSV.get_datatype_obj(datatype)
            for param in datatype_obj.extra_params:
                extra[param] = form.cleaned_data[param]

        new_column.extra = extra

    def unpack_extra_params(self, form):
        datatype = form.instance.datatype
        if datatype in GeneratorCSV.with_extra:
            datatype_obj = GeneratorCSV.get_datatype_obj(datatype)
            for param in datatype_obj.extra_params:
                form.fields[param].initial = form.instance.extra[param]
