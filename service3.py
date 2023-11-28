import sqlite3
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from service2 import connect_to_db
serv3 = Blueprint('service3', __name__)


def get_good_by_name(name):
    
    """ this function retrieves a good from the inventory table in the database

        Args:
            name (str): the name of the good to be retrieved
        
        Returns:
            good: the good retrieved from the inventory table
    """
    
    item = {}
    
    try:
        with connect_to_db() as conn:
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
        conn = connect_to_db()
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

@serv3.route('/api/get_goods', methods=['GET'])
def api_get_goods():
    return jsonify(get_goods())

@serv3.route('/api/get_good_by_name/<name>', methods=['GET'])
def api_get_good_by_name(name):
    return jsonify(get_good_by_name(name))

