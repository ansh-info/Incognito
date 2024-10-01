import sys
import os

# Add the parent directory to sys.path to access the connection module
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from connection.db_connection import get_db_connection  # Import the connection function

DB_NAME = 'doodle'  # Replace with your actual database name
TABLES = {}

TABLES['master_candidates'] = (
    "CREATE TABLE `master_candidates` ("
    "  `candidate_id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `reputation` int(11) NOT NULL,"
    "  `reached` int(11) NOT NULL,"
    "  `answers` int(11) NOT NULL,"
    "  `questions` int(11) NOT NULL,"
    "  `gold_badge_score` int(11) NOT NULL,"
    "  `silver_badge_score` int(11) NOT NULL,"
    "  `bronze_badge_score` int(11) NOT NULL,"
    "  `followers` int(11) NOT NULL,"
    "  `public_repos` int(11) NOT NULL,"
    "  `total_stars` int(11) NOT NULL,"
    "  `total_forks` int(11) NOT NULL,"
    "  `total_contributions` int(11) NOT NULL,"
    "  `total_repos` int(11) NOT NULL,"
    "  `commit_count` int(11) NOT NULL,"
    "  `pull_request_count` int(11) NOT NULL,"
    "  `issue_count` int(11) NOT NULL,"
    "  `member_exp` float NOT NULL,"
    "  PRIMARY KEY (`candidate_id`)"
    ") ENGINE=InnoDB")

def create_database(cursor, db_name):
    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database {db_name} created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print(f"Database {db_name} already exists.")
        else:
            print(f"Failed to create database: {err}")
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
        exit(1)

    try:
        cursor = cnx.cursor()
        create_database(cursor, db_name)
        create_tables(cursor)
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
