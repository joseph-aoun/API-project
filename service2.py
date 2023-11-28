import sqlite3
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from service3 import app

service2 = Blueprint('service2', __name__)

def connect_to_db():
    conn = sqlite3.connect('inventory_database.db')
    return conn

def create_db_table():
    
    """ 
        this function creates the inventory table in the database

        returns:
            conn: connection to the database
    """
    
    try:
        with connect_to_db() as conn:
            conn.execute('''
                CREATE TABLE inventory (
                    item_id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    description TEXT NOT NULL
                );
            ''')
            conn.commit()
            print("Inventory table created successfully")
    except:
        print("Inventory table creation failed - Maybe table already exists")
    finally:
        conn.close()
        
def add_good(good):
    """
        this function adds a good to the inventory table in the database
        
        args:
            good: the good to be added to the inventory table
        
        raises:
            sqlite3.IntegrityError: if the good already exists
    """
    
    if get_good_by_name(good['name']):
        raise sqlite3.IntegrityError
    try:
        with connect_to_db() as conn:
            conn.execute('''
                INSERT INTO inventory (name, category, price, quantity, description)
                VALUES (?, ?, ?, ?, ?);
            ''', (good['name'], good['category'], good['price'], good['quantity'], good['description']))
            conn.commit()
            print("Good added successfully")
    except:
        print("Good addition failed")
    finally:
        conn.close()

def get_good_by_name(name):
    
    """ this function retrieves a good from the inventory table in the database

        Args:
            name (str): the name of the good to be retrieved
        
        Returns:
            good: the good retrieved from the inventory table
    """
    
    try:
        with connect_to_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM inventory WHERE name = ?;
            ''', (name,))
            good = cursor.fetchone()
            return good
    except:
        print("Good retrieval failed")
    finally:
        conn.close()

def update_good(good):
    """ 
        this function updates a good in the inventory table in the database
        
        args:
            good: the good to be updated in the inventory table
        
        returns:
            updated_good: the good that has been updated
    """
    
    updated_good = {}
    try:
        with connect_to_db() as conn:
            conn.execute('''
                UPDATE inventory SET name = ?, category = ?, price = ?, quantity = ?, description = ? WHERE item_id = ?;
            ''', (good['name'], good['category'], good['price'], good['quantity'], good['description'], good['item_id']))
            conn.commit()
            print("Good updated successfully")
            updated_good = get_good_by_name(good['name'])
    except:
        print("Good update failed")
    finally:
        conn.close()
    return updated_good

def deduct_good(name):
    """ this function deducts a good from the inventory table in the database

        Args:
            name (str): the name of the good to be deducted
            
        Returns:
            message: a message indicating the status of the deduction
    """
    
    message = {}
    try:
        with connect_to_db() as conn:
            conn.execute('''
                UPDATE inventory SET quantity = quantity - 1 WHERE name = ?;
            ''', (name['name'],))
            conn.commit()
            cursor = conn.execute('''
                SELECT quantity FROM inventory WHERE name = ?;
            ''', (name['name'],))
            quantity = cursor.fetchone()
            print("Good deducted successfully")
            message['quantity'] = quantity[0]
            message['status'] = "Good deducted successfully"
    except:
        print("Good deduction failed")
        message['status'] = "Good deduction failed"
    finally:
        conn.close()
    return message

def get_goods():
    
    """ this function retrieves all goods from the inventory table in the database

        Returns:
            goods: the goods retrieved from the inventory table
    """
    
    goods = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM inventory")
        rows = cur.fetchall()
        for row in rows:
            goods.append(dict(row))
    except:
        goods = []
    finally:
        conn.close()
    return goods

@service2.route('/api/add_good', methods=['POST'])
def api_add_good():
    good = request.get_json()
    try:
        add_good(good)
        return jsonify({'status': 'Good added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'Good already exists'})
    except:
        return jsonify({'status': 'Good addition failed'})

@service2.route('/api/get_goods', methods=['GET'])
def api_get_goods():
    return jsonify(get_goods())

@service2.route('/api/update_good', methods=['POST'])
def api_update_good():
    good = request.get_json()
    return jsonify(update_good(good))

@service2.route('/api/deduct_good', methods=['PUT'])
def api_deduct_good():
    name = request.get_json()
    return jsonify(deduct_good(name))

@service2.route('/api/get_good_by_name/<name>', methods=['GET'])
def api_get_good_by_name(name):
    return jsonify(get_good_by_name(name))

create_db_table()