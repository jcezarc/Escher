import os
import re
from lib.base_generator import BaseGenerator
from lib.key_names import ANGULAR_KEYS

class FrontendGenerator(BaseGenerator):

    def __init__(self, linter):
        super().__init__(linter)
        self.summary = linter.summary

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
                            'colors': 'colors-label.html',
                            'other': 'other-labels.html'
                        }),
                        'comp-item.component.ts',
                    ],
                    'comp-list': [
                        'comp-list.component.html',
                        ('comp-list.component.ts',{
                            'save_nesteds': 'nested-save.ts',
                            'nested_import-list': 'nested-list.import.ts'
                        }),
                    ],
                    'new-comp': [
                        ('new-comp.component.html',{
                            'options': 'options-new.html',
                            'form_fields': 'input_fields-form.html',
                            'form_nested': 'nested-form.html'
                        }),
                        ('new-comp.component.ts',{
                            'new-field_list': 'field_list-new.ts',
                            'new-nested': 'nested-new.ts',
                            'new-nested_import': 'nested-new.import.ts'
                        })
                    ],
                    '': [
                        (
                            'comp-model.ts',
                            {
                                'fieldList': 'field_list.comp.ts',
                                'nested_fields': 'nested-model.ts'
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
        self.source['saveImage'] = ''
        image_field = angular_data['image']
        if 'image' in angular_data:
            self.source['img_tag'] = """
            <img [src]="{}.{}" 
                class="img-{}" height="96" 
            >
            """.format(
                table, image_field,
                table
            )
            if '.' not in image_field:
                self.source['saveImage'] = "item."+image_field+" = `assets/img/"\
                    + table + "/${(<string>item." + pk_field + ")}.jpg`"
        else:
            self.source['img_tag'] = ''
        for key in ANGULAR_KEYS:
            self.source[key] = angular_data.get(key, '')
        label_field = angular_data.get('label')
        if label_field is None:
            colors_angular = {}
        else:
            colors_angular = angular_data.get(
                'label-colors',
                {}
            )
        nested = obj.get('nested', {})
        input_fields = self.source['field_list'].copy()
        other_labels = {}
        if colors_angular:            
            input_fields.pop(label_field)
            self.source['pre-option'] = f'''
                <div class="col">
                    <label>{label_field}:</label>
                    <select formControlName="{label_field}">
            '''
            self.source['pos-option'] = '''
                    </select>
                </div>
            '''
        else:
            if nested:
                detail = list(nested.keys())[-1]
                self.source['detail'] = '{}.{}'.format(
                    detail,
                    self.get_field_attrib(detail)
                )
                d = nested
                other_labels = {i:d[i] for i in d if i != detail}
            elif label_field:
                other_labels = {label_field: ''}
            self.source['pre-option'] = ''
            self.source['pos-option'] = ''
        self.source['input_fields'] = input_fields
        self.source['colors'] = colors_angular
        self.source['options'] = colors_angular
        self.source['other'] = other_labels
        ref = self.nesting_reference(table)
        if ref:
            self.source['export_button'] = """
                        <button 
                        style="border: none;background-color: transparent;margin-left: 10%;"
                        (click)="select({})">
                            <i class="fa fa-check-circle-o"
                            data-toggle="tooltip" title="Select {} for {}"></i>
                        </button>
            """.format(
                table,
                table, ref['table']
            )
            self.source['nesting_ref'] = ref['table']
        else:
            self.source['export_button'] = ''
            self.source['nesting_ref'] = ''
        self.source['nested'] = nested
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
        colors = {
            'red': 'danger',
            'yellow': 'warning',
            'green': 'success',
            'blue': 'info',
        }
        if field_name in  colors:
            return colors[field_name]
        try:
            nested = self.source['nested']
            ref = nested[field_name]
            result = '.'+self.summary[ref]['Angular']['title']
        except KeyError:
            result = ''
        return result

    def nesting_reference(self, subject):
        for table in self.tables:
            nested = table.get('nested')
            if nested is None:
                continue
            for key in nested:
                value = nested[key]
                if value == subject:
                    return table
        return None
