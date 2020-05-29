import os
import re
from lib.base_generator import BaseGenerator
from lib.key_names import ANGULAR_KEYS

class FrontendGenerator(BaseGenerator):

    def field_type(self, value):
        return {
            'str': 'string',
            'int': 'number',
            'date': 'string',
            'float': 'number'
        }.get(value, value)


    def template_list(self):
        return {
            'app':{
                '': [
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
                    }),
                    'app.component.ts',
                    'app.component.html',
                    'app.api.ts'
                ],
                'component': {
                    'comp-item': [
                        'comp-item.component.css',
                        ('comp-item.component.html',{
                            'colors': 'colors-label.html'
                        }),
                        'comp-item.component.ts',
                    ],
                    'comp-list': [
                        'comp-list.component.html',
                        'comp-list.component.ts',
                    ],
                    'new-comp': [
                        ('new-comp.component.html',{
                            'options': 'options-new.html'
                        }),
                        'new-comp.component.ts'
                    ],
                    '': [
                        (
                            'comp-model.ts',
                            {
                                'fieldList': 'field_list.comp.ts'
                            }
                        ),
                        'comp-service.ts',
                        'comp-component.html',
                        'comp-component.ts'
                    ]
                },
                'header': [
                    ('header.component.html',{
                        'Link_List':'list.link.html'
                    }),
                    'header.component.ts'
                ]
            }
        }

    def root_dir(self, base_path='templates'):
        result = super().root_dir(base_path)
        if base_path == '':
            result = os.path.join(
                result,
                'src'
            )
        return result

    def rename(self, text, table):
        root, file_name = os.path.split(text)
        if 'component' in root:
            root = re.sub(r'\bcomponent\b', table, root)
            text = os.path.join(root, file_name)
        if 'new-' in text:
            return text.replace('-comp', '-'+table)
        return text.replace('comp-', table+'-')

    def extract_table_info(self, obj):
        table = super().extract_table_info(obj)
        pk_field = obj['pk_field']
        angular_data = obj.get('Angular', {})
        if 'image' in angular_data:
            self.source['img_tag'] = f"""
            <img [src]="{table}.%image%" 
                class="img-{table}" height="96" 
                onerror="this.onerror=null;this.src='assets/img/{table}/default.png'"
            >
            """
            self.source['saveImage'] = "item.%image% = `assets/img/'"+table+"'/${(<string>item."+pk_field+")}.jpg`"
        else:
            self.source['img_tag'] = ''
            self.source['saveImage'] = ''
        for key in ANGULAR_KEYS:
            self.source[key] = angular_data.get(key, '')
        colors_angular = angular_data.get(
            'label-colors',
            {}
        )
        self.source['colors'] = colors_angular
        self.source['options'] = colors_angular
        return table

    def util_folder(self):
        return os.path.join('app', 'shared')

    def is_bundle(self, path, file_name):
        if file_name in ['app.routes.ts', 'app.module.ts']:
            return True
        path = os.path.split(path)[-1]
        if path == 'header' and file_name == 'header.component.html':
            return True
        return False

    def get_field_attrib(self, field_name):
        return {
            'red': 'danger',
            'yellow': 'warning',
            'green': 'success',
            'blue': 'info',
        }.get(field_name, '')
