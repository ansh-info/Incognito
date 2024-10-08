from mysql_db_handler import get_db_connection
from mysql.connector import Error

#Todo: Later change table user to leetcode table

def get_connection():
    """ Get a database connection. """
    return get_db_connection()

def fetch_records_by_table(table_name):
    """ Fetch all records from a specified table """
    records = []
    with get_db_connection() as connection:
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT * FROM {table_name}"
                cursor.execute(query)
                records = cursor.fetchall()
            except Error as e:
                print(f"Error occurred: {e}")
            finally:
                cursor.close()
    return records

def insert_stackoverflow_data(user_data):
    """Insert user profile into the database if not already present, handling the connection internally."""
    connection = None
    cursor = None
    try:
        with get_connection() as connection:  # Establish the connection
            if connection:
                cursor = connection.cursor()
                
                # Step 1: Check if the user_id already exists in the table
                check_sql = "SELECT COUNT(*) FROM stackoverflow_fetch WHERE user_id = %s"
                cursor.execute(check_sql, (user_data['user_id'],))
                result = cursor.fetchone()

                if result[0] == 0:  # No existing record, proceed with insert
                    # Step 2: Insert the new record into the database
                    insert_sql = """
                    INSERT INTO stackoverflow_fetch (
                        profileURL, user_id, githubUrl, reputation, reached, answers, questions, 
                        gold_badge_score, silver_badge_score, bronze_badge_score, top_5_tags
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (
                        user_data['profileURL'], 
                        user_data['user_id'], 
                        user_data['githubUrl'], 
                        user_data['reputation'], 
                        user_data['reached'], 
                        user_data['answers'], 
                        user_data['questions'], 
                        user_data['gold_badge_score'], 
                        user_data['silver_badge_score'], 
                        user_data['bronze_badge_score'], 
                        user_data['top_5_tags']
                    ))
                    connection.commit()  # Commit the transaction
                    print(f"User {user_data['user_id']} inserted successfully.")
                else:
                    # Record already exists
                    print(f"User {user_data['user_id']} already exists in the database.")
    
    except Error as e:
        print(f"Error occurred: {e}")
        if connection:
            connection.rollback()  # Undo any changes if an error occurs
    
    finally:
        if cursor:
            cursor.close()  # Ensure the cursor is closed after the operation

def fetch_github_urls_from_table(table_name, last_processed=None):
    """Fetch GitHub URLs and their corresponding IDs from the given table, starting from the last processed record."""
    github_records = []
    with get_db_connection() as connection:
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            try:
                query = f"SELECT id, githubUrl FROM {table_name} WHERE githubUrl IS NOT NULL"
                if last_processed:
                    query += f" AND id > {last_processed}"  # Start from the last processed record
                cursor.execute(query)
                github_records = cursor.fetchall()
            except Error as e:
                print(f"Error occurred: {e}")
            finally:
                cursor.close()
    return github_records

