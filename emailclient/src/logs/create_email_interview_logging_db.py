import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# MySQL logging database connection details
log_db_config = {
    'user': os.getenv('LOG_DB_USER'),
    'password': os.getenv('LOG_DB_PASSWORD'),
    'host': os.getenv('LOG_DB_HOST')
}

# Database and table creation statements
DB_NAME = 'doodle'

TABLES = {}
TABLES['email_interview_loggs'] = (
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
        cnx = mysql.connector.connect(**log_db_config)
        cursor = cnx.cursor()

        # Create database
        try:
            cnx.database = DB_NAME
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                create_database(cursor)
                cnx.database = DB_NAME
            else:
                print(err)
                exit(1)

        # Create tables
        create_tables(cursor)

    except mysql.connector.Error as err:
        print(err)
    else:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    main()
