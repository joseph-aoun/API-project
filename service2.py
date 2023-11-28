import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

def connect_to_db():
    conn = sqlite3.connect('inventory_database.db')
    return conn

def create_db_table():
    try:
        with connect_to_db() as conn:
            # it has a name, category(food, clothes, accessories, electronics), price, quantity, description
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
    message = {}
    try:
        with connect_to_db() as conn:
            conn.execute('''
                UPDATE inventory SET name = ?, category = ?, price = ?, quantity = ?, description = ? WHERE item_id = ?;
            ''', (good['name'], good['category'], good['price'], good['quantity'], good['description'], good['item_id']))
            conn.commit()
            print("Good updated successfully")
            message['status'] = "Good updated successfully"
    except:
        print("Good update failed")
        message['status'] = "Good update failed"
    finally:
        conn.close()
    return message

def deduct_good(good_id):
    message = {}
    try:
        with connect_to_db() as conn:
            conn.execute('''
                UPDATE inventory SET quantity = quantity - 1 WHERE item_id = ?;
            ''', (good_id,))
            conn.commit()
            print("Good deducted successfully")
            message['status'] = "Good deducted successfully"
    except:
        print("Good deduction failed")
        message['status'] = "Good deduction failed"
    finally:
        conn.close()
    return message

def get_goods():
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