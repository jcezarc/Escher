from util.db.db_table import DbTable, SQL_INSERT_MODE

class FormatTable(DbTable):
    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        self.last_condition = ''

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
        json_data = {k: self.flatten(k, d[k]) for k in d}
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
                self.get_conditions(json_data, False)
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
        super().get_conditions(values, only_pk)
        self.last_condition = ' AND '.join(self.conditions)
        return self.last_condition
