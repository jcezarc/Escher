import sys
sys.path.append('..')
from service.%table% import %table%Service
from model.%table% import %table%Model, PK_DEFAULT_VALUE
from util.db.fake_table import FakeTable
from util.messages import resp_ok, resp_not_found

def test_find_success():
    table = FakeTable(%table%Model)
    record = table.default_values()
    table.insert(record)
    service = %table%Service(table)
    status_code = service.find(None, PK_DEFAULT_VALUE)[1]
    assert status_code == 200

def test_find_failure():
    service = %table%Service(FakeTable(%table%Model))
    status_code = service.find(None, PK_DEFAULT_VALUE)[1]
    assert status_code == 404

def test_insert_success():
    table = FakeTable(%table%Model)
    service = %table%Service(table)
    record = table.default_values()
    status_code = service.insert(record)[1]
    assert status_code == 201

def test_insert_failure():
    service = %table%Service(FakeTable(%table%Model))
    status_code = service.insert({})[1]
    assert status_code == 400
