def default_params(db_type):
    params = {
        'dynamodb': {
            "service_name": 'dynamodb',
            "region_name": 'us-west-2',
            "endpoint_url": "http://localhost:8000",
            "aws_access_key_id": "",
            "aws_secret_access_key": "",
            'import_dao_class': 'dynamo_table',
            'dao_class': 'DynamoTable'
        },
        'neo4j': {
            'host': 'localhost',
            'port': 7687,
            'user': '',
            'password': '',
            'import_dao_class': 'neo4j_table',
            'dao_class': 'Neo4Table'
        },
        'postgres': {
            "dialect": "postgresql",
            "driver": "psycopg2",
            "username": "postgres",
            "password": "xxxxx",
            "host": "localhost",
            "port": "5432",
            "database": "pg01",
            'import_dao_class': 'sql_table',
            'dao_class': 'SqlTable'
        },
        'mongodb': {
            'server': 'mongodb+srv',
            'host_or_user': '',
            'port_or_password': '',
            'database': '',
            'import_dao_class': 'mongo_table',
            'dao_class': 'MongoTable'
        },
        'sqlserver': {
            "dialect": "mssql",
            "driver": "pyodbc",
            "username": "",
            "password": "",
            "host": "localhost",
            "port": "1433",
            "database": "",
            'import_dao_class': 'sql_table',
            'dao_class': 'SqlTable'
        }
    }
    result = params.get(db_type.lower(), {})
    aux = {}
    if result:
        for key in ['import_dao_class', 'dao_class']:
            aux[key] = result.pop(key)
    return result, aux
