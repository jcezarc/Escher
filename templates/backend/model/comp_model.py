from marshmallow import Schema
from marshmallow.fields import Str, Nested, List, Integer, Float, Date, Boolean
%nested_imports%

PK_DEFAULT_VALUE = %default%

class %table%Model(Schema):
%fieldList%
%nested%
