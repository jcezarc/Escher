import os
import sys
import json
import shutil
from db_defaults import default_params

class BaseGenerator:
    """    
        1 - Ler JSON
        2 - Armazenar configurações
            2.1 - Completar valores ausentes com default.
        3 - Ler templates e substituir marcas pelas configurações
            >> 3.1 - Identificar quais arquivos temporários usar em cada pasta;
            3.2 - Completar nomes de arquivos com nomes de tabelas
            3.3 - Relacionar tabelas NESTED
        4 - Salvar os arquivos nas pastas corretas
            4.1 - Se a pasta não existir, criar
                4.1.1 - Em pastas vazias existem arquivos obrigatórios?
                        (__init__.py)
            4.2 - Remover arquivos desnecessários.
        5 - Ligar todos os arquivos através de IMPORT
    """

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

    def __init__(self, json_info):
        self.tables = json_info['tables']
        db_type = json_info['db_type']
        db_config, aux = default_params(db_type)
        db_config.update(
            json_info.get('db_config',{})
        )
        self.db_config = db_config
        self.dao_info = aux
        self.summary = {}
        
    def create_init_file(self, target):
        init_file = os.path.join(
            target,
            '__init__.py'
        )
        with open(init_file, 'w') as f:
            f.write(' ')
            f.close()

    def render_code(self, path, file_name, read_only=False):
        origin = os.path.join(self.root_dir(), path, file_name[0])
        target = os.path.join(params["API_name"], path)
        if not os.path.exists(target):
            os.makedirs(target)
            self.create_init_file(target)
        with open(origin, 'r') as f:
            text = f.read()
            f.close()
        for key in params:
            value = params[key]
            ## ??????????????
            if not isinstance(value, str):
                continue 
            ## ??????????????
            text = text.replace(f'%{key}%', value)
        if not read_only:
            target = os.path.join(target, file_name[-1])
            with open(target, 'w') as f:
                f.write(text)
                f.close()
        return text

    def template_list(self):
        return {
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
            }
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

    def merge_info(self, file_name, table, symbol):
        params = {
            'file_name': [file_name],
            'table': table
        }
        self.summary[symbol] = self.render_code(
            params,
            True
        )

    def build_app(self, params, root=''):
        # self.summary = {}
        is_dict = isinstance(params, dict)
        is_list = isinstance(params, list)
        for key in params:
            if is_dict:
                self.build_app(
                    params[key],
                    os.path.join(root, key)
                )
            elif is_list:
                self.render_code(
                    path=root,
                    file_name=key
                )
    def exec(self):
        self.build_app(self.template_list())
