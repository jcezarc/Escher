import os
from base_generator import BaseGenerator, ANGULAR_KEYS

class FrontendGenerator(BaseGenerator):

    def field_type(self, value):
        return {
            'str': 'string',
            'int': 'int',
            'date': 'string', #-- new Date() ??
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
                    ],
                    '': [
                        (
                            'comp.model.ts',
                            {
                                'fieldList': 'field_list.comp.ts'
                            }
                        ),
                        'comp.service.ts',
                        'comp.component.html',
                        'comp.component.ts'
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

    def rename(self, text, table):
        if 'new-' in text:
            return text.replace('-comp', table)
        return text.replace('comp-', table)

    def extract_table_info(self, obj):
        result = super().extract_table_info(obj)
        angular_data = obj.get('Angular')
        if angular_data:
            for key in ANGULAR_KEYS:
                self.summary[key] = obj.get(key, '')
            label_colors = angular_data.get('label-colors',{})
            for color in label_colors:
                self.summary[color] = label_colors[color]
        return result

    def util_folder(self):
        return os.path.join('app', 'shared')
