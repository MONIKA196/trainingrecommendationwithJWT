
import mysql.connector
from werkzeug.security import generate_password_hash

# Database Configuration (matches your app.py)
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'moni@@naga17N5',
    'database': 'training_db'
}

def fix_passwords():
    try:
        db = mysql.connector.connect(**config)
        cursor = db.cursor(dictionary=True)
        
        # 1. Fetch all users
        cursor.execute("SELECT id, username, password_hash FROM users")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users. Checking for plain-text passwords...")
        
        updated_count = 0
        for user in users:
            uid = user['id']
            pwd = user['password_hash']
            
            # Simple check: hashes from Werkzeug usually start with 'scrypt:' or 'pbkdf2:'
            # and are very long. Plain text passwords are usually short and simple.
            if not (pwd.startswith('scrypt:') or pwd.startswith('pbkdf2:')):
                print(f"Hashing password for user: {user['username']}")
                new_hash = generate_password_hash(pwd)
                
                # 2. Update the record
                cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, uid))
                updated_count += 1
        
        db.commit()
        print(f"Done! Updated {updated_count} users.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            db.close()

if __name__ == "__main__":
    fix_passwords()
