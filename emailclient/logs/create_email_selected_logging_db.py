import mysql.connector
from mysql.connector import errorcode

from __init__ import path
path()

from connection.db_connection import get_db_connection

cnx, DB_NAME = get_db_connection()

# Table creation statements
TABLES = {}
TABLES['email_selection_logging'] = (
    "CREATE TABLE `email_selection_logging` ("
    "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
    "  `submission_id` INT NOT NULL,"
    "  `user_id` INT NOT NULL,"
    "  `question_id` INT NOT NULL,"
    "  `code` TEXT NOT NULL,"
    "  `result` INT NOT NULL,"
    "  `email` VARCHAR(255) NOT NULL,"
    "  `status` VARCHAR(50) NOT NULL,"
    "  `error_message` TEXT,"
    "  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

def create_tables(cursor):
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table {table_name}: ", end='')
            cursor.execute(table_description)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)

def main():
    # Get the database connection and database name
    cnx, db_name = get_db_connection()

    if cnx is None or db_name is None:
        print("Connection failed.")
        return

    try:
        cursor = cnx.cursor()

        # Create tables
        create_tables(cursor)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    main()
