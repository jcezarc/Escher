import datetime
import logging

GET_NOT_FOUND_MSG = "Not found"

def resp_ok(msg="OK", data=None, status_code=200):
    result = {}
    result['timeStamp'] = str(datetime.datetime.now())
    if data:
        result['data'] = data
    result['status'] = msg
    logging.info(msg)
    return result, status_code

def resp_error(msg, status_code=400):
    result = {}
    result['timeStamp'] = str(datetime.datetime.now())
    result['status'] = msg
    logging.error(f'Error {status_code}: {msg}')
    return result, status_code

def resp_not_found():
    # return resp_error(msg, 404)
    return resp_ok(GET_NOT_FOUND_MSG)

def resp_get_ok(data=None):
    return resp_ok('GET ok!', data)

def resp_post_ok(data=None):
    return resp_ok('POST ok!', data, 201)
