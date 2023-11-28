from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

def create_app():
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    CORS(app)
    
    from .service1 import service1
    from .service2 import service2
    
    app.register_blueprint(service1)
    app.register_blueprint(service2)
    
    return app