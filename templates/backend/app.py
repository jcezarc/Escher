# -*- coding: utf-8 -*-
import logging
import uuid
from flask import Flask, Blueprint, request, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import create_access_token, JWTManager
from resource.user_controller import valid_user
from util.swagger_generator import FlaskSwaggerGenerator
%imports%

BASE_PATH = '/%API_name%'

def config_routes(app):
    api = Api(app)
    #--- Resources: ----
%config_routes%    
    #-------------------

def set_swagger(app):
    swagger_url = '/docs'
    swaggerui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        '/api',
        config={
            'app_name': "*- %API_name% -*"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)


def swagger_details(args):
    id_route = args[0]
    params = args[1]
    model = None
    resource = None
    docstring = ""
    if id_route == 'docs':
        docstring = """Swagger documentation
        #Doc
        """
%swagger_details%    
    ignore = False
    return model, resource, docstring, ignore

logging.basicConfig(
    filename='%API_name%.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

APP = Flask(__name__)
CORS(APP)
APP.config['JWT_SECRET_KEY'] = str(uuid.uuid4())
JWT = JWTManager(APP)
config_routes(APP)
set_swagger(APP)

@APP.route('/api')
def get_api():
    """
    API json data

    #Doc
    """
    generator = FlaskSwaggerGenerator(
        swagger_details,
        None
    )
    return jsonify(generator.content)

@APP.route('/health')
def health():
    return 'OK', 200

@APP.route('/handshake', methods=['POST'])
def handshake():
    user = request.json.get('user')
    password = request.json.get('password')
    found, user_id = valid_user(user, password)
    if not found:
        return "Invalid user", 403
    access_token = create_access_token(identity=user_id)
    return jsonify(access_token=access_token), 200

if __name__ == '__main__':
    APP.run(debug=True)
