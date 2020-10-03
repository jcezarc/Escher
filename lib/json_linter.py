import os
import json
from json.decoder import JSONDecodeError
from lib.key_names import JSON_KEYS, ANGULAR_KEYS
from lib.db_defaults import default_params

FIELD_TYPES = ['str', 'int', 'float', 'date']

ERR_INVALID_JFILE = 1
ERR_NO_TABLE_LIST = 2
ERR_TABLE_ELEMENT = 3
ERR_REQ_FIELD_LST = 4
ERR_INCORRECT_ANG = 5
ERR_REQ_FIELD_ANG = 6
ERR_FLIST_NO_DICT = 7
ERR_UNKNOWN_FTYPE = 8
ERR_ANG_NOT_IN_FL = 9
ERR_NES_ALRD_EXST = 10
ERR_PKF_NOT_IN_FL = 11
ERR_NES_MATCH_TBL = 12
ERR_NES_CIRCL_REF = 13
ERR_NO_DBTYPE_KEY = 14
ERR_UNKNOW_DBTYPE = 15
ERR_DBTYPE_NODICT = 16
ERR_DBTYPE_UPARAM = 17
ERR_DBTYPE_PVALUE = 18


LINTER_ERRRORS = {
    0: 'No errors',
    ERR_INVALID_JFILE: 'Invalid JSON file.',
    ERR_NO_TABLE_LIST: 'Missing or incorrect "tables" key.',
    ERR_TABLE_ELEMENT: 'Invalid "table" element of "tables" list.',
    ERR_REQ_FIELD_LST: 'Missing required fields',
    ERR_INCORRECT_ANG: 'Incorret value for "Angular" key',
    ERR_REQ_FIELD_ANG: 'Missing required Angular fields',
    ERR_FLIST_NO_DICT: '"field_list" is not the expected type',
    ERR_UNKNOWN_FTYPE: 'Unknown field type in "field_list"',
    ERR_ANG_NOT_IN_FL: 'Angular field is not contained in the field_list',
    ERR_NES_ALRD_EXST: 'Nested field already exists in the field_list',
    ERR_PKF_NOT_IN_FL: '"pk_field" is not contained in the field_list',
    ERR_NES_MATCH_TBL: 'Nested table does not match any given table',
    ERR_NES_CIRCL_REF: 'A nested table cannot point to itself',
    ERR_NO_DBTYPE_KEY: '"db_type" key not found',
    ERR_UNKNOW_DBTYPE: 'Unknown db_type',
    ERR_DBTYPE_NODICT: 'db_config is not the expected type',
    ERR_DBTYPE_UPARAM: 'db_config: Unknown param ',
    ERR_DBTYPE_PVALUE: 'db_config: Incorrect value in ',
}

class JSonLinter:
    def __init__(self, options):
        self.file_name = options.file_name
        try:
            self.load_json()
        except JSONDecodeError:
            self.data = None
            self.error_code = ERR_INVALID_JFILE
            return
        self.error_code = 0
        self.field_list = None
        self.summary = {}
        self.curr_table = ''
        self.curr_field = ''
        self.has_frontend = options.frontend
        self.jwt = options.jwt

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

    def foreign_table(self, nested):
        expr = self.curr_field.split('.')
        try:
            table = nested[expr[0]]
            key = expr[-1]
            flist = self.summary[table]['field_list']
            return key in flist
        except KeyError:
            return False
        

    def incompatible_fields(self, dataset, rule, nested={}):
        fl = self.field_list
        func = {
            'key_in': lambda k, d: k in fl,
            'value_in': lambda k, d: d[k] in fl,
            'key_not_in': lambda k, d: k not in fl
        }[rule]
        for key in dataset:
            if rule == 'value_in':
                value = dataset[key]
                self.curr_field = value
                if '.' in value and self.foreign_table(nested):
                    continue
            else:
                self.curr_field = key
            if not func(key, dataset):
                if self.curr_field in nested:
                    continue
                return True
        self.curr_field = ''
        return False

    def check_nesteds(self):
        for table in self.summary:
            nested = self.summary[table].get('nested') or {}
            for field in nested:
                target = nested[field]
                if target not in self.summary:
                    self.curr_field = field
                    return ERR_NES_MATCH_TBL
                if target == table:
                    self.curr_field = field
                    return ERR_NES_CIRCL_REF
        return 0

    def compare_configs(self, source, defaults):
        for key in defaults:
            if key not in source:
                source[key] = defaults[key]
        for key in source:
            if key not in defaults:
                return ERR_DBTYPE_UPARAM, key
            value = source[key]
            if not value:
                return ERR_DBTYPE_PVALUE, key
        return 0, ""

    def __get_error(self):
        def angular_data(table, nested):
            ng = table.get('Angular')
            if not isinstance(ng, dict):
                return ERR_INCORRECT_ANG
            if not self.required_fields(ng, ANGULAR_KEYS, ignore='image'):
                return ERR_REQ_FIELD_ANG
            ng = {i:ng[i] for i in ng if i != 'label-colors'}
            if self.incompatible_fields(ng, 'value_in', nested or {}):
                return ERR_ANG_NOT_IN_FL
        tables = self.data.get('tables')
        if not tables:
            return ERR_NO_TABLE_LIST
        for table in tables:
            self.curr_table = table.get('table')
            if not self.curr_table:
                return ERR_TABLE_ELEMENT
            if not self.required_fields(table, JSON_KEYS, ignore='nested'):
                return ERR_REQ_FIELD_LST
            self.field_list = table['field_list']
            if not isinstance(self.field_list, dict)\
            or not self.field_list:
                return ERR_FLIST_NO_DICT
            if not self.is_valid_types():
                return ERR_UNKNOWN_FTYPE
            nested = table.get('nested')
            if isinstance(nested, dict):
                if self.incompatible_fields(nested, 'key_not_in'):
                    return ERR_NES_ALRD_EXST
            if self.has_frontend:
                result = angular_data(table, nested)
                if result:
                    return result
            pk_field = table['pk_field']
            if self.incompatible_fields([pk_field], 'key_in'):
                return ERR_PKF_NOT_IN_FL
            self.summary[self.curr_table] = {
                'field_list': self.field_list,
                'nested': nested,
                'Angular': table.get('Angular')
            }
        nested_error = self.check_nesteds()
        if nested_error:
            return nested_error
        db_type = self.data.get('db_type')
        if not db_type:
            return ERR_NO_DBTYPE_KEY
        params_db = default_params(db_type)[0]
        if not params_db:
            return ERR_UNKNOW_DBTYPE
        db_config = self.data.get('db_config')
        if not isinstance(db_config, dict):
            return ERR_DBTYPE_NODICT
        config_error, key = self.compare_configs(db_config, params_db)
        if config_error > 0:
            self.curr_field = key
            return config_error
        return 0

    def analyze(self):
        if not self.error_code:
            self.error_code = self.__get_error()

    def error_message(self):
        result = 'Error {}: {}'.format(
            self.error_code,
            LINTER_ERRRORS[self.error_code]
        )
        if self.error_code in range(ERR_REQ_FIELD_LST, ERR_NES_CIRCL_REF+1):
            result += ' (table "{}"'.format(self.curr_table)
            if self.curr_field:
                result += ', field: "{}"'.format(self.curr_field)
            result += ')'
        if self.error_code in [ERR_DBTYPE_UPARAM, ERR_DBTYPE_PVALUE]:
            result += '"{}"'.format(self.curr_field)
        if self.error_code == ERR_UNKNOWN_FTYPE:
            result += f'\n\t valid types are:{FIELD_TYPES}'
        return result
