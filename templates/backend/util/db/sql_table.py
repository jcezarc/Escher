import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from marshmallow.fields import Str, Nested
from util.db.fmt_table import FormatTable

CON_STR = '{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}'

class SqlTable(FormatTable):
    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        engine = create_engine(
            CON_STR.format(**params)
        )
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def insert(self, json_data):
        errors = super().insert(json_data)
        if errors:
            return errors
        command = self.get_command(
            json_data,
            is_insert=True,
            use_quotes=True
        )
        self.session.execute(command)
        self.session.commit()
        return None

    def update(self, json_data):
        command = self.get_command(
            json_data,
            is_insert=False,
            use_quotes=True
        )
        self.session.execute(command)
        self.session.commit()

    def query_elements(self, prefix=''):
        a = self.alias
        fields = [f'{a}."{f}" as "{prefix}{f}"' for f in self.map]
        curr_table = '"{}" {}'.format(self.table_name, self.alias)
        expr_join = ''
        for field in self.joins:
            join = self.joins[field]
            join_fields, join_table, sub_expr = join.query_elements(
                prefix+join.alias+'__'
            )
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
                key, value = self.inflate(
                    item[1],
                    record,
                    item[0].split('__')
                )
                record[key] = value
            result.append(record)
            if len(result) == limit:
                break
        return result

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
