import os
import sys
import json
import shutil
from db_defaults import default_params

JSON_KEYS = [
    'table',
    'pk_field',
    'field_list',
    'nested', #--- ???
]
ANGULAR_KEYS = [
    'title',
    'image',
    'detail',
    'label'
]

class BaseGenerator:

    json_info = {}
    api_name = ''

    def __init__(self, file_name):
        file_name = os.path.splitext(file_name)[0]
        if self.api_name != file_name:
            with open(file_name+'.json', 'r') as f:
                text = f.read()
                f.close()
            self.json_info = json.loads(text)
            self.api_name = file_name
        self.tables = self.json_info['tables']
        db_type = self.json_info['db_type']
        db_config, aux = default_params(db_type)
        db_config.update(
            self.json_info.get('db_config',{})
        )
        self.db_config = db_config
        self.dao_info = aux
        self.is_sql = aux['dao_class'] == 'SqlTable'
        self.summary = {}

    def ignore_list(self):
        db_list = ['dynamo_table.py', 'mongo_table.py', 'neo4j_table.py', 'sql_table.py']
        dao = self.dao_info['import_dao_class']+'.py'
        return [i for i in db_list if i != dao]

    def root_dir(self):
        # FrontendGenerator => '.../frontend'
        # BackendGenerator => '.../backend'
        return os.path.join(
            'templates',
            self.__class__.__name__.lower()
        )
      
    def create_empty_dir(self, target):
        os.makedirs(target)
        init_file = os.path.join(
            target,
            '__init__.py'
        )
        with open(init_file, 'w') as f:
            f.write(' ')
            f.close()

    def render_code(self, file_name, path='', read_only=False):
        params = self.summary
        origin = os.path.join(self.root_dir(), path, file_name[0])
        target = os.path.join(params["API_name"], path)
        if not os.path.exists(target):
            self.create_empty_dir(target)
        with open(origin, 'r') as f:
            text = f.read()
            f.close()
        for key in params:
            value = params[key]
            text = text.replace(f'%{key}%', value)
        if not read_only:
            target = os.path.join(target, file_name[-1])
            with open(target, 'w') as f:
                f.write(text)
                f.close()
        return text

    def template_list(self):
        return {
            '':[
                ('app.module.ts',{
                    'importModule_List':'list.import.module.ts'
                    ,
                    'Module_List':'list.module.ts'
                    ,
                    'Service_List':'list.service.ts'
                }),
                ('app.routes.ts',{
                    'Routes_List':'list.routes.ts',
                    'import_List':'list.import.ts'
                })
            ],
            'component': {
                'comp-item': [
                    'comp-item.component.css',
                    'comp-item.component.html',
                    'comp-item.component.ts',
                ],
                'comp-list': [
                    'comp-list.component.html',
                    'comp-list.component.ts',
                ],
                'new-comp': [
                    'new-comp.component.html',
                    'new-comp.component.ts'
                ]
            },
            'header': [
                ('header.component.html',{
                    'Link_List':'list.link.html'
                }),
                'header.component.ts'
            ]
        }

    def copy_util(self, ref, ignore_list, sub='util'):
        src = os.path.join(self.root_dir(), sub)
        dst = os.path.join(ref, sub)
        if not os.path.exists(dst):
            os.makedirs(dst)
        for f in os.listdir(src):
            if f in ignore_list:
                continue
            s = os.path.join(src, f)
            d = os.path.join(dst, f)
            if os.path.isdir(s):
                self.copy_util(
                    ref,
                    ignore_list,
                    os.path.join(sub, f)
                )
                continue
            shutil.copy2(s, d)

    def merge_files(self, root, info):
        params = info[1]
        for key in params:
            self.summary[key] = self.render_code(
                file_name=params[key],
                path=root,
                read_only=True
            )
        return info[0]

    def build_app(self, params, table, root=''):
        is_dict = isinstance(params, dict)
        is_list = isinstance(params, list)
        for key in params:
            if is_dict:
                self.build_app(
                    params[key],
                    table,
                    os.path.join(root, key)
                )
            elif is_list:
                if isinstance(key, tuple):
                    file_name = self.merge_files(
                        root,
                        key
                    )
                else:
                    file_name = [
                        key,
                        self.rename(key, table)
                    ]
                self.render_code(
                    path=root,
                    file_name=file_name
                )

    def rename(self, text, table):
        if 'new-' in text:
            return text.replace('new-', table)
        return text.replace('comp-', table)

    def extract_table_info(self, obj):
        for key in JSON_KEYS:
            self.summary = obj[key]
        angular_data = obj.get('Angular')
        if angular_data:
            for key in ANGULAR_KEYS:
                self.summary = obj[key]
        self.summary['API_name'] = self.api_name
        self.summary['is_SQL'] = str(self.is_sql)
        return obj['table']

    def exec(self):
        for table in self.tables:
            self.summary = {}
            table_name = self.extract_table_info(table)
            self.build_app(
                self.template_list(), 
                table_name
            )
