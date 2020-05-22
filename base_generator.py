import os
import sys
import json
import shutil

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
        self.summary = {}

    def ignore_list(self):
        return []

    def root_dir(self):
        # FrontendGenerator => '.../frontend'
        # BackendGenerator => '.../backend'
        return os.path.join(
            'templates',
            self.__class__.__name__.lower()
        )
      
    def create_empty_dir(self, target):
        pass

    def render_code(self, file_name, path='', read_only=False):
        params = self.summary
        origin = os.path.join(
            self.root_dir(),
            path,
            file_name[0]
        )
        target = os.path.join(self.api_name, path)
        if not os.path.exists(target):
            os.makedirs(target)
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
        return {}

    def util_folder():
        pass

    def copy_folder(self, folder):
        src = os.path.join(self.root_dir(), folder)
        dst = os.path.join(self.api_name, folder)
        if not os.path.exists(dst):
            os.makedirs(dst)
        ignore_list = self.ignore_list()
        for f in os.listdir(src):
            if f in ignore_list:
                continue
            s = os.path.join(src, f)
            d = os.path.join(dst, f)
            if os.path.isdir(s):
                self.copy_util(
                    os.path.join(folder, f)
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
        pass

    def extract_table_info(self, obj):
        for key in JSON_KEYS:
            self.summary = obj[key]
        self.summary['API_name'] = self.api_name
        return obj['table']

    def exec(self):
        for table in self.tables:
            self.summary = {}
            table_name = self.extract_table_info(table)
            self.build_app(
                self.template_list(), 
                table_name
            )
        self.copy_folder(self.util_folder())
