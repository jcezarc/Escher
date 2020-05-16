import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from marshmallow.fields import Str, Nested
from util.db.db_table import DbTable, SQL_INSERT_MODE

CON_STR = '{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}'

class SqlTable(DbTable):
    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        engine = create_engine(
            CON_STR.format(**params)
        )
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def insert(self, json_data):
        sample = json_data.copy()
        # --- Validation ------------
        for field in self.joins:
            sample[field] = self.joins[field].default_values()
        errors = self.validator.validate(sample)
        if errors:
            return errors
        # ---------------------------
        insert_values = self.statement_columns(json_data, SQL_INSERT_MODE, '{value}')
        field_list = [f'"{field}"' for field in json_data]
        command = 'INSERT INTO "{}"({})VALUES({})'.format(
            self.table_name,
            ','.join(field_list),
            ','.join(insert_values)
        )
        self.session.execute(command)
        self.session.commit()
        return None

    def update(self, json_data):
        update_fields = self.statement_columns(json_data,pattern='"{field}"={value}')
        command = 'UPDATE "{}" SET {} WHERE {}'.format(
            self.table_name,
            ','.join(update_fields),
            self.get_conditions(json_data)
        )
        self.session.execute(command)
        self.session.commit()

    def query_elements(self):
        fields = [f'{self.alias}."{field}"' for field in self.map]
        curr_table = '"{}" {}'.format(self.table_name, self.alias)
        expr_join = ''
        for field in self.joins:
            join = self.joins[field]
            join_fields, join_table, sub_expr = join.query_elements()
            join_primary_key = join.alias + '.' + join.pk_fields[0]
            if join_primary_key in join_fields:
                join_fields.remove(join_primary_key)
            fields += join_fields
            expr_join += '\n\tLEFT JOIN {} ON ({}.{} = {}){}'.format(
                join_table,
                self.alias, field,
                join_primary_key,
                sub_expr
            )
        return fields, curr_table, expr_join

    def find_all(self, limit=0, filter_expr=''):
        fields, curr_table, expr_join = self.query_elements()
        command = 'SELECT {} \nFROM {} {}'.format(
            ',\n\t'.join(fields),
            curr_table,
            expr_join
        )
        if filter_expr:
            has_where = 'WHERE' in filter_expr.upper()
            if not has_where:
                filter_expr = 'WHERE {}.{}'.format(
                    self.alias,
                    filter_expr
                )
            command += '\n' + filter_expr
        dataset = self.session.execute(command)
        result = []
        for row in dataset.fetchall():
            record = {}
            for item in row.items():
                key = item[0]
                value = item[1]
                record[key] = str(value)
            result.append(record)
            if len(result) == limit:
                break
        return result

    @staticmethod
    def contained_clause(value):
        return "LIKE '%" + value + "%'"

    def get_conditions(self, values):
        if not values:
            return ''
        super().get_conditions(values)
        return ' AND '.join(self.conditions)

    def find_one(self, values):
        found = self.find_all(
            1, self.get_conditions(values)
        )
        if found:
            found = found[0]
        return found

    def delete(self, values):
        command = 'DELETE FROM "{}" WHERE {}'.format(
            self.table_name,
            self.get_conditions(values)
        )
        self.session.execute(command)
        self.session.commit()
