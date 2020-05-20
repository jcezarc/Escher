import os
import sys
import json
import shutil

CURR_VERSION = '0.29'


def render_code(path, file_name, params, to_write=True):
    if isinstance(file_name, list):
        origin = os.path.join('templates', path, file_name[0])
    else:
        origin = os.path.join('templates', path, file_name)
    with open(origin, 'r') as f:
        text = f.read()
        f.close()
    for key in params:
        value = params[key]
        if not isinstance(value, str):
            continue
        text = text.replace(f'%{key}%', value)
    if to_write:
        if not path:
            target = params["API_name"]
        else:
            target = os.path.join(params["API_name"], path)
        if not os.path.exists(target):
            os.makedirs(target)
            init_file = os.path.join(
                target,
                '__init__.py'
            )
            with open(init_file, 'w') as f:
                f.write(' ')
                f.close()
        if isinstance(file_name, list):
            target = os.path.join(target, file_name[1])
        else:
            target = os.path.join(target, file_name)
        with open(target, 'w') as f:
            f.write(text)
            f.close()
    return text


def copy_util(ref, ignore_list, sub='util'):
    src = os.path.join('templates', sub)
    dst = os.path.join(ref, sub)
    if not os.path.exists(dst):
        os.makedirs(dst)
    for f in os.listdir(src):
        if f in ignore_list:
            continue
        s = os.path.join(src, f)
        d = os.path.join(dst, f)
        if os.path.isdir(s):
            copy_util(ref, ignore_list, os.path.join(sub, f))
            continue
        shutil.copy2(s, d)
        print('/', end='')


def field_type(field):
    types = {
        'nm': ('Str', '"000"'),
        'tx': ('Str', '"000"'),
        'id': ('Integer', '1'),
        'nr': ('Integer', '1'),
        'qt': ('Integer', '1'),
        'in': ('Boolean', 'False'),
        'is': ('Boolean', 'False'),
        'vl': ('Float', '1.00'),
        'dt': ('Date', '"2020-03-19"'),
    }
    result = types.get(
        field[:2], ('Str', '"???"')
    )
    return result


def load_json(file_name):
    with open(file_name, 'r') as f:
        text = f.read()
        f.close()
    content = json.loads(text)
    result = []
    empty_values = {
        'tables': [],
        'db_type': "",
        'db_config': {}
    }
    for item in empty_values:
        result.append(
            content.get(item, empty_values[item])
        )
    return tuple(result)




def exec_cmd():
    if len(sys.argv) < 2:
        print("""
                *** Create-Flask-App {} ***

                How to use:
                > python create_flask_app.py <JSON file>

                Example:
                > python create_flask_app.py Movies
                """.format(
            CURR_VERSION
        )
        )
        return

    def indentation(num_tabs):
        return '\t' * num_tabs

    def formated_json(json_data):
        result = '{'
        for key in json_data:
            value = json_data[key]
            result += '\n{}"{}": "{}",'.format(
                indentation(4),
                key,
                value
            )
        result += '\n{}{}'.format(
            indentation(3),
            '}'
        )
        return result
    is_help = sys.argv[1][0] == '-'
    if is_help:
        db_type = sys.argv[1][1:]
        print('-'*100)
        print(f'Default config for {db_type}:')
        print(
            formated_json(
                default_params(db_type)[0]
            )
        )
        print('-'*100)
        return
    file_name = os.path.splitext(sys.argv[1])[0]
    tables, db_type, config_read = load_json(file_name + '.json')
    db_config, aux = default_params(db_type)
    db_config.update(config_read)

    summary = {}
    is_sql = aux['dao_class'] == 'SqlTable'
    summary['API_name'] = file_name
    summary['is_SQL'] = str(is_sql)
    for info in tables:
        info['API_name'] = file_name
        info['field_type'], info['default'] = field_type(info['pk_field'])
        print('*', end='')
        for template in ['config_routes', 'imports', 'swagger_details']:
            text = summary.get(template, '')
            summary[template] = text + render_code(
                'app',
                f'{template}.py',
                info,
                False
            )
            print('+', end='')
        for template in ['model', 'resource', 'service', 'tests']:
            nested_fields = info.get('nested', [])
            field_list = info.get('field_list', [])
            module = info['table']
            if template == 'resource':
                for sub in ['res_by_id.py', 'all_res.py']:
                    render_code(
                        template,
                        [
                            sub,
                            sub.replace('res', module)
                        ],
                        info
                    )
                continue
            elif template == 'service':
                info.update(aux)
                info['extra'] = formated_json(db_config)
            elif template == 'model':
                imports = ''
                nested_expr = ''
                for nested in nested_fields:
                    imports += f'from model.{nested} import {nested}Model\n'
                    nested_expr += f'    {nested.lower()} = Nested({nested}Model)\n'
                info['imports'] = imports
                info['nested'] = nested_expr
                model_fields = ''
                remaining = len(field_list)-1
                for field in field_list:
                    model_fields += '    {} = {}()'.format(
                        field,
                        field_type(field)[0]
                    )
                    if remaining:
                        model_fields += '\n'
                    remaining -= 1
                info['field_list'] = model_fields
            elif template == 'tests':
                module = 'test_' + module
            render_code(
                template,
                [
                    f'{template}.py',
                    f"{module}.py"
                ],
                info
            )
            print('.', end='')
    render_code('', 'app.py', summary)
    dbs = ['dynamo_table.py', 'mongo_table.py', 'neo4j_table.py', 'sql_table.py']
    dbs.remove(info['import_dao_class']+'.py')
    copy_util(file_name, dbs)
    print('='*50)
    print('\tSuccess!')
    print('-'*100)


exec_cmd()
