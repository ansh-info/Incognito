import mysql.connector
import os
from mysql.connector import errorcode

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'root'),
            database=os.getenv('DB_NAME', 'doodle'),  # Database name here
            port=os.getenv('DB_PORT', 3306)
        )
        db_name = os.getenv('DB_NAME', 'doodle')  # Retrieve DB_NAME
        return connection, db_name  # Return both connection and DB name
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None
