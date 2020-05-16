import json
from pymongo import MongoClient
from util.db.db_table import DbTable
from bson.json_util import dumps

CON_STR = '{server}://{host_or_user}:{port_or_password}'

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

    def add_join(self, name, schema, params):
        pass

    def insert(self, json_data):
        self.collection.insert(json_data)

    def update(self, json_data):
        self.collection.update_one(
            self.get_conditions(json_data),
            {'$set': json_data}
        )

    def find_all(self, limit=0, filter=None):
        result =  self.collection.find(limit=limit, filter=filter)
        return json.loads(dumps(result))

    def find_one(self, values):
        result = self.collection.find_one(
            self.get_conditions(values)
        )
        return json.loads(dumps(result))
    
    def delete(self, values):
        return self.collection.delete_one(
            self.get_conditions(values)
        )

    def get_conditions(self, values):
        super().get_conditions(values)
        return dict(self.conditions)

    def add_condition(self, field, value):
        if self.map[field] == "N":
            value = int(value)
        self.conditions.append(
            (field, value)
        )
