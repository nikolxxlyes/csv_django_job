from mimesis import Generic, locales
from datetime import datetime, date
from ..decorators import classproperty
import random
import typing


class BaseType():
    generic = Generic(locales.EN)
    extra_params = ['from_column', 'to_column']
    extra = False

    @classproperty
    def name(cls):
        return cls.__name__.removesuffix('Type')

    @classmethod
    def generate(self, count: int, extra: dict) -> iter:
        return ()


class DateType(BaseType):
    @classmethod
    def generate(self, count: int, extra: dict) -> typing.Generator:
        now = datetime.now().timestamp()
        return (date.fromtimestamp(random.randint(0, int(now))) for _ in range(count))


class EmailType(BaseType):
    @classmethod
    def generate(self, count: int, extra: dict) -> typing.Generator:
        return (self.generic.person.email() for _ in range(count))


class FullNameType(BaseType):
    verbose_name = 'Full name'

    @classmethod
    def generate(self, count: int, extra: dict) -> typing.Generator:
        return (self.generic.person.full_name() for _ in range(count))


class PhoneNumberType(BaseType):
    verbose_name = 'Phone number'

    @classmethod
    def generate(self, count: int, extra: dict) -> typing.Generator:
        gen_mask = lambda : '38{}#######'.format(random.choice(['063', '093', '073',
                                        "039", "067", "068", "096", "097", "098",
                                        "050", "066", "095", "099"]))

        return (self.generic.person.telephone(mask=gen_mask()) for _ in range(count))


class TextType(BaseType):
    extra = True

    @classmethod
    def generate(self, count: int, extra: dict) -> typing.Generator:
        min_num = extra[self.extra_params[0]]
        max_num = extra[self.extra_params[1]]
        if min_num > max_num:
            min_num, max_num = max_num, min_num

        return (self.generic.text.text(random.randint(min_num, max_num))
                for _ in range(count))


class JobType(BaseType):
    @classmethod
    def generate(self, count: int, extra: dict) -> typing.Generator:
        return (self.generic.business.company() for _ in range(count))


class IntegerType(BaseType):
    extra = True

    @classmethod
    def generate(self, count: int, extra: dict) -> typing.Generator:
        min_num = extra[self.extra_params[0]]
        max_num = extra[self.extra_params[1]]
        if min_num > max_num:
            min_num, max_num = max_num, min_num

        return (random.randint(min_num, max_num) for _ in range(count))
