import os
import json
from json.decoder import JSONDecodeError
from key_names import JSON_KEYS, ANGULAR_KEYS
from db_defaults import default_params

FIELD_TYPES = ['str', 'int', 'float', 'date']

LINTER_ERRRORS = {
    0: 'No errors',
    1: 'Invalid JSON file.',
    2: '"tables" key not found',
    3: 'Missing required fields',
    4: 'Incorret value for "Angular" key',
    5: 'Missing required Angular fields',
    6: '"field_list" is not the expected type',
    7: 'Unknown field type in "field_list"',
    8: 'Angular field is not contained in the field_list',
    9: 'Nested field is not contained in the field_list',
    10: '"pk_field" is not contained in the field_list',
    11: 'Nested table does not match any given table',
    12: 'A nested table cannot point to itself',
    13: '"db_type" key not found',
    14: 'Unknown db_type',
    15: 'db_config: Unknown param ',
    16: 'db_config: Incorrect value in ',
}

class JSonLinter:
    def __init__(self, file_name):
        self.file_name = os.path.splitext(file_name)[0]
        try:
            self.load_json()
        except JSONDecodeError:
            self.data = None
            self.error_code = 1
            return
        self.error_code = 0
        self.field_list = None
        self.table_names = []
        self.nested_list = {}
        self.curr_table = ''
        self.curr_field = ''

    def load_json(self):
        with open(self.file_name+'.json', 'r') as f:
            text = f.read()
            f.close()
        self.data = json.loads(text)

    def required_fields(self, obj, keys, ignore):
        for key in keys:
            if key == ignore:
                continue
            if key not in obj:
                self.curr_field = key
                return False
        return True

    def is_valid_types(self):
        for field in self.field_list:
            value = self.field_list[field]
            if value not in FIELD_TYPES:
                self.curr_field = field
                return False
        return True

    def compatible_fields(self, dataset, from_value):
        for key in dataset:
            if from_value:
                value = dataset[key]
                if not isinstance(value, str):
                    continue
                if value not in self.field_list:
                    self.curr_field = value
                    return False
            elif key not in self.field_list:
                self.curr_field = key
                return False
        return True

    def check_nesteds(self):
        for table in self.nested_list:
            nested = self.nested_list[table]
            for field in nested:
                target = nested[field]
                if target not in self.table_names:
                    self.curr_field = field
                    return 11
                if target == table:
                    self.curr_field = field
                    return 12
        return 0

    def compare_configs(self, source, defaults):
        for key in defaults:
            if key not in source:
                source[key] = defaults[key]
        for key in source:
            if key not in defaults:
                return 15, key
            value = source[key]
            if not value:
                return 16, key
        return 0, ""

    def __get_error(self):
        tables = self.data.get('tables')
        if not tables:
            return 2
        for table in tables:
            self.curr_table = table['table']
            if not self.required_fields(table, JSON_KEYS, 'nested'):
                return 3
            angular_data = table.get('Angular')
            if not isinstance(angular_data, dict):
                return 4
            if not self.required_fields(angular_data, ANGULAR_KEYS, 'image'):
                return 5
            self.field_list = table['field_list']
            if not isinstance(self.field_list, dict):
                return 6
            if not self.is_valid_types():
                return 7
            if not self.compatible_fields(angular_data, True):
                return 8
            nested = table.get('nested')
            if isinstance(nested, dict):
                if not self.compatible_fields(nested, False):
                    return 9
                self.nested_list[self.curr_table] = nested
            pk_field = table['pk_field']
            if not self.compatible_fields([pk_field], False):
                return 10
            self.table_names.append(self.curr_table)
        nested_error = self.check_nesteds()
        if nested_error:
            return nested_error  ##--- 11 or 12
        db_type = self.data.get('db_type')
        if not db_type:
            return 13
        params_db = default_params(db_type)[0]
        if not params_db:
            return 14
        db_config = self.data.get('db_config', {})
        config_error, key = self.compare_configs(db_config, params_db)
        if config_error > 0:
            self.curr_field = key
            return config_error #--- 15 or 16
        return 0

    def analyze(self):
        if not self.error_code:
            self.error_code = self.__get_error()

    def error_message(self):
        result = 'Error {}: {}'.format(
            self.error_code,
            LINTER_ERRRORS[self.error_code]
        )
        if self.error_code in range(3, 13):
            result += ' (table "{}"'.format(self.curr_table)
            if self.curr_field:
                result += ', field: "{}"'.format(self.curr_field)
            result += ')'
        if self.error_code > 14:
            result += '"{}"'.format(self.curr_field)
        return result
