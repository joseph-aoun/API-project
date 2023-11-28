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
    message = {}
    try:
        with connect_to_db() as conn:
            conn.execute('''
                UPDATE inventory SET quantity = quantity - 1 WHERE name = ?;
            ''', (name,))
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

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/add_good', methods=['POST'])
def api_add_good():
    good = request.get_json()
    try:
        add_good(good)
        return jsonify({'status': 'Good added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'Good already exists'})
    except:
        return jsonify({'status': 'Good addition failed'})

@app.route('/api/get_goods', methods=['GET'])
def api_get_goods():
    return jsonify(get_goods())

@app.route('/api/update_good', methods=['POST'])
def api_update_good():
    good = request.get_json()
    return jsonify(update_good(good))

@app.route('/api/deduct_good', methods=['POST'])
def api_deduct_good():
    name = request.get_json()
    return jsonify(deduct_good(name))

create_db_table()

if __name__ == '__main__':
    app.run(debug=True, port=5000, host = '0.0.0.0')
    
'''
pm.environment.set("name", "chips");
pm.environment.set("category", "food");
pm.environment.set("price", 10);
pm.environment.set("quantity", 10);
pm.environment.set("description", "crispy");
'''