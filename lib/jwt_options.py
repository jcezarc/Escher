
def get_jwt_options(empty=False):
    result = {
        'jwt_import_access_token': '''
            import uuid
            from flask_jwt_extended import create_access_token, JWTManager
        ''',
        'jwt_secret_key': '''
            APP.config['JWT_SECRET_KEY'] = str(uuid.uuid4())
            JWT = JWTManager(APP)
        ''',
        'jwt_requirements': '''
            Flask-JWT==0.3.2
            Flask-JWT-Extended==3.24.1
        ''',
        'jwt_decorator': '@jwt_required',
        'import_jwt_required': '''
            from flask_jwt_extended import jwt_required
        ''',
        'jwt_decorators_list': 'decorators=[jwt_required]',
        'jwt_handshake': '''
            @APP.route('/handshake', methods=['POST'])
            def handshake():
                user = request.json.get('user')
                password = request.json.get('password')
                found, user_id = valid_user(user, password)
                if not found:
                    return "Invalid user", 403
                access_token = create_access_token(identity=user_id)
                return jsonify(access_token=access_token), 200
        '''
    }
    if empty:
        for key in result:
            result[key] = ''
    return result