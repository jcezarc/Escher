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

    def query_elements(self, operator, filter_expr='', suffix=''):
        expr_join = ''
        main_table = not suffix
        curr_alias = self.alias + suffix
        alias_list = curr_alias
        if operator.upper() == 'RETURN':
            for field in self.joins:
                join = self.joins[field]
                join_params = join.query_elements(
                    operator,
                    '',
                    '_'+self.alias   # '_'+curr_alias
                )
                alias_list += ', '+join_params['alias_list']
                if expr_join:
                    expr_join += ', ({})'.format(curr_alias)
                expr_join += '-->({alias}:{table}){join}'.format(**join_params)
        result = {
            'alias': curr_alias,
            'table': self.table_name,
            'join': expr_join,
            'alias_list': alias_list
        }
        if main_table:
            result['filter'] = filter_expr
            result['operator'] = operator
        return result

    def inflate(self, row, last=None, suffix=''):
        # 
        # [To-Do]  No banco de dados "Sale", a consulta de vários itens aninhados resulta em arrays duplicados...!!
        #
        record={}
        combine = False
        curr_alias = self.alias+suffix
        for field in self.map:
            join = self.joins.get(field)
            if join:
                value = join.inflate(
                    row, 
                    suffix='_'+self.alias
                )[0]
            else:
                value = row[curr_alias].get(field)
            if combine and join:
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
            # record, to_update = self.inflate(row, record)
            record = row
            if to_update:
                result[-1] = record
            else:
                result.append(record)
                if len(result) == limit:
                    break
        # -----------------------------------------
        return result

    def find_one(self, values):
        found = self.find_all(
            1, self.get_conditions(values)
        )
        if found:
            found = found[0]
        return found

    def contained_clause(self, field, value):
        return "CONTAINS '" + value + "'"

    def get_conditions(self, values, only_pk=False):
        if not values:
            return ''
        super().get_conditions(values, only_pk)
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
            #
            # [To-Do]  relation_name = callback(...)
            #          ex.: callback(table1, table2)
            #
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
            'DETACH DELETE', 
            self.get_conditions(values)
        )
        command = CYPHER_QUERY.format(**params)
        session = self.driver.session()
        session.run(command)
