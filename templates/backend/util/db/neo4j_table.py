from neo4j import GraphDatabase
from marshmallow.fields import Str, Nested
from util.db.db_table import DbTable

CYPHER_QUERY = 'MATCH({alias}:{table}){join} {filter} {operator} {alias_list}'

class Neo4Table(DbTable):
    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        uri = "bolt://{host}:{port}/neo4j"
        self.driver = GraphDatabase.driver(
            uri.format(**params),
            auth=(params['user'], params['password']),
            encrypted=False
        )

    def query_elements(self, operator, filter_expr='', alias_list=None):
        curr_table = self.table_name
        expr_join = ''
        if alias_list is None:
            alias_list = []
        if operator.upper() == 'RETURN':
            alias_list.append(self.alias)
            for field in self.joins:
                join = self.joins[field]
                if join.alias in alias_list:
                    continue
                join_params = join.query_elements(operator, '', alias_list)
                if expr_join:
                    expr_join += ', ({})'.format(self.alias)
                expr_join += '-->({alias}:{table}){join}'.format(**join_params)
        return {
            'alias': self.alias,
            'table': curr_table,
            'join': expr_join,
            'filter': filter_expr,
            'operator': operator,
            'alias_list': ','.join(alias_list)
        }

    def json_record(self, row, last=None):
        record={}
        combine = False
        for field in self.map:
            join = self.joins.get(field)
            if join:
                value = join.json_record(row)[0]
            else:
                value = row[self.alias].get(field)
            if combine:
                result = last[field]
                if not isinstance(result, list):
                    result = [result]
                if value not in result:
                    result.append(value)
                    value = result
            elif last and field in self.pk_fields:
                combine = last[field] == value
            record[field] = value
        return record, combine

    def find_all(self, limit=0, filter_expr=''):
        params = self.query_elements('RETURN', filter_expr)
        command = CYPHER_QUERY.format(**params)
        order_fields = [self.alias+'.'+f for f in self.pk_fields]
        command += ' ORDER BY ' + ','.join(order_fields)
        session = self.driver.session()
        dataset = session.run(command)
        # -----------------------------------------
        result = []
        record = None
        for row in dataset:
            record, to_update = self.json_record(row, record)
            if to_update:
                result[-1] = record
            elif len(result) == limit:
                break
            else:
                result.append(record)
        # -----------------------------------------
        return result

    def find_one(self, values):
        found = self.find_all(
            1, self.get_conditions(values)
        )
        if found:
            found = found[0]
        return found

    @staticmethod
    def contained_clause(value):
        return "CONTAINS '" + value + "'"

    def get_conditions(self, values):
        if not values:
            return ''
        super().get_conditions(values)
        cond_list = [self.alias+'.'+cond for cond in self.conditions]
        return 'WHERE ' + ' AND '.join(cond_list)

    def get_node(self, json_data):
        insert_values = ','.join(
            self.statement_columns(json_data, True, '{field}:{value}')
        )
        nodes = 'MERGE ({}:{} {})\n'.format(
            self.alias,
            self.table_name,
            '{' + insert_values + '}'
        )
        expr_join = ''
        for field in self.joins:
            if field not in json_data:
                continue
            join = self.joins[field]
            nodes += join.get_node(json_data[field])
            expr_join += 'MERGE ({})-[: {}_{}]->({})\n'.format(
                self.alias,
                self.alias, join.alias,
                join.alias
            )
        return nodes + expr_join

    def insert(self, json_data):
        errors = self.validator.validate(json_data)
        if errors:
            return errors
        command = self.get_node(json_data)
        session = self.driver.session()
        session.run(command)
        return None

    def update(self, json_data):
        update_fields = self.statement_columns(json_data, False, '{prefix}{field}={value}')
        fields_set = 'SET '+ ','.join(update_fields)
        params = self.query_elements(
            fields_set,
            self.get_conditions(json_data)
        )
        command = CYPHER_QUERY.format(**params)
        session = self.driver.session()
        session.run(command)

    def delete(self, values):
        params = self.query_elements(
            'DETACH DELETE '+self.alias, 
            self.get_conditions(values)
        )
        command = CYPHER_QUERY.format(**params)
        session = self.driver.session()
        session.run(command)
