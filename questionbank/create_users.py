from __init__ import path
path()

from connection.db_connection import get_db_connection

# Table creation statements
TABLES = {}
TABLES['users'] = (
    "CREATE TABLE IF NOT EXISTS users ("
    "  user_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  username VARCHAR(50) NOT NULL UNIQUE,"
    "  email VARCHAR(255) NOT NULL UNIQUE,"
    "  password VARCHAR(255) NOT NULL,"
    "  is_admin BOOLEAN NOT NULL DEFAULT FALSE"
    ")"
)

TABLES['questions'] = (
    "CREATE TABLE IF NOT EXISTS questions ("
    "  question_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  question_text TEXT NOT NULL"
    ")"
)

TABLES['submissions'] = (
    "CREATE TABLE IF NOT EXISTS submissions ("
    "  submission_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  user_id INT NOT NULL,"
    "  question_id INT NOT NULL,"
    "  code TEXT NOT NULL,"
    "  result BOOLEAN NOT NULL,"
    "  output TEXT,"
    "  email VARCHAR(255) NOT NULL,"
    "  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "  FOREIGN KEY (user_id) REFERENCES users(user_id),"
    "  FOREIGN KEY (question_id) REFERENCES questions(question_id)"
    ")"
)

def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET 'utf8'")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table {table_name}: ", end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

def main():
    # Get the database connection and database name from the connection module
    cnx, db_name = get_db_connection()
    
    if cnx is None or db_name is None:
        print("Connection failed.")
        exit(1)
    
    try:
        cursor = cnx.cursor()
        create_database(cursor, db_name)  # Create database if it doesn't exist
        cnx.database = db_name  # Switch to the created database
        create_tables(cursor)    # Create the required tables
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
