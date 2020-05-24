from marshmallow import Schema
from marshmallow.fields import Str, Nested, List, Integer, Float, Date, Boolean
%imports%


class %table%Model(Schema):
%fieldList%
%nested%

PK_DEFAULT_VALUE = %table%Model.%pk_field%.default
