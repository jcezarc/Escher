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

    def check_lists(self, key, main_file, text):
        new_text, changed = super().check_lists(
            'nested',
            main_file,
            text
        )
        if not changed:
            return super().check_lists(
                key,
                main_file,
                text
            )
        return text, True

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
            'service': [
                'service.py',
                'db_connection.py'
            ],
            'tests': ['testes.py']
        }

    def util_folder():
        return 'util'

    def rename(self, text, table):
        if 'res_' in text:
            return text.replace('res_', table+'_')
        elif '_res' in text:
            return text.replace('_res', '_'+table)

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
        self.summary['is_SQL'] = str(self.is_sql)
        self.summary['extra'] = self.formated_json_config()
        self.summary[IMP_DAO] = self.dao_info[IMP_DAO]
        self.summary[DAO_CLS] = self.dao_info[DAO_CLS]
        return result
