from marshmallow import Schema
from marshmallow.fields import Str, Nested, List, Integer, Float, Date, Boolean
%imports%

PK_DEFAULT_VALUE = %default%

class %table%Model(Schema):
    %pk_field% = %field_type%(primary_key=True, default=PK_DEFAULT_VALUE, required=True)
%field_list%
%nested%
