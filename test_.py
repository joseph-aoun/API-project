import pytest
import service1, service2, service3

service1.create_db_table()
service2.create_db_table()
service3.create_db_table_3()

global user

service1.delete_customer('testuser')
service2.delete_good('testgood')
service3.delete_purchase_history()

user = {'username': 'testuser', 'password': 'testpass', 'full_name': 'testing agent', 'age': 18, 'gender': 'male', 'marital_status': 'married', 'address': 'test address'}
user = service1.insert_customer(user)

def test_amount():
    assert user['wallet_balance'] == 0
    assert user['username'] == 'testuser'
    assert user['password'] == 'testpass'
    assert user['full_name'] == 'testing agent'
    assert user['age'] == 18
    assert user['marital_status'] == 'married'
    
def test_charge():
    user = service1.get_customer_by_username('testuser')
    service1.charge_customer_wallet(user['username'], 100)
    user = service1.get_customer_by_username(user['username'])
    assert user['wallet_balance'] == 100

def test_deduct():
    user = service1.get_customer_by_username('testuser')
    service1.deduct_from_customer_wallet(user['username'], 50)
    user = service1.get_customer_by_username(user['username'])
    assert user['wallet_balance'] == 50

# try service 2

def test_add_good():
    good = {'name': 'testgood', 'category': 'testcategory', 'price': 20, 'quantity': 10, 'description': 'test description'}
    service2.add_good(good)
    good = service2.get_good_by_name('testgood')
    assert good['name'] == 'testgood'

def test_deduct_good():
    good = service2.get_good_by_name('testgood')
    service2.deduct_good(good)
    good = service2.get_good_by_name('testgood')
    assert good['quantity'] == 9

# try service 3

def test_make_purchase():
    service3.make_purshase('testgood', 'testuser', 1)
    good = service2.get_good_by_name('testgood')
    assert good['quantity'] == 8
    user = service1.get_customer_by_username('testuser')
    assert user['wallet_balance'] == 30

def test_purchase_history():
    history = service3.get_purshase_history('testuser')
    assert history[0]['name'] == 'testgood'
    assert history[0]['quantity'] == 1
    assert history[0]['price'] == 20
    assert len(history) == 1
    
def test_deduct_good_2():
    good = service2.get_good_by_name('testgood')
    service2.deduct_good(good)
    good = service2.get_good_by_name('testgood')
    assert good['quantity'] == 7

def test_deduct_good_amount():
    good = service2.get_good_by_name('testgood')
    service3.deduct_good_amount(good, 2)
    good = service2.get_good_by_name('testgood')
    assert good['quantity'] == 5