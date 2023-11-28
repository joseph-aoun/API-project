from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')