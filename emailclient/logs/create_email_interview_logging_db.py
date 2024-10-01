import mysql.connector
from mysql.connector import errorcode

from add_parent_path import add_parent_dir_to_path
add_parent_dir_to_path()

from connection.db_connection import get_db_connection

cnx, DB_NAME = get_db_connection()

TABLES = {}
TABLES['email_interview_logging'] = (
    "CREATE TABLE `email_interview_logging` ("
    "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
    "  `user_id` INT NOT NULL,"
    "  `email` VARCHAR(255) NOT NULL,"
    "  `status` VARCHAR(50) NOT NULL,"
    "  `error_message` TEXT,"
    "  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    ") ENGINE=InnoDB"
)

def create_database(cursor):
    try:
        cursor.execute(
            f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database {DB_NAME} created successfully.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

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

        # Try to switch to the existing database
        try:
            cnx.database = DB_NAME
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"Database {DB_NAME} does not exist. Creating it...")
                create_database(cursor)
                cnx.database = DB_NAME
            else:
                print(err)
                exit(1)

        # Create tables
        create_tables(cursor)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    main()
