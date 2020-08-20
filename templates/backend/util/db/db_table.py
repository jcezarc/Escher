import json
from marshmallow.fields import Str, Nested, Integer, Float, Decimal

SQL_INSERT_MODE = 'SQL_INS'

class DbTable:

    existing = {}

    def  __new__(cls, schema, params={}):
        table_name = schema.__name__.replace('Model', '')
        obj = cls.existing.get(table_name)
        if not obj:
            obj = object.__new__(cls)
            obj.config(table_name, schema, params)
            cls.existing[table_name] = obj
        return obj

    def pk_numeric(self):
        field = self.pk_fields[0]
        return self.map[field] == "N"

    def config(self, table_name, schema, params):
        self.table_name = table_name
        self.alias = self.table_name[:3].lower()
        self.validator = schema()
        self.joins = {}
        field_defs = self.validator.declared_fields
        self.pk_fields = []
        self.map = {}
        self.required_fields = []
        self.new_condition_event = {
            # field : <<callback function>>
        }
        self.conditions = []
        for field_name in field_defs:
            field = field_defs[field_name]
            if field.required:
                self.required_fields.append(field_name)
            is_primary_key = field.metadata.get('primary_key')
            field_type = field.__class__.__name__
            is_number = field_type in ['Integer','Float', 'Decimal']
            if isinstance(field, Nested):
                self.add_join(field_name, field.nested, params)
                join = self.joins[field_name]
                is_number = join.pk_numeric()
            elif is_primary_key:
                self.pk_fields.append(field_name)
            if is_number:
                self.map[field_name] = "N"
            else:
                self.map[field_name] = "S"

    def default_values(self):
        return json.loads(self.validator.dumps(''))

    def statement_columns(self, dataset, is_insert=False, pattern='{field}={value}'):
        result = []
        args = {}
        if 'prefix' in pattern:
            args['prefix'] = self.alias+'.'
        for field in dataset:
            pk_in_update = not is_insert and field in self.pk_fields
            is_nested = field in self.joins and (is_insert != SQL_INSERT_MODE)
            if pk_in_update or is_nested:
                continue
            args['field'] = field
            value = dataset[field]
            if self.map[field] == "S":
                value = "'"+value+"'"
            else:
                value = str(value)
            args['value'] = value
            result.append(
                pattern.format(**args)
            )
        return result

    def add_join(self, name, schema, params):
        self.joins[name] = self.__class__(schema, params)

    def insert(self, json_data):
        raise NotImplementedError('Method "insert" not implemented!')

    def update(self, json_data):
        raise NotImplementedError('Method "update" not implemented!')

    def delete(self, values):
        raise NotImplementedError('Method "delete" not implemented!')

    def find_all(self, limit=0, filter_expr=''):
        raise NotImplementedError('Method "find_all" not implemented!')

    def find_one(self, values):
        raise NotImplementedError('Method "find_one" not implemented!')

    def contained_clause(self, field, value):
        return "='" + value + "'"

    def add_condition(self, field, value):
        func = self.new_condition_event.get(field)
        if func:
            result = func(value)
            if not result: return
        elif self.map.get(field) == "S":
            result = "{} {}".format(
                field,
                self.contained_clause(field, value)
            )
        else:
            result = '{}={}'.format(
                field,
                value
            )
        self.conditions.append(result)

    def get_conditions(self, values, only_pk=False):
        self.conditions = []
        if not values:
            return None
        if isinstance(values, dict):
            if only_pk:
                result = []
                for field in self.pk_fields:
                    value = values.get(field, '')
                    result.append(value)
                values = result
            else:
                for field in values:
                    value = values[field]
                    if isinstance(value, list):
                        value = value[0]
                    self.add_condition(field, value)
                return
        if not isinstance(values, list):
            values = [values]
        for field, value in zip(self.pk_fields, values):
            self.add_condition(field, value)
