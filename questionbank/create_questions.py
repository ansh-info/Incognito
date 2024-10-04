from __init__ import path
path()

from connection.db_connection import get_db_connection
import mysql.connector
from mysql.connector import errorcode

cnx, DB_NAME = get_db_connection()

TABLES = {
    'questions': (
        "CREATE TABLE `questions` ("
        "  `question_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `title` varchar(255) NOT NULL,"
        "  `description` text NOT NULL,"
        "  `difficulty` varchar(50) NOT NULL,"
        "  PRIMARY KEY (`question_id`)"
        ") ENGINE=InnoDB"),
    
    'test_cases': (
        "CREATE TABLE `test_cases` ("
        "  `test_case_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `question_id` int(11) NOT NULL,"
        "  `input` text NOT NULL,"
        "  `expected_output` text NOT NULL,"
        "  PRIMARY KEY (`test_case_id`),"
        "  KEY `question_id` (`question_id`),"
        "  CONSTRAINT `test_cases_ibfk_1` FOREIGN KEY (`question_id`) "
        "     REFERENCES `questions` (`question_id`) ON DELETE CASCADE"
        ") ENGINE=InnoDB"
    )
}

def create_database(cursor):
    try:
        cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database {DB_NAME} created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print(f"Database {DB_NAME} already exists.")
        else:
            print(f"Failed to create database: {err}")
            exit(1)

def create_tables(cursor):
    cursor.execute(f"USE {DB_NAME}")
    for table_name, table_description in TABLES.items():
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
    if cnx is None or DB_NAME is None:
        print("Connection failed.")
        exit(1)
    try:
        cursor = cnx.cursor()
        create_database(cursor)
        create_tables(cursor)
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
