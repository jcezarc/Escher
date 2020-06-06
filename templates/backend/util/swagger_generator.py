import json
from flask import current_app
from marshmallow import Schema
from marshmallow.fields import (
    Str,
    Integer,
    Float,
    Decimal,
    Date,
    DateTime,
    Boolean,
    List,
    Nested,
    Dict,
    Raw
)

class FlaskSwaggerGenerator:
    """    
    ---------- callback sample: -----------------
    def swagger_details(id_route):
        model = ...
        resource = ...
        docstring = ...
        ignore = False
        return model, resource, docstring, ignore

    generator = FlaskSwaggerGenerator(swagger_details)
    """
    def __init__(self, callback_func=None, swagger_info=None):
        self.app = current_app
        self.callback = callback_func
        # Monta o Swagger no self.content ...
        if swagger_info:
            self.content = self.swagger_header(swagger_info)
        else:
            self.content = self.swagger_header({
                "description": "",
                "version": "1.0",
                "title": ""
            })
        self.content['paths'] = self.list_routes()

    @staticmethod
    def swagger_header(info):
        return {
            "swagger": "2.0",
            "info": info
        }

    @staticmethod    
    def route_split(route):
        names = route.split('/')
        params = []
        last_name = None
        for name in names:
            if not name:
                continue
            elif name[0] == '<':
                params.append(name)
            else:
                last_name = name
        return last_name, params

    def list_routes(self):
        result = {}
        def clear_tag(item):
            return item.strip().replace('\n', '')
        for rule in self.app.url_map.iter_rules():
            route_name = rule.rule
            is_static = route_name[0:7].upper() == '/STATIC'
            invalid_route = '<path:' in route_name
            if is_static or invalid_route:
                continue
            schema = None
            resource = None
            description = ""
            if self.callback:
                schema, resource, description, ignore = self.callback(
                    self.route_split(route_name)
                )
                if ignore:
                    continue
            route_name = route_name.replace('<','{').replace('>','}')
            route_obj = result.get(route_name, {})
            for method in rule.methods:
                if not method in ['GET', 'POST', 'PUT', 'DELETE']:
                    continue
                if not description:
                    if resource:
                        if method == 'GET':
                            view_func = resource.get
                        elif method == 'POST':
                            view_func = resource.post
                        elif method == 'PUT':
                            view_func = resource.put
                        elif method == 'DELETE':
                            view_func = resource.delete
                    else:
                        view_func = self.app.view_functions.get(rule.endpoint)
                    if view_func:
                        description = (view_func.__doc__ or "").strip()
                if description:
                    tags = description.split('#')
                    description = tags.pop(0)
                    tags = list(map(clear_tag, tags))
                else:
                    tags = []
                meth_obj = {
                    "description": description,
                    "produces": self.json_statement(),
                    "responses": self.response_for(method)
                }
                params = []
                if method in ['GET', 'DELETE']:
                    for argument in rule.arguments:
                        if argument in route_name:
                            params.append(
                                self.new_parameter(argument)
                            )
                else:
                    if isinstance(schema, Schema):
                        schema = self.schema_to_dict(
                            schema.declared_fields
                        )
                        if schema:
                            params.append(
                                self.new_parameter('request', schema)
                            )
                    meth_obj["consumes"] = self.json_statement()
                if params:
                    meth_obj["parameters"] = params
                if tags:
                    meth_obj["tags"] = tags
                route_obj[method.lower()] = meth_obj
            result[route_name] = route_obj
        return result

    @staticmethod
    def new_parameter(param_name, schema=None):
        if schema:
            result = {
                "in": "body",
                "name": param_name,
                "schema": schema
            }
        else:
            result = {
                "name": param_name,
                "in": "path",
                "description": "",
                "required": True,
                "type": "string"
            }
        return result

    @staticmethod
    def json_statement():
        return ["application/json"]

    @staticmethod
    def response_for(method):
        if method in ['GET', 'DELETE']:
            if method == 'DELETE':
                operacao = 'deletado'
            else:
                operacao = 'recuperado'
            result = {
                "200": {
                    "description": f"objeto {operacao} com sucesso"
                },
                "404":{
                    "description": "O recurso não foi encontrado"
                }
            }
        else:
            result = {
                "201": {
                    "description": "Sucesso"
                },
                "400":{
                    "description": "Erro(s)"
                }
            }
        return result

    def schema_to_dict(self, source):
        result = {}
        for key in source:
            value = {}
            field = source[key]
            is_array = isinstance(field, List)
            if is_array:
                field = field.inner
            is_integer = isinstance(field, Integer)
            is_float = isinstance(field, Float)
            is_decimal = isinstance(field, Decimal)
            if isinstance(field, Date):
                date_format = "date"
            elif isinstance(field, DateTime):
                date_format = "date-time"
            else:
                date_format = None
            if isinstance(field, Nested):
                value = self.schema_to_dict(field.nested._declared_fields)
            elif is_integer or is_float or is_decimal:
                value = self.set_type("number")
            elif isinstance(field, Str) or date_format:
                value = self.set_type("string")
                if date_format:
                    value['format'] = date_format
            elif isinstance(field, Boolean):
                value = self.set_type("boolean")
            elif isinstance(field, Dict) or isinstance(field, Raw):
                value = self.type_object(None)
            else:
                continue
            if field.required:
                value['required'] = True
            if field.default:
                value['default'] = field.default
            if is_array:
                result[key] = self.type_array(value)
            else:
                result[key] = value
        return self.type_object(result)

    @staticmethod
    def type_array(items):
        return {
            "type": "array",
            "items": items
        }

    @staticmethod
    def set_type(data_type):
        return {
            "type": data_type
        }


    @staticmethod
    def type_object(properties):
        result = {}
        result['type'] = "object"
        if properties:
            result["properties"] = properties
        return result
