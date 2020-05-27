import os
import sys
import json
import shutil
from key_names import JSON_KEYS

class BaseGenerator:

    json_info = {}
    api_name = ''

    def __init__(self, linter):
        if self.api_name != linter.file_name:
            self.json_info = linter.data
            self.api_name = linter.file_name
        self.tables = self.json_info['tables']
        self.source = {}
        self.bundle = {}

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

    def on_create_dir(self, target):
        pass

    def field_type(self, value):
        pass

    def get_field_attrib(self, field_name):
        return ''

    def check_fields(self, key, curr_file, text):
        size = len(key)
        has_fields = curr_file[:size] == key
        if has_fields:
            field_list = self.source[key]
            result = ''
            for field in field_list:
                result += text.replace(
                    '%field_name%',
                    field
                ).replace(
                    '%field_type%',
                    self.field_type(field_list[field])
                ).replace(
                    '%attributes%',
                    self.get_field_attrib(field)
                )
            text = result
        return text

    def is_bundle(self, path, file_name):
        pass

    def render_code(self, file_names, paths, read_only=False):
        curr_file = file_names[0]
        origin = os.path.join(
            self.root_dir(),
            paths[0],
            curr_file
        )
        with open(origin, 'r') as f:
            text = f.read()
            f.close()
        for key in self.source:
            value = self.source[key]
            if isinstance(value, dict):
                text = self.check_fields(
                    key,
                    curr_file,
                    text
                )
            else:
                text = text.replace(f'%{key}%', value)
        if not read_only:
            target = os.path.join(
                self.api_name,
                self.root_dir(''),
                paths[-1]
            )
            if not os.path.exists(target):
                os.makedirs(target)
                self.on_create_dir(target)
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
        main_file = info[0]
        is_bundle = self.is_bundle(root, main_file)
        if is_bundle:
            dataset = self.bundle.setdefault(
                main_file, {
                    'path': root
                }
            )
        else:
            dataset = self.source
        for key in params:
            value = self.render_code(
                file_names=[params[key]],
                paths=[root],
                read_only=True
            )
            if is_bundle:
                value = dataset.get(key, '') + value
            dataset[key] = value
        return [
            main_file,
            self.rename(main_file, table)
        ], is_bundle

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
                    file_names, ignore = self.merge_files(
                        root,
                        item,
                        table
                    )
                    if ignore:
                        continue
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

    def init_source(self):
        self.source = {}
        self.source['API_name'] = self.api_name

    def extract_table_info(self, obj):
        self.init_source()
        for key in JSON_KEYS:
            if key in obj:
                self.source[key] = obj[key]
        return obj['table']

    def unpack(self):
        for file_name in self.bundle:
            params = self.bundle[file_name]
            path = params.pop('path')
            self.init_source()
            self.source.update(params)
            self.render_code(
                file_names=[file_name],
                paths=[path]
            )

    def exec(self):
        for table in self.tables:
            self.source = {}
            table_name = self.extract_table_info(table)
            self.build_app(
                self.template_list(), 
                table_name
            )
        self.unpack()
        self.copy_folder(self.util_folder())
