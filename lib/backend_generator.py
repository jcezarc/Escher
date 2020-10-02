import os
from lib.base_generator import BaseGenerator
from lib.db_defaults import default_params, formated_json

class BackendGenerator(BaseGenerator):

    def __init__(self, linter):
        super().__init__(linter)
        db_type = self.json_info['db_type']
        db_config, aux = default_params(db_type)
        db_config.update(
            self.json_info.get('db_config',{})
        )
        self.db_config = db_config
        self.dao_info = aux

    def ignore_list(self):
        db_list = [
            'dynamo_table.py',
            'mongo_table.py',
            'neo4j_table.py',
            'sql_table.py',
            'lite_table.py'
        ]
        dao = self.dao_info['import_dao_class']+'.py'
        result = [i for i in db_list if i != dao]
        if dao not in db_list[-2:]:
            result.append('fmt_table.py')
        return result

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
                }),
                'requirements.txt'
            ],
            'model': [
                ('comp_model.py',{
                    'fieldList': 'field_list.py',
                    'nested_imports': 'nested_imports.py',
                    'nested': 'nested.py'
                })
            ],
            'resource':[
                'all_comp.py',
                'comp_by_id.py',
                'user_controller.py'
            ],
            'service': [
                'comp_service.py',
                'db_connection.py'
            ],
            'tests': ['test_comp.py']
        }

    def util_folder(self):
        return 'util'

    def rename(self, text, table):
        if 'comp_' in text:
            return text.replace('comp_', table+'_')
        if '_comp' in text:
            return text.replace('_comp', '_'+table)
        return text

    def get_field_attrib(self, field_name):
        pk_field = self.source['pk_field']
        if field_name == pk_field:
            return 'primary_key=True, default=PK_DEFAULT_VALUE, required=True'
        return ''

    def extract_table_info(self, obj):
        IMP_DAO = 'import_dao_class'
        DAO_CLS = 'dao_class'
        REQ_TXT = 'requirements'
        result = super().extract_table_info(obj)
        pk_field = obj['pk_field']
        field_list = obj['field_list']
        type_of_pk = field_list[pk_field]
        self.source['default'] = {
            'str': '"000"',
            'int': '0',
            'date': '"2020-05-24"',
            'float': '0.00'
        }[type_of_pk]
        self.source['extra'] = formated_json(self.db_config)
        self.source[IMP_DAO] = self.dao_info[IMP_DAO]
        self.source[DAO_CLS] = self.dao_info[DAO_CLS]
        req = self.dao_info[REQ_TXT]
        self.source[REQ_TXT] = req.replace(' ', '')
        self.source.setdefault('nested', {})
        return result

    def is_bundle(self, path, file_name):
        if path == '' and file_name == 'app.py':
            return True
        return False
