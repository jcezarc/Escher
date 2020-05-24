import os
from base_generator import BaseGenerator, ANGULAR_KEYS
from db_defaults import default_params

class BackendGenerator(BaseGenerator):

    def __init__(self, file_name):
        super().__init__(file_name)
        if self.json_info is None:
            return
        db_type = self.json_info['db_type']
        db_config, aux = default_params(db_type)
        db_config.update(
            self.json_info.get('db_config',{})
        )
        self.db_config = db_config
        self.dao_info = aux
        self.is_sql = aux['dao_class'] == 'SqlTable'

    def ignore_list(self):
        db_list = ['dynamo_table.py', 'mongo_table.py', 'neo4j_table.py', 'sql_table.py']
        dao = self.dao_info['import_dao_class']+'.py'
        return [i for i in db_list if i != dao]

    def on_create_dir(self, target):
        init_file = os.path.join(
            target,
            '__init__.py'
        )
        with open(init_file, 'w') as f:
            f.write(' ')
            f.close()

    def field_type(self, value):
        return {
            'str': 'Str',
            'int': 'Integer',
            'date': 'Date',
            'float': 'Float'
        }.get(value, value)

    def template_list(self):
        return {
            '':[
                ('app.py',{
                    'config_routes': 'config_routes.py',
                    'imports': 'imports.py',
                    'swagger_details': 'swagger_details.py',
                })
            ],
            'model': [
                ('comp_model.py',{
                    'fieldList': 'field_list.py',
                    'imports': 'nested_imports.py',
                    'nested': 'nested.py'
                })
            ],
            'resource':[
                'all_comp.py',
                'comp_by_id.py'
            ],
            'service': [
                'comp_service.py',
                'db_connection.py'
            ],
            'tests': ['comp_tests.py']
        }

    def util_folder(self):
        return 'util'

    def rename(self, text, table):
        if 'comp_' in text:
            return text.replace('comp_', table+'_')
        if '_comp' in text:
            return text.replace('_comp', '_'+table)
        return text

    def formated_json_config(self):
        def indentation(num_tabs):
            return '\t' * num_tabs
        result = '{'
        for key in self.db_config:
            value = self.db_config[key]
            result += '\n{}"{}": "{}",'.format(
                indentation(4),
                key,
                value
            )
        result += '\n{}{}'.format(
            indentation(3),
            '}'
        )
        return result

    def extract_table_info(self, obj):
        IMP_DAO = 'import_dao_class'
        DAO_CLS = 'dao_class'
        result = super().extract_table_info(obj)
        self.source['is_SQL'] = str(self.is_sql)
        self.source['extra'] = self.formated_json_config()
        self.source[IMP_DAO] = self.dao_info[IMP_DAO]
        self.source[DAO_CLS] = self.dao_info[DAO_CLS]
        return result
