DB_TYPES = {
        'dynamodb': ({
                "service_name": 'dynamodb',
                "region_name": 'us-west-2',
                "endpoint_url": "http://localhost:8000",
                "aws_access_key_id": "",
                "aws_secret_access_key": "",
            },{
                'import_dao_class': 'dynamo_table',
                'dao_class': 'DynamoTable'
            }),
        'neo4j': ({
                'host': 'localhost',
                'port': 7687,
                'user': '',
                'password': '',
            },{
                'import_dao_class': 'neo4j_table',
                'dao_class': 'Neo4Table'
            }),
        'postgres': ({
                "dialect": "postgresql",
                "driver": "psycopg2",
                "username": "postgres",
                "password": "xxxxx",
                "host": "localhost",
                "port": "5432",
                "database": "pg01",
            },{
                'import_dao_class': 'sql_table',
                'dao_class': 'SqlTable'
            }),
        'mongodb': ({
                'server': 'mongodb+srv',
                'host_or_user': '',
                'port_or_password': '',
                'database': '',
            },{
                'import_dao_class': 'mongo_table',
                'dao_class': 'MongoTable'
            }),
        'sqlserver': ({
                "dialect": "mssql",
                "driver": "pyodbc",
                "username": "",
                "password": "",
                "host": "localhost",
                "port": "1433",
                "database": "",
            },{
                'import_dao_class': 'sql_table',
                'dao_class': 'SqlTable'
            })
    }

def default_params(db_type):
    params = DB_TYPES
    return params.get(db_type.lower(), ({}, {}))

def formated_json(dataset, num_tabs=12, step=4):
    is_list = isinstance(dataset, list)
    if is_list:
        separators = ['[', ']']
    else:
        separators = ['{', '}']
    indentation = ' ' * num_tabs
    result = separators[0]
    num_tabs += step
    has_values = False
    for key in dataset:
        if is_list:
            value = key
        else:
            value = dataset[key]
        if isinstance(value, str):
            value = f'"{value}"'
        elif isinstance(value, dict) or isinstance(value, list):
            value = formated_json(value, num_tabs)
        if has_values:
            result += ','
        if is_list:
            result += '\n{}{}'.format(
                ' ' * num_tabs,
                value
            )
        else:
            result += '\n{}"{}": {}'.format(
                ' ' * num_tabs,
                key,
                value
            )
        has_values = True
    result += '\n{}{}'.format(
        indentation,
        separators[1]
    )
    return result
