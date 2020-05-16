import json
from flask_restful import Resource
from flask import request, jsonify
from service.%table% import %table%Service

class All%table%(Resource):
    def get(self):
        """
        Returns all records from the table %table%

        #Read
        """
        service = %table%Service()
        return service.find(request.args)
    
    def post(self):
        """
        Write a new record in %table%

        #Write
        """
        req_data = request.get_json()
        service = %table%Service()
        return service.insert(req_data)

    def put(self):
        """
        Updates a record in %table%

        #Write
        """
        req_data = json.loads(request.data.decode("utf8"))
        service = %table%Service()
        return service.update(req_data)
