from .datatype import *

allowed = [FullNameType, EmailType, JobType, PhoneNumberType, DateType, TextType, IntegerType]

choices = [(t.name, getattr(t, 'verbose_name', t.name)) for t in allowed]
with_extra = {t.name: t for t in allowed if t.extra}
generator_by_name = {t.name: t for t in allowed}


def get_generator_by_dbcolumn(dbcolumn, db_column_name='datatype'):
    name = getattr(dbcolumn, db_column_name)
    return generator_by_name[name]


__all__ = ['allowed', 'choices', 'with_extra', "generator_by_name", "get_generator_by_dbcolumn"]
