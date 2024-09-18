import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

# MySQL database connection details
config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'port': os.getenv('DB_PORT'),  # Replace with your MySQL container port if different
}

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

def create_database(cursor):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']} DEFAULT CHARACTER SET 'utf8'")
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
    try:
        cnx = mysql.connector.connect(user=config['user'], password=config['password'], host=config['host'])
        cursor = cnx.cursor()
        create_database(cursor)
        cnx.database = config['database']
        create_tables(cursor)
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
