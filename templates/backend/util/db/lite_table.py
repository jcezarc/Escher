import sqlite3
import mysql.connector
from util.db.db_table import DbTable

class LiteTable(DbTable):
    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        if 'user' in params:
            self.connection = mysql.connector.connect(**params)
        else:
            self.connection = sqlite3.connect(**params)

    def execute(self, command, need_commit):
        cursor = self.connection.cursor()
        cursor.execute(command)
        if need_commit:
            self.connection.commit()
        return cursor

    def find_all(self, limit=0, filter_expr=''):
        field_list = list(self.map)
        command = 'SELECT {} FROM {}{}{}'.format(
            ','.join(field_list),
            self.table_name,
	        f' WHERE {filter_expr}' if filter_expr else '',
	        f' LIMIT {limit}' if limit else ''
        )
        dataset = self.execute(command, False).fetchall()
        result = []
        for values in dataset:
            record = {}
            for field, value in zip(field_list, values):
                if field in self.joins:
                    join = self.joins[field]
                    value = join.find_one(value)
                record[field] = value
            result.append(record)
        return result

    def get_conditions(self, values, only_pk=True):
        if not values:
            return ''
        super().get_conditions(values, only_pk)
        return ' AND '.join(self.conditions)

    def find_one(self, values):
        found = self.find_all(
            1, self.get_conditions(values)
        )
        if found:
            return found[0]
        return None

    def delete(self, values):
        command = 'DELETE FROM "{}" WHERE {}'.format(
            self.table_name,
            self.get_conditions(values)
        )
        self.execute(command, True)

    def insert(self, json_data):
        errors = self.validator.validate(json_data)
        if errors:
            return errors
        insert_values = self.statement_columns(
            json_data,
            True,
            '{value}'
        )
        field_list = [field for field in json_data]
        command = 'INSERT INTO {} ({})VALUES({})'.format(
            self.table_name,
            ','.join(field_list),
            ','.join(insert_values)
        )
        self.execute(command, True)
        return None

    @staticmethod
    def contained_clause(value):
        return "LIKE '%" + value + "%'"

    def update(self, json_data):
        update_fields = self.statement_columns(
            json_data,
            False
        )
        command = 'UPDATE "{}" SET {} WHERE {}'.format(
            self.table_name,
            ','.join(update_fields),
            self.get_conditions(json_data)
        )
        self.execute(command, True)
