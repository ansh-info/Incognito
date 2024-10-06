import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
import os

def create_database_if_not_exists(host, user, password, database_name):
    """ Create a database if it does not already exist """
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = connection.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database '{database_name}' checked/created successfully.")

        cursor.close()
        connection.close()

    except Error as e:
        print(f"Error while creating/checking database: {e}")

@contextmanager
def get_db_connection(host='localhost', user='root', password='root', database_name='incognito'):
    """ Get a DB connection, create database if it doesn't exist, and always close connection after use """
    connection = None
    try:     
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database_name 
        )
        yield connection
    except Error as e:
        print(f"Error occurred: {e}")
        yield None
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection is closed")

def execute_sql_file(cursor, file_path):
    """ Execute SQL commands from a file """
    with open(file_path, 'r') as file:
        sql_commands = file.read().split(';')
        for command in sql_commands:
            if command.strip():
                try:
                    cursor.execute(command)
                except Error as e:
                    print(f"Error executing command: {e}")

def setup_database_and_tables(sql_file_name):
    """ Set up the database and tables on initial run """

    current_directory = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_directory, sql_file_name)

    with get_db_connection() as connection:
        if connection and connection.is_connected():
            cursor = connection.cursor()
            execute_sql_file(cursor, sql_file_path)
            connection.commit()
            print("Tables created successfully.")

if __name__ == "__main__":
    host='localhost'
    user='root'
    password='root'
    database_name='incognito'
    create_database_if_not_exists(host, user, password, database_name)
    setup_database_and_tables('queries.txt')
