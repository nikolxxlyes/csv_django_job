from mimesis import Person, Generic, locales
from datetime import date, datetime
import random


class BaseType():
    generic = Generic(locales.EN)
    extra = False
    extra_params = {'from_column': 'min', 'to_column': 'max'}

    @classmethod
    @property
    def name(cls):
        return cls.__name__.removesuffix('Type')

    @classmethod
    def generate(self, count: int, extra: dict = {}) -> list:
        return []


class DateType(BaseType):
    to_date = date.fromtimestamp

    @classmethod
    def generate(self, count: int, extra: dict = {}) -> list:
        now = datetime.now().timestamp()
        return [self.to_date(random.randint(0, int(now))) for _ in range(count)]


class EmailType(BaseType):
    @classmethod
    def generate(self, count: int, extra: dict = {}) -> list:
        res = [Person().email() for _ in range(count)]
        return res


class FullNameType(BaseType):
    verbose_name = 'Full name'

    @classmethod
    def generate(self, count: int, extra: dict = {}) -> list:
        res = [Person().full_name() for _ in range(count)]
        return res


class PhoneNumberType(BaseType):
    verbose_name = 'Phone number'

    @classmethod
    def generate(self, count: int, extra: dict = {}) -> list:
        r_code = lambda: random.choice(['063', '093', '073',
                                        "039", "067", "068", "096", "097", "098",
                                        "050", "066", "095", "099"])

        return [Person().telephone(mask='38{}#######').format(r_code()) for _ in range(count)]


class TextType(BaseType):
    extra = True

    @classmethod
    def generate(self, count: int, extra: dict = {}) -> list:
        min = extra['min']
        max = extra['max']
        if min > max:
            min, max = max, min
        return [self.generic.text.text(random.randint(min, max)) for _ in range(count)]


class JobType(BaseType):
    @classmethod
    def generate(self, count: int, extra: dict = {}) -> list:
        return [self.generic.business.company() for _ in range(count)]


class IntegerType(BaseType):
    extra = True

    @classmethod
    def generate(self, count: int, extra: dict = {}) -> list:
        min = extra['min']
        max = extra['max']
        if min > max:
            min, max = max, min

        return [random.randint(min, max) for _ in range(count)]
