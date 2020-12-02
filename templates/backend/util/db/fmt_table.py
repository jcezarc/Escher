from util.db.db_table import DbTable, SQL_INSERT_MODE


class FormatTable(DbTable):

    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        self.created = False
        self.flat_all = lambda d: {k: self.flatten(k, v) for k,v in d.items()}

    def insert(self, json_data):
        sample = json_data.copy()
        # --- Validation ------------
        for field in self.joins:
            sample[field] = self.joins[field].default_values()
        errors = self.validator.validate(sample)
        # ---------------------------
        return errors

    def get_command(self, json_data, is_insert=True, use_quotes=False):
        table_name = self.table_name
        if use_quotes:
            table_name = f'"{table_name}"'
            mask = '"{}"'
        else:
            mask = '{}'
        d = json_data
        json_data = self.flat_all(json_data)
        if is_insert:
            field_list = [mask.format(k) for k in d]
            insert_values = self.statement_columns(
                json_data,
                SQL_INSERT_MODE,
                pattern='{value}'
            )
            return 'INSERT INTO {}({})VALUES({})'.format(
                table_name,
                ','.join(field_list),
                ','.join(insert_values)
            )
        else:
            pattern = mask.format('{field}') + '={value}'
            field_list = self.statement_columns(
                json_data,
                is_insert=False,
                pattern=pattern
            )
            return 'UPDATE {} SET {} WHERE {}'.format(
                table_name,
                ','.join(field_list),
                self.get_conditions(json_data, True)
            )

    def flatten(self, key, value):
        if isinstance(value, dict) and key in self.joins:
            join = self.joins[key]
            key = join.pk_fields[0]
            return value[key]
        return value

    def inflate(self, value, record, prefix):
        search = prefix.pop(0)
        key = search
        if prefix:
            for field in self.joins:
                join = self.joins[field]
                if join.alias == search:
                    result = record.get(field)
                    if not isinstance(result, dict) :
                        result = {}
                    key, value = join.inflate(
                        value,
                        result,
                        prefix
                    )
                    result[key] = value
                    key = field
                    value = result
                    break
        return key, value

    def contained_clause(self, field, value):
        if field in self.required_fields:
            return super().contained_clause(field, value)
        return "LIKE '%" + value + "%'"

    def get_conditions(self, values, only_pk=True):
        if not values:
            return ''
        if isinstance(values, dict):
            values = self.flat_all(values)
        super().get_conditions(values, only_pk)
        return ' AND '.join(
            self.conditions
        )

    def create_table(self):
        result = ''
        field_list = []
        for field_name, field_type in self.map.items():
            field_list.append('\n\t{} {}'.format(
                field_name, 
                field_type
            ))
        for field, join in self.joins.items():
            if not join.created:
                result += join.create_table()
            field_list.append(
                '\n\tFOREIGN KEY ({}) REFERENCES {}({})'.format(
                    field, join.table_name, join.pk_fields[0]
                )
            )
        field_list.append('\n\tPRIMARY KEY({})'.format(
            ','.join(self.pk_fields)
        ))
        command = 'CREATE TABLE IF NOT EXISTS {} ({}\n);\n'.format(
            self.table_name, 
            ','.join(field_list) 
        )
        self.execute(command, False)
        self.created = True
        result += command
        return result

    def query_elements(self, prefix='', source=''):
        a = self.alias
        if prefix:
            fields = [f'{a}.{f} as {prefix}{f}' for f in self.map]
        else:
            fields = [f'{a}.{f}' for f in self.map]
        curr_table = '{} {}'.format(self.table_name, self.alias)
        expr_join = ''
        for field in self.joins:
            join = self.joins[field]
            join_fields, join_table, join_left = join.query_elements(
                prefix+join.alias+'__', expr_join
            )
            join_primary_key = join.alias + '.' + join.pk_fields[0]
            if join_primary_key in join_fields:
                join_fields.remove(join_primary_key)
            header = 'LEFT JOIN {} '.format(join_table)
            if header in source or header in expr_join:
                continue
            sub_expr = '\n\t{}ON ({}.{} = {}){}'.format(
                header,
                self.alias, field,
                join_primary_key,
                join_left
            )
            fields += join_fields
            expr_join += sub_expr
        return fields, curr_table, expr_join
