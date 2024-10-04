from __init__ import path
path()

from connection.db_connection import get_db_connection
import mysql.connector 
from mysql.connector import errorcode

try:
    # Get the database connection and database name
    cnx, db_name = get_db_connection()

    if cnx is None or db_name is None:
        print("Connection failed.")
        exit(1)

    cursor = cnx.cursor()

    # Check if the database exists
    cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
    database_exists = cursor.fetchone()

    if not database_exists:
        # Create the database if it does not exist
        print(f"Database '{db_name}' does not exist. Creating database...")
        cursor.execute(f"CREATE DATABASE {db_name}")
    else:
        print(f"Database '{db_name}' already exists.")

    # Select the database
    cursor.execute(f"USE {db_name}")

    # Check if the table exists
    cursor.execute("SHOW TABLES LIKE 'suitable_candidates'")
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create the table if it does not exist
        print("Table 'suitable_candidates' does not exist. Creating table...")
        create_table_query = """
        CREATE TABLE suitable_candidates (
            user_id INT PRIMARY KEY,
            username VARCHAR(255),
            email VARCHAR(255),
            reputation INT,
            reached INT,
            answers INT,
            questions INT,
            gold_badge_score INT,
            silver_badge_score INT,
            bronze_badge_score INT,
            followers INT,
            public_repos INT,
            total_stars INT,
            total_forks INT,
            total_contributions INT,
            total_repos INT,
            commit_count INT,
            pull_request_count INT,
            issue_count INT,
            member_exp FLOAT,
            prediction INT  -- For storing the logistic regression prediction
        );
        """
        cursor.execute(create_table_query)
        print("Table 'suitable_candidates' created successfully.")
    else:
        print("Table 'suitable_candidates' already exists.")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
finally:
    cursor.close()
    cnx.close()
    print("MySQL connection closed.")
