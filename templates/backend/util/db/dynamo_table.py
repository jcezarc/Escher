import os
import json
import decimal
import boto3
from datetime import datetime
from flask import current_app
from botocore.exceptions import ClientError, ValidationError
from boto3.dynamodb.conditions import Key, Attr
from marshmallow.fields import Integer, Float, Decimal
from util.db.db_table import DbTable

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

class DynamoTable(DbTable):
    def add_join(self, name, schema, params):
        pass

    def config(self, table_name, schema, params):
        super().config(table_name, schema, params)
        self.connection = boto3.resource(**params)
        try:
            self.session = self.create_table()
        except (ClientError, os.error):
            self.session = self.connection.Table(self.table_name)

    def create_table(self):
        kschema = []
        k_type = 'HASH'
        definitions = []
        for key in self.pk_fields:
            kschema.append({'AttributeName': key, 'KeyType': k_type})
            k_type = 'RANGE'
            attr_type = self.map.get(key) or 'S'
            definitions.append({'AttributeName': key, 'AttributeType': attr_type})
        return self.connection.create_table(
            TableName=self.table_name,
            KeySchema=kschema,
            AttributeDefinitions=definitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            })

    def statement_columns(self, dataset, is_insert=False, pattern='{field}={param_name}'):
        result = []
        key_fields = {}
        attributes = {}
        for field in dataset:
            args = {}
            value = dataset[field]
            if field in self.pk_fields:
                key_fields[field] = value
                continue
            param_name = ':p_' + field
            args['field'] = field
            args['param_name'] = param_name
            result.append(
                pattern.format(**args)
            )
            attributes[param_name] = value
        expression = 'SET ' + ','.join(result)
        return key_fields, expression, attributes

    def insert(self, json_data):
        errors = self.validator.validate(json_data)
        if errors:
            return errors
        self.session.put_item(
            Item=json_data
        )
        return None

    def update(self, json_data):
        key_fields, expression, attributes = self.statement_columns(json_data)
        try:
            self.session.update_item(
                Key=key_fields,
                UpdateExpression=expression,
                ExpressionAttributeValues=attributes,
                ReturnValues="UPDATED_NEW"
            )
        except (ClientError, ValidationError) as update_error:
            return str(update_error)
        return None

    def find_all(self, limit=None, filter=None):
        params = {}
        if limit:
            params['Limit'] = limit
        if filter:
            params['FilterExpression'] = filter
        result = self.session.scan(**params)
        result = json.loads(json.dumps(result, cls=DecimalEncoder))
        if result.get('Count'):
            return result.get('Items')
        return None

    def find_one(self, values):
        result = self.session.query(
            KeyConditionExpression=self.get_conditions(values)
        )
        result = json.loads(json.dumps(result, cls=DecimalEncoder))
        if result.get('Count'):
            return result.get('Items')[0]
        return None

    def delete(self, values):
        if isinstance(values, dict):
            key_expr = values
        else:
            key_expr = {}
            if not isinstance(values, list):
                values = [values]
            for field, value in zip(self.pk_fields, values or []):
                key_expr[field] = value
        self.session.delete_item(Key=key_expr)

    def add_condition(self, field, value):
        if self.map[field] == "N":
            value = int(value)
        self.conditions.append(
            Key(field).eq(value)
        )

    def get_conditions(self, values, only_pk=False):
        super().get_conditions(values, only_pk)
        result = None
        for condition in self.conditions:
            if result:
                result = result & condition
            else:
                result = condition
        return result
