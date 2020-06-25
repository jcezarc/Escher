import sqlite3
import mysql.connector
from util.db.fmt_table import FormatTable


class LiteTable(FormatTable):
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

    def find_one(self, values):
        found = self.find_all(
            1, self.get_conditions(values)
        )
        if found:
            return found[0]
        return None

    def delete(self, values):
        command = 'DELETE FROM {} WHERE {}'.format(
            self.table_name,
            self.get_conditions(values)
        )
        self.execute(command, True)

    def insert(self, json_data):
        errors = super().insert(json_data)
        if errors:
            return errors
        command = self.get_command(
            json_data,
            is_insert=True,
            use_quotes=False
        )
        self.execute(command, True)
        return None

    def update(self, json_data):
        command = self.get_command(
            json_data,
            is_insert=False,
            use_quotes=False
        )
        self.execute(command, True)
