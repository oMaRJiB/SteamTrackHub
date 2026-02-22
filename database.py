import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',              # Change if your MySQL user is different
        password='A1ysia01081978$',  # ← Put your actual MySQL root password
        database='steamtrack_hub'
    )

from werkzeug.security import generate_password_hash, check_password_hash

import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import errorcode

def register_user(username, email, password, role='user'):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')  # safe method
    
    try:
        cursor.execute(
            "INSERT INTO Users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_pw, role)
        )
        conn.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:  # 1062 = duplicate entry
            raise ValueError("Email already in use. Please choose a different email or log in.")
        else:
            raise  # re-raise other errors
    finally:
        cursor.close()
        conn.close()

def login_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

# Add more functions later, e.g., add_game_to_library(...)
