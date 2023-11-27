from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

# the following code is from service1.py 
# the code was created by: Joseph Aoun and Samer Saade

def connect_to_db():
    
    """ this function connects to the database
    Returns:
        conn: connection to the database
    """
    
    conn = sqlite3.connect('customer_database.db')
    return conn

def create_db_table():
    
    """ this function creates the customer table in the database
    """
    
    try:
        with connect_to_db() as conn:
            conn.execute('''
                CREATE TABLE customers (
                    customer_id INTEGER PRIMARY KEY NOT NULL,
                    full_name TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    address TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    marital_status TEXT NOT NULL,
                    wallet_balance REAL DEFAULT 0
                );
            ''')
            conn.commit()
            print("Customer table created successfully")
    except:
        print("Customer table creation failed - Maybe table already exists")
    finally:
        conn.close()

def insert_customer(customer):
    
    """ this function inserts a customer into the database
    Args:
        customer: the customer to be inserted
    
    Returns:
        inserted_customer: the inserted customer
        
    Raises:
        sqlite3.IntegrityError: if the username is already taken
    """

    if get_customer_by_username(customer['username']):
        raise sqlite3.IntegrityError
    
    inserted_customer = {}
    try:
        with connect_to_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO customers (full_name, username, password, age, address, gender, marital_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (customer['full_name'], customer['username'], customer['password'], customer['age'], customer['address'], customer['gender'], customer['marital_status']))
            conn.commit()
            inserted_customer = get_customer_by_id(cur.lastrowid)
    except sqlite3.IntegrityError:
        conn.rollback()
        print("Error: Username already taken")
    finally:
        conn.close()
    return inserted_customer

def get_customers():
    
    """ this function gets all the customers from the database

    Returns:
        a list of all the customers
    """
    
    customers = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers")
        rows = cur.fetchall()
        for i in rows:
            customer = dict(i)
            customers.append(customer)
    except:
        customers = []
    finally:
        conn.close()
    return customers

def get_customer_by_id(customer_id):
    
    """ this function gets a customer by id from the database

    Args:
        customer_id (int): the id of the customer to be retrieved
    
    Returns:
        customer: the customer retrieved from the database
    """
    
    customer = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        row = cur.fetchone()
        if row:
            customer = dict(row)
    except:
        customer = {}
    finally:
        conn.close()
    return customer

def get_customer_by_username(username):
    customer = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            customer = dict(row)
    except:
        customer = {}
    finally:
        conn.close()
    return customer

def update_customer(customer):
    updated_customer = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET full_name = ?, password = ?, age = ?, address = ?, gender = ?, marital_status = ? WHERE username = ?",
                    (customer["full_name"], customer["password"], customer["age"], customer["address"], customer["gender"], customer["marital_status"], customer["username"]))
        conn.commit()
        updated_customer = get_customer_by_username(customer["username"])
    except:
        conn.rollback()
        updated_customer = {}
    finally:
        conn.close()
    return updated_customer

def delete_customer(username):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE FROM customers WHERE username = ?", (username,))
        conn.commit()
        message["status"] = "Customer deleted successfully"
    except:
        conn.rollback()
        message["status"] = "Cannot delete customer"
    finally:
        conn.close()
    return message

def charge_customer_wallet(username, amount):
    
    """ this function charges a customer's wallet by a certain amount
    
    Args:
        username (str): the username of the customer
        amount (float): the amount to be charged
    """
    
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET wallet_balance = wallet_balance + ? WHERE username = ?", (amount, username))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

def deduct_from_customer_wallet(username, amount):
    
    """ this function deducts from a customer's wallet by a certain amount
    
    Args:
        username (str): the username of the customer
        amount (float): the amount to be deducted
    """
    
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET wallet_balance = wallet_balance - ? WHERE username = ?", (amount, username))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

create_db_table()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# The following code is the API endpoints for the customer service

@app.route('/api/customers', methods=['GET'])
def api_get_customers():
    return jsonify(get_customers())

@app.route('/api/customers/<customer_id>', methods=['GET'])
def api_get_customer(customer_id):
    return jsonify(get_customer_by_id(customer_id))

@app.route('/api/customers/add', methods=['POST'])
def api_add_customer():
    customer = request.get_json()
    return jsonify(insert_customer(customer))

@app.route('/api/customers/update', methods=['PUT'])
def api_update_customer():
    customer = request.get_json()
    return jsonify(update_customer(customer))

@app.route('/api/customers/delete/<username>', methods=['DELETE'])
def api_delete_customer(username):
    return jsonify(delete_customer(username))

@app.route('/api/customers/charge_wallet', methods=['PUT'])
def api_charge_customer_wallet():
    customer = request.get_json()
    charge_customer_wallet(customer["username"], customer["amount"])
    return jsonify(get_customer_by_username(customer["username"]))

@app.route('/api/customers/deduct_wallet', methods=['PUT'])
def api_deduct_from_customer_wallet():
    customer = request.get_json()
    deduct_from_customer_wallet(customer["username"], customer["amount"])
    return jsonify(get_customer_by_username(customer["username"]))

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')

#now I'm modyfying another branch