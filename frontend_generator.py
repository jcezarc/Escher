from base_generator import BaseGenerator

class FrontendGenerator(BaseGenerator):

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
                ]
            },
            'header': [
                ('header.component.html',{
                    'Link_List':'list.link.html'
                }),
                'header.component.ts'
            ]
        }

    def rename(self, text, table):
        if 'new-' in text:
            return text.replace('new-', table)
        return text.replace('comp-', table)

    def extract_table_info(self, obj):
        result = super().extract_table_info(obj)
        angular_data = obj.get('Angular')
        if angular_data:
            for key in ANGULAR_KEYS:
                self.summary = obj[key]
        return result

    def util_folder():
        return 'shared'
