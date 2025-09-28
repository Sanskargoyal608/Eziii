import sqlite3
from flask import Flask, jsonify
from flask_cors import CORS

# --- Configuration ---
DB_FILE = "federated_data.db"
app = Flask(__name__)

# Configure CORS to allow requests from your React app's origin.
# Also, add your partner's IP address to allow their Django server to make requests.
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://192.168.52.110:8000"]
    }
})

# --- Helper Function ---
def get_db_connection():
    """Establishes a connection to the database and sets the row factory."""
    conn = sqlite3.connect(DB_FILE)
    # This line allows you to access columns by name (like a dictionary).
    conn.row_factory = sqlite3.Row
    return conn

# --- API Endpoints ---

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Fetches all government jobs from the database."""
    try:
        with get_db_connection() as conn:
            jobs = conn.execute('SELECT * FROM govt_jobs ORDER BY closing_date DESC').fetchall()
            # Convert the list of Row objects to a list of dictionaries.
            job_list = [dict(row) for row in jobs]
            return jsonify(job_list)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to retrieve jobs from the database"}), 500

@app.route('/api/scholarships', methods=['GET'])
def get_scholarships():
    """Fetches all scholarships from the database."""
    try:
        with get_db_connection() as conn:
            scholarships = conn.execute('SELECT * FROM scholarships ORDER BY deadline DESC').fetchall()
            scholarship_list = [dict(row) for row in scholarships]
            return jsonify(scholarship_list)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to retrieve scholarships from the database"}), 500

# --- Run the App ---

if __name__ == '__main__':
    # debug=True will auto-reload the server when you make changes.
    # host='0.0.0.0' makes the server accessible from other devices on your network.
    # The default port is 5000.
    app.run(host='0.0.0.0', debug=True, port=5000)