from .datatype import *
from ...models import Schema
from ..decorators import classproperty
import pandas


class GeneratorCSV():
    registered = [FullNameType, EmailType, JobType, PhoneNumberType, DateType, TextType, IntegerType]

    def __init__(self, schema_id, count):
        self.schema_obj = Schema.objects.get(pk=schema_id)
        self.columns_objs = self.schema_obj.column_set.all()
        self.data_count = count
        self.columns = self.__columns()

    def to_csv(self, path: str = None) -> str:
        ''' Write object to a comma-separated values (csv) file using df.to_csv()

        :param path: None or str
        :return: If path defined > writing file; else > return csv string
        '''
        df = pandas.DataFrame(zip(*self.generate_new_data()), columns=self.columns)
        return df.to_csv(path, index=False, header=True, sep=self.schema_obj.delimiter,
                         quotechar=self.schema_obj.quotechar)

    def generate_new_data(self):
        iter_list = []
        for column_obj in self.columns_objs:
            datatype_obj = self.get_datatype_obj(column_obj.datatype)
            iter_column = datatype_obj.generate(self.data_count, column_obj.extra)
            iter_list.append(iter_column)

        return iter_list

    def __columns(self):
        return [column.header for column in self.columns_objs]

    @classproperty
    def choices(cls) -> list:
        choices_list = []
        for datatype in cls.registered:
            verbose_name = getattr(datatype, 'verbose_name', datatype.name)
            line = (datatype.name, verbose_name)
            choices_list.append(line)
        return choices_list

    @classproperty
    def with_extra(cls) -> list:
        return [datatype.name for datatype in cls.registered if datatype.extra]

    @classmethod
    def get_datatype_obj(self, name):
        for datatype_obj in self.registered:
            if datatype_obj.name == name:
                return datatype_obj
        raise ModuleNotFoundError('Datatype generator not found!')


__all__ = ['GeneratorCSV']
