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

    def root_dir(self):
        # FrontendGenerator => '.../frontend'
        # BackendGenerator => '.../backend'
        return os.path.join(
            'templates',
            self.__class__.__name__.lower()
        )
      
    def create_empty_dir(self, target):
        pass

    def field_type(self, value):
        pass

    def render_code(self, file_name, path='', read_only=False):
        params = self.summary
        ID_FIELD_LIST = 'field_list'
        main_file = file_name[0]
        origin = os.path.join(
            self.root_dir(),
            path,
            main_file
        )
        target = os.path.join(self.api_name, path)
        if not os.path.exists(target):
            os.makedirs(target)
            self.create_empty_dir(target)
        with open(origin, 'r') as f:
            text = f.read()
            f.close()
        field_list = params.pop(ID_FIELD_LIST, None)
        has_fields = main_file[:10] == ID_FIELD_LIST
        if field_list and has_fields:
            result = ''
            # ----- Transformar em função
            # ----- para usar com NESTED!
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
            # -------------------------------
        for key in params:
            value = params[key]
            text = text.replace(f'%{key}%', value)
        if not read_only:
            target = os.path.join(target, file_name[-1])
            with open(target, 'w') as f:
                f.write(result)
                f.close()
        print('.', end='')
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
                file_name=[params[key]],
                path=root,
                read_only=True
            )
        return [info[0]]

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
                    file_name = self.merge_files(
                        root,
                        item
                    )
                else:
                    file_name = [
                        item,
                        self.rename(item, table)
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