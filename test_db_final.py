
import mysql.connector

config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'moni@@naga17N5',
    'database': 'training_db'
}

try:
    print(f"Testing connection to {config['host']}...")
    db = mysql.connector.connect(**config)
    print("SUCCESS: Connection established.")
    db.close()
except Exception as e:
    print(f"FAILURE: {e}")
