import logging
from model.%table%_model import %table%Model
from util.messages import (
    resp_erro,
    resp_not_found,
    resp_post_ok,
    resp_get_ok,
    resp_ok
)
from db_connection import get_table

class %table%Service:
    def __init__(self, table=None):
        if table:
            self.table = table
        else:
            self.table = get_table(%table%Model)

    def find(self, params, %pk_field%=None):
        if %pk_field%:
            logging.info(f'Finding "{%pk_field%}" in %table% ...')
            found = self.table.find_one([%pk_field%])
        else:
            logging.info('Finding all records of %table%...')
            found = self.table.find_all(20, self.table.get_conditions(params))
        if not found:
            return resp_not_found()
        return resp_get_ok(found)

    def insert(self, json):
        logging.info('New record write in %table%')
        erros = self.table.insert(json)
        if erros:
            return resp_erro(erros)
        return resp_post_ok()

    def update(self, json):
        logging.info('Changing record of %table% ...')
        erros = self.table.update(json)
        if erros:
            return resp_erro(erros)
        return resp_ok("Record changed OK!")
        
    def delete(self, %pk_field%):
        logging.info('Removing record of %table% ...')
        self.table.delete(%pk_field%)
        return resp_ok("Deleted record OK!")
