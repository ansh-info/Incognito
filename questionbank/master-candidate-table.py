import mysql.connector
from mysql.connector import errorcode

# MySQL database connection details (hardcoded)
config = {
    'user': 'root',         # Replace with your DB username
    'password': '9084Mysql#', # Replace with your DB password
    'host': '0.0.0.0',         # Replace with your DB host (e.g., 'localhost' or '127.0.0.1')
    'database': 'doodle',   # If you want to include the database here, uncomment and set the database name
    'port': '3306',       # If needed, replace with your DB port, usually 3306 for MySQL
}

DB_NAME = 'doodle'            # Replace with your actual database name
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

def create_database(cursor):
    try:
        cursor.execute(
            f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database {DB_NAME} created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print(f"Database {DB_NAME} already exists.")
        else:
            print(f"Failed to create database: {err}")
            exit(1)

def create_tables(cursor):
    cursor.execute(f"USE {DB_NAME}")
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
    try:
        cnx = mysql.connector.connect(**config)
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
