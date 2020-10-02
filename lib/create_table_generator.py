import os
from lib.base_generator import BaseGenerator

class CreateTableGenerator(BaseGenerator):

    def root_dir(self, base_path='templates'):
        return os.path.join(
            base_path,
            'sql'
        )

    def util_folder(self):
        return ''

    def field_type(self, value):
        return {
            'str': 'VARCHAR(100)',
            'int': 'INT',
            'date': 'DATE',
            'float': 'FLOAT'
        }.get(value, value)

    def get_field_attrib(self, field_name):
        pk_field = self.source['pk_field']
        if field_name == pk_field:
            return 'PRIMARY KEY'
        return ''
    
    def template_list(self):
        return {
            '': [
                ('table.sql',{
                    'fieldList': 'field_list.sql',
                    'nested': 'nested.sql'
                })
            ]
        }
    
    def rename(self, text, table):
        return text.replace('table', table)

    def extract_table_info(self, obj):
        result = super().extract_table_info(obj)
        self.source['nested'] = obj.get('nested', {})
        return result
