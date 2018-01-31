# coding=utf-8
"""ORM package
"""
from __future__ import absolute_import, division, print_function, with_statement

import json
import re
import uuid
import functools

from sqlalchemy import Column
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.types import TypeDecorator, String, CHAR

__author__ = "Yihang Yang"
__copyright__ = "Copyright 2015, Kanjian"
__credits__ = ["Yihang Yang"]
__license__ = "Apache"
__version__ = "2.0"
__maintainer__ = "Yihang Yang"
__email__ = "lianghuihui@kanjian.com"
__status__ = "Production"

__all__ = ["ORMBase", "JSONEncodedDict", "GUID", "guid", "FullColumn"]


# pylint: disable=too-few-public-methods

def _camel_case_2_snake_case(name):
    """Convert CamelCase string to snake_case string.

    Reference:
        http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case

    P.s. There is a pre-compiled version that can speed up re execution.
    """
    tmp = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', tmp).lower()


@as_declarative()
class ORMBase(object):
    """

    Reference:
        https://github.com/zzzeek/sqlalchemy/blob/master/lib/sqlalchemy/ext/declarative/api.py#L336
    """
    __table_args__ = dict(mysql_charset="utf8", )  # 默认utf-8, nullable=False

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return "kanjian_{}".format(_camel_case_2_snake_case(cls.__name__))  # pylint: disable=no-member


class JSONEncodedDict(TypeDecorator):  # pylint: disable=abstract-method
    """copy from http://docs.sqlalchemy.org/en/latest/core/custom_types.html#marshal-json-strings

    Represents an immutable structure as a json-encoded string.
    Usage::

        JSONEncodedDict(255)
    """
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class GUID(TypeDecorator):  # pylint: disable=abstract-method
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(36), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))


def guid():
    """default func for GUID"""
    return str(uuid.uuid4())


FullColumn = functools.partial(Column, nullable=False, )  # pylint: disable=invalid-name
