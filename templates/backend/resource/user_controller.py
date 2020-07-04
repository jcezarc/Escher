import hashlib

def users():
    return [
        '424a915b720e1e282004d4a3db7af3bb',
        'd374bafcbb8b166013ef8cc81d74f67b',
        '99e25fc40d47d8490bf5c7c2e6980d3d',
        'acb9135314ca86d4ce0518c33e08132b'
    ]

def encode_user(user, password):
    hash_object = hashlib.md5(
        f'{user}:{password}'.encode()
    )
    return hash_object.hexdigest()

def valid_user(user, password):
    #------- initial examples --------
    #       valid_user('development', '123')
    #       valid_user('testing', '456')
    #       valid_user('approval', '789')
    #       valid_user('production', 'ABC')
    #---------------------------------
    user_id = encode_user(user, password)
    found = user_id in users()
    return found, user_id
