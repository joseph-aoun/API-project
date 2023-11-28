from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from __init__ import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')