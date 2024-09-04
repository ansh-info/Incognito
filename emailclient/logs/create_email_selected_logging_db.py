import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# MySQL logging database connection details
log_db_config = {
    'user': os.getenv('LOG_DB_USER1'),
    'password': os.getenv('LOG_DB_PASSWORD1'),
    'host': os.getenv('LOG_DB_HOST1'),
    'database': os.getenv('LOG_DB_NAME1')
}

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

        # Create tables
        create_tables(cursor)

    except mysql.connector.Error as err:
        print(err)
    else:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    main()
