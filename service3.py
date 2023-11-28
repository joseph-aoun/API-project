import sqlite3
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import service2, service1
serv3 = Blueprint('service3', __name__)

def connect_to_db_3():
    conn = sqlite3.connect('purshase_history.db')
    return conn

def create_db_table_3():
        
        """ 
            this function creates the inventory table in the database
    
            returns:
                conn: connection to the database
        """
        
        try:
            with connect_to_db_3() as conn:
                conn.execute('''
                    CREATE TABLE purchase_history (
                        purchase_id INTEGER PRIMARY KEY NOT NULL,
                        username TEXT NOT NULL,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL
                    );
                ''')
                conn.commit()
                print("purchase_history table created successfully")
        except:
            print("purchase_history table creation failed - Maybe table already exists")
        finally:
            conn.close()

def get_good_by_name(name):
    
    """ this function retrieves a good from the inventory table in the database

        Args:
            name (str): the name of the good to be retrieved
        
        Returns:
            good: the good retrieved from the inventory table
    """
    
    item = {}
    
    try:
        with service2.connect_to_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM inventory WHERE name = ?;
            ''', (name,))
            good = cursor.fetchone()
            item['name'] = good[1]
            item['price'] = good[3]
            item['quantity'] = good[4]
            item['category'] = good[2]
            item['description'] = good[5]
            return item
    except:
        print("Good retrieval failed")
    finally:
        conn.close()

def get_goods():
    
    """ this function retrieves all goods from the inventory table in the database

        Returns:
            goods: the goods retrieved from the inventory table
    """
    
    goods = []
    try:
        conn = service2.connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM inventory")
        rows = cur.fetchall()
        for row in rows:
            item = {}
            item['name'] = row['name']
            item['price'] = row['price']
            goods.append(item)
    except:
        goods = []
    finally:
        conn.close()
    return goods

def deduct_good_amount(good, quantity=1):
    """ this function deducts a good from the inventory table in the database

        Args:
            good (dict): the good to be deducted
            quantity (int): the quantity of the good to be deducted
            
        Returns:
            message: a message indicating the status of the deduction
    """
    
    message = {}
    try:
        with service2.connect_to_db() as conn:
            conn.execute('''
                UPDATE inventory SET quantity = quantity - ? WHERE name = ?;
            ''', (quantity, good['name']))
            conn.commit()
            print("Good deducted successfully")
            message['status'] = "Good deducted successfully"
    except:
        print("Good deduction failed")
        message['status'] = "Good deduction failed"
    finally:
        conn.close()
    return message

def make_purshase(good_name, username, quantity):
    good = get_good_by_name(good_name)
    message = {}
    quantity = int(quantity)
    if good['quantity'] < quantity:
        message['status'] = "Purchase failed - Not enough goods in stock"
        return message
    else:
        user = service1.get_customer_by_username(username)
        money = user['wallet_balance']
        price = good['price']
        if money < price*quantity:
            message['status'] = "Purchase failed - Not enough money in wallet"
            return message
        else:
            try:
                service1.deduct_from_customer_wallet(username, price*quantity)
                deduct_good_amount({'name': good_name}, quantity)
                with connect_to_db_3() as conn:
                    conn.execute('''
                        INSERT INTO purchase_history (username, name, quantity, price)
                        VALUES (?, ?, ?, ?);
                    ''', (username, good_name, quantity, price))
                    conn.commit()
                    print("Purchase successful")
                    message['status'] = "Purchase successful"
            except:
                print("Purchase failed")
                message['status'] = "Purchase failed"
            finally:
                conn.close()
            return message

def get_purshase_history(username):
    history = []
    try:
        conn = connect_to_db_3()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM purchase_history WHERE username = ?", (username,))
        rows = cur.fetchall()
        for row in rows:
            item = {}
            item['name'] = row['name']
            item['quantity'] = row['quantity']
            item['price'] = row['price']
            history.append(item)
    except:
        history = []
    finally:
        conn.close()
    return history

def delete_purchase_history():
    try:
        with connect_to_db_3() as conn:
            conn.execute('''
                DELETE FROM purchase_history;
            ''')
            conn.commit()
            print("purchase_history table deleted successfully")
    except:
        print("purchase_history table deletion failed")
    finally:
        conn.close()

@serv3.route('/api/get_goods', methods=['GET'])
def api_get_goods():
    return jsonify(get_goods())

@serv3.route('/api/get_good_by_name/<name>', methods=['GET'])
def api_get_good_by_name(name):
    return jsonify(get_good_by_name(name))

@serv3.route('/api/make_purshase', methods=['POST'])
def api_make_purshase():
    purshase = request.get_json()
    print(purshase)
    return jsonify(make_purshase(purshase['good_name'], purshase['username'], purshase['quantity']))

@serv3.route('/api/get_purshase_history/<username>', methods=['GET'])
def api_get_purshase_history(username):
    return jsonify(get_purshase_history(username))

create_db_table_3()