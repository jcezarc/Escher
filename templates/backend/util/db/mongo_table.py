import json
from pymongo import MongoClient
from util.db.db_table import DbTable
from bson.json_util import dumps

CON_STR = '{server}{host_or_user}:{port_or_password}'

class MongoTable(DbTable):
    conn = None

    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        if not self.conn:
            self.conn = MongoClient(
                CON_STR.format(**params)
            )
        db = self.conn[params['database']]
        self.collection = db.get_collection(self.table_name)

    def new_record(self, json_data):
        found = self.find_one(json_data)
        if not found:
            record = {}
            for field, value in json_data.items():
                join = self.joins.get(field)
                if join:
                    value = join.new_record(value)
                record[field] = value
            self.collection.insert(record)
            found = record
        return found

    def insert(self, json_data):
        errors = self.validator.validate(json_data)
        if errors:
            return errors
        self.new_record(json_data)
        return None

    def update(self, json_data):
        self.collection.update_one(
            self.get_conditions(json_data),
            {'$set': json_data}
        )

    def get_node(self, record):
        result = {}
        for field, value in record.items():
            if field not in self.map:
                continue
            result[field] = value
        return result

    def find_all(self, limit=0, filter=None):
        dataset = self.collection.find(limit=limit, filter=filter)
        result = []
        for record in dataset:
            result.append(self.get_node(record))
        return result

    def find_one(self, values):
        found = self.collection.find_one(
            self.get_conditions(values, True)
        )
        if found:
            found = self.get_node(found)
        return found
    
    def delete(self, values):
        return self.collection.delete_one(
            self.get_conditions(values)
        )

    def get_conditions(self, values, only_pk=False):
        super().get_conditions(values, only_pk)
        return dict(self.conditions)

    def add_condition(self, field, value):
        if self.map[field] == "N":
            value = int(value)
        self.conditions.append(
            (field, value)
        )
