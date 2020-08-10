import json
from util.db.db_table import DbTable

class FakeTable(DbTable):
    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        self.internal_data = []

    def insert(self, json):
        errors = self.validator.validate(json)
        if errors:
            return errors
        self.internal_data.append(json)
        return None

    def find_one(self, values):
        for record in self.internal_data:
            match = True
            for field, value in zip(self.pk_fields, values):
                if record[field] != value:
                    match = False
                    break
            if match:
                return record
        return None
