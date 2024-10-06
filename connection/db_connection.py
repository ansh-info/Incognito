import mysql.connector
import os
from mysql.connector import errorcode
from dotenv import load_dotenv
from sqlalchemy import create_engine  # Import for SQLAlchemy
# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    db_name = os.getenv('DB_NAME')  # Retrieve the DB name from env or use default
    try:
        # Try connecting to the database directly
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=db_name,
            port=os.getenv('DB_PORT')
        )
        print(f"Connected to database '{db_name}' successfully.")
        return connection, db_name
    except mysql.connector.Error as err:
        # Handle the case when the database does not exist
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Database '{db_name}' does not exist. Creating it...")
            # Connect without specifying a database to create the database
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT')
            )
            cursor = connection.cursor()
            try:
                # Create the database
                cursor.execute(f"CREATE DATABASE {db_name} DEFAULT CHARACTER SET 'utf8'")
                print(f"Database '{db_name}' created successfully.")
                # Now reconnect to the newly created database
                connection.database = db_name
            except mysql.connector.Error as err:
                print(f"Failed to create database: {err}")
                connection = None
            finally:
                cursor.close()
            return connection, db_name
        else:
            print(f"Error: {err}")
            return None, None

def get_sqlalchemy_engine():
    db_name = os.getenv('DB_NAME')
    try:
        # Create the SQLAlchemy engine
        engine = create_engine(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{db_name}")
        print(f"SQLAlchemy engine for database '{db_name}' created successfully.")
        return engine, db_name
    except Exception as err:
        print(f"Error creating SQLAlchemy engine: {err}")
        return None, None

