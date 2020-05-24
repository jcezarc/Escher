import os
import sys
import json
import shutil
from json.decoder import JSONDecodeError

JSON_KEYS = [
    'table',
    'pk_field',
    'field_list',
    'nested',
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
            try:
                self.load_json(file_name)
            except JSONDecodeError:
                self.json_info = None
                print('\n\n*** Invalid JSON file! ***\n')
                return
            self.api_name = file_name
        self.tables = self.json_info['tables']
        self.summary = {}

    def load_json(self, file_name):
        with open(file_name+'.json', 'r') as f:
            text = f.read()
            f.close()
        self.json_info = json.loads(text)

    def ignore_list(self):
        return []

    def root_dir(self, base_path='templates'):
        # FrontendGenerator => '.../frontend'
        # BackendGenerator => '.../backend'
        return os.path.join(
            base_path,
            self.__class__.__name__.replace(
                'Generator', ''
            ).lower()
        )
      
    def create_empty_dir(self, target):
        pass

    def field_type(self, value):
        pass

    def check_lists(self, key, main_file, text):
        params = self.summary
        size = len(key)
        has_fields = main_file[:size] == key
        if has_fields:
            field_list = params.pop(key, None)
            if field_list is None:
                return text, False
            result = ''
            for field in field_list:
                if field == params['pk_field']:
                    attr = 'primary_key=True, default=PK_DEFAULT_VALUE, required=True'
                else:
                    attr = ''
                result += text.replace(
                    '%field_name%',
                    field
                ).replace(
                    '%field_type%',
                    self.field_type(field_list[field])
                ).replace(
                    '%attributes%',
                    attr
                )
            text = result
        return text, has_fields

    def render_code(self, file_names, paths, read_only=False):
        params = self.summary
        main_file = file_names[0]
        origin = os.path.join(
            self.root_dir(),
            paths[0],
            main_file
        )
        target = os.path.join(
            self.api_name,
            self.root_dir(''),
            paths[-1]
        )
        #---
        # [to-DO] Verificar quando paths[0] é VAZIO ("")
        #  (1)= app.py <target> deve ser lida como <origin>
        #  (2)= frontend/component NÃO deve ser criado
        #                           (os.makedirs...)
        #---
        if not os.path.exists(target):
            os.makedirs(target)
            self.create_empty_dir(target)
        with open(origin, 'r') as f:
            text = f.read()
            f.close()
        new_text, changed = self.check_lists(
            'field_list',
            main_file,
            text
        )
        if changed:
            text = new_text
        for key in params:
            value = params[key]
            if isinstance(value, str):
                text = text.replace(f'%{key}%', value)
        if not read_only:
            target = os.path.join(target, file_names[-1])
            with open(target, 'w') as f:
                f.write(text)
                f.close()
        print('.', end='')
        return text

    def template_list(self):
        return {}

    def util_folder(self):
        pass

    def copy_folder(self, folder):
        src = os.path.join(self.root_dir(), folder)
        dst = os.path.join(
            self.api_name,
            self.root_dir(''),
            folder
        )
        if not os.path.exists(dst):
            os.makedirs(dst)
        ignore_list = self.ignore_list()
        for f in os.listdir(src):
            if f in ignore_list:
                continue
            s = os.path.join(src, f)
            d = os.path.join(dst, f)
            if os.path.isdir(s):
                self.copy_folder(
                    os.path.join(folder, f)
                )
                continue
            shutil.copy2(s, d)

    def merge_files(self, root, info, table):
        params = info[1]
        for key in params:
            self.summary[key] = self.render_code(
                file_names=[params[key]],
                paths=[root],
                read_only=True
            )
        return [
            info[0],
            self.rename(info[0], table)
        ]

    def build_app(self, params, table, root=''):
        is_dict = isinstance(params, dict)
        is_list = isinstance(params, list)
        for item in params:
            if is_dict:
                self.build_app(
                    params[item],
                    table,
                    os.path.join(root, item)
                )
            elif is_list:
                if isinstance(item, tuple):
                    file_names = self.merge_files(
                        root,
                        item,
                        table
                    )
                else:
                    file_names = [
                        item,
                        self.rename(item, table)
                    ]
                self.render_code(
                    paths=[
                        root,
                        self.rename(root, table)
                    ],
                    file_names=file_names
                )

    def rename(self, text, table):
        pass

    def extract_table_info(self, obj):
        for key in JSON_KEYS:
            if key in obj:
                self.summary[key] = obj[key]
        self.summary['API_name'] = self.api_name
        return obj['table']

    def exec(self):
        if self.json_info is None:
            return
        for table in self.tables:
            self.summary = {}
            table_name = self.extract_table_info(table)
            self.build_app(
                self.template_list(), 
                table_name
            )
        self.copy_folder(self.util_folder())
