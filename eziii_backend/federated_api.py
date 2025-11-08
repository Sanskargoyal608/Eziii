from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "federated_data.db"

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM govt_jobs').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in jobs])

@app.route('/api/scholarships', methods=['GET'])
def get_scholarships():
    conn = get_db_connection()
    scholarships = conn.execute('SELECT * FROM scholarships').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in scholarships])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)