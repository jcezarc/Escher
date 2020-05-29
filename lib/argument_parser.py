import os
import json
from lib.db_defaults import default_params, DB_TYPES, formated_json
from lib.version import CURR_VERSION
from lib.key_names import JSON_SAMPLE

class ArgumentParser:
    def __init__(self, param_list):
        self.param_list = param_list
        self.frontend = True
        self.backend = True
        self.funcs = []
        self.file_name = ''
        self.db_type = ''
        self.__eval()

    def __eval(self):
        last_arg = ''
        is_first = True
        for param in self.param_list:
            if is_first:
                is_first = False #-- sys.argv[0] == Escher.py
                continue
            text = param.lower()
            if text in ['-h', '--help']:
                self.funcs.append(self.show_help)
                last_arg = 'H'
            elif text in ['-f', '--frontend']:
                self.backend = False
                last_arg = 'F'
            elif text in ['-b', '--backend']:
                self.frontend = False
                last_arg = 'B'
            elif text in ['-n', '--new']:
                self.funcs.append(self.create_empty_json)
                last_arg = 'N'
            elif last_arg == 'H':
                if text == 'db_types':
                    self.funcs.append(self.show_all_types)
                elif text == 'db_config':
                    self.funcs.append(self.show_db_config)
                    last_arg = 'C'
            elif last_arg in ['C', 'J']:
                self.db_type = text
            else:
                self.file_name = os.path.splitext(text)[0]
                if text[0] == '-':
                    self.funcs = [self.show_error_arg]
                    return
                last_arg = 'J'
        if last_arg in ['F', 'B'] and not self.file_name:
            self.funcs = [self.show_error_file]

    def show_help(self):
        print(
            """
            Escher {}
            **** Arguments:***

            --help db_types | db_config <db_type>
                Examples:   --help db_config MongoDB
                            --help db_types
                                Lists all supported db_types
            --frontend <JSON file>
                    Creates only the frontend part.
            --backend <JSON file>
                    Creates only the backend part.
            --new <JSON file> [<db_type>]
                    Produces an empty JSON file for Escher.
            """.format(CURR_VERSION)
        )

    def show_all_types(self):
        print('*** Db Types: ***')
        for dtype in DB_TYPES:
            print('\t', dtype)

    def show_db_config(self):
        if not self.db_type:
            print('ERROR: Missing db_type')
            return
        print(f'*** Default config for "{self.db_type}":')
        print(formated_json(
            default_params(self.db_type)[0],
            num_tabs=2,
            step=4
        ))

    def create_empty_json(self):
        if not self.file_name:
            self.show_error_file()
            return
        result = JSON_SAMPLE
        if self.db_type:
            result['db_type'] = self.db_type
            db_config = default_params(self.db_type)[0]
            result['db_config'] = db_config
        content = formated_json(result, num_tabs=0, step=4)
        target = self.file_name+'.json'
        with open(target, 'w') as f:
            f.write(content)
            f.close()
        print(f'The "{target}" file was created!')

    def exec_funcs(self):
        for func in self.funcs:
            func()

    def show_error_arg(self):
        bad_argument = self.file_name
        print(f'ERROR: Invalid argument {bad_argument}')

    def show_error_file(self):
        print('ERROR: Missing JSON file')
