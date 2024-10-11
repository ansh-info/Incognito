import os
from __init__ import path
path()

from connection.db_connection import get_db_connection
import logging
from mysql.connector import Error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_connection():
    """ Get a database connection using mysql.connector (centralized logic). """
    cnx, DB_NAME = get_db_connection()  # Using your centralized logic to get the connection
    return cnx, DB_NAME


def fetch_records_by_table(table_name):
    """ Fetch all records from a specified table using mysql.connector. """
    records = []
    cnx, DB_NAME = get_connection()
    cursor = None
    try:
        if cnx.is_connected():
            cursor = cnx.cursor(dictionary=True)
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            records = cursor.fetchall()
    except Error as e:
        logging.error(f"Error fetching records: {e}")
    finally:
        if cursor:
            cursor.close()
        cnx.close()
    return records


def insert_stackoverflow_data(user_data):
    """ Insert user profile into the database if not already present using mysql.connector. """
    cnx, DB_NAME = get_connection()
    cursor = None
    try:
        if cnx.is_connected():
            cursor = cnx.cursor()

            # Step 1: Check if the user_id already exists in the table
            check_sql = "SELECT COUNT(*) FROM stackoverflow_fetch WHERE user_id = %s"
            cursor.execute(check_sql, (user_data['user_id'],))
            count = cursor.fetchone()[0]

            if count == 0:  # No existing record, proceed with insert
                # Step 2: Insert the new record into the database
                insert_sql = """
                    INSERT INTO stackoverflow_fetch (
                        profileURL, user_id, githubUrl, reputation, reached, answers, questions, 
                        gold_badge_score, silver_badge_score, bronze_badge_score, top_5_tags
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    user_data['profileURL'], user_data['user_id'], user_data['githubUrl'], user_data['reputation'], 
                    user_data['reached'], user_data['answers'], user_data['questions'], 
                    user_data['gold_badge_score'], user_data['silver_badge_score'], user_data['bronze_badge_score'], 
                    user_data['top_5_tags']
                ))
                cnx.commit()
            else:
                logging.info(f"User {user_data['user_id']} already exists in the database.")
    except Error as e:
        logging.error(f"Error inserting data: {e}")
    finally:
        if cursor:
            cursor.close()
        cnx.close()


def fetch_github_urls_from_table(table_name, last_processed=None):
    """ Fetch GitHub URLs and their corresponding IDs from the given table using mysql.connector. """
    cnx, DB_NAME = get_connection()
    github_records = []
    cursor = None
    try:
        if cnx.is_connected():
            cursor = cnx.cursor(dictionary=True)
            query = f"SELECT id, githubUrl FROM {table_name} WHERE githubUrl IS NOT NULL"
            if last_processed:
                query += f" AND id > {last_processed}"
            cursor.execute(query)
            github_records = cursor.fetchall()

            # Add debugging to check the structure of the returned data
            logging.info(f"Fetched records: {github_records}")
    except Error as e:
        logging.error(f"Error fetching GitHub URLs: {e}")
    finally:
        if cursor:
            cursor.close()
        cnx.close()

    return github_records


def execute_sql_file(file_path):
    """ Execute SQL commands from a file using mysql.connector. """
    cnx, DB_NAME = get_connection()
    cursor = None
    try:
        if cnx.is_connected():
            cursor = cnx.cursor()
            with open(file_path, 'r') as file:
                sql_commands = file.read().split(';')
                for command in sql_commands:
                    if command.strip():
                        cursor.execute(command)
            cnx.commit()
    except Error as e:
        logging.error(f"Error executing SQL file: {e}")
    finally:
        if cursor:
            cursor.close()
        cnx.close()


def setup_database_and_tables(sql_file_name):
    """ Set up the database and tables using mysql.connector, using the provided SQL file. """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_directory, sql_file_name)

    # Execute the SQL commands to set up the database and tables
    execute_sql_file(sql_file_path)
    logging.info("Database and tables set up successfully.")


if __name__ == "__main__":
    # Example of setting up the database and tables with a SQL file
    setup_database_and_tables('queries.txt')
