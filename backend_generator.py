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

    def create_empty_dir(self, target):
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
        }[value]

    def template_list(self):
        return {
            '':[
                ('app.py',{
                    'config_route': 'config_route.py',
                    'imports': 'imports.py',
                    'swagger_details': 'swagger_details.py',
                }),
            ],
            'model': (
                'model.py',
                {
                    'fieldList': 'field_list.py'
                }
            ),
            'resource':[
                'all_res.py',
                'res_by_id.py'
            ],
            'service': ['service.py'],
            'tests': ['testes.py']
        }

    def util_folder():
        return 'util'

    def rename(self, text, table):
        if 'res_' in text:
            return text.replace('res_', table+'_')
        elif '_res' in text:
            return text.replace('_res', '_'+table)

    def extract_table_info(self, obj):
        result = super().extract_table_info(obj)
        self.summary['is_SQL'] = str(self.is_sql)
        self.summary['extra'] = str(self.db_config)
        return result
