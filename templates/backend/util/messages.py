import datetime
import logging

def resp_ok(msg="OK", data=None, status_code=200):
    result = {}
    result['timeStamp'] = str(datetime.datetime.now())
    if data:
        result['data'] = data
    result['status'] = msg
    logging.info(msg)
    return result, status_code

def resp_erro(msg, status_code=400):
    result = {}
    result['timeStamp'] = str(datetime.datetime.now())
    result['status'] = msg
    logging.error(f'Error {status_code}: {msg}')
    return result, status_code

def resp_not_found(msg="Not found"):
    return resp_erro(msg, 404)

def resp_get_ok(data=None):
    return resp_ok('GET ok!', data)

def resp_post_ok(data=None):
    return resp_ok('POST ok!', data, 201)
