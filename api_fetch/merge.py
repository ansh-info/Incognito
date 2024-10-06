import os
import logging
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine
import mysql.connector
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Database configuration using environment variables
db_config = {
    'user': 'root',
    'password': 'root',
    'port': '3306',
    'host': '127.0.0.1',
    'database': 'incognito'
}

# URL encode the password
encoded_password = urllib.parse.quote(db_config['password'])

# Create SQLAlchemy engine for pandas compatibility
db_url = f"mysql+mysqlconnector://{db_config['user']}:{encoded_password}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(db_url)

def fetch_stackoverflow_data(engine):
    """Fetch data from the stackoverflow_test table using SQLAlchemy."""
    query = """
    SELECT user_id, reputation, reached, answers, questions, gold_badge_score,
           silver_badge_score, bronze_badge_score
    FROM stackoverflow_test;
    """
    df = pd.read_sql(query, engine)
    logging.info(f"Fetched {df.shape[0]} records from stackoverflow_test table.")
    return df

def fetch_github_data(engine):
    """Fetch data from the github_test table using SQLAlchemy."""
    query = """
    SELECT username, followers, public_repos, total_stars, total_forks, total_contributions,
           total_repos, commit_count, pull_request_count, issue_count
    FROM github_test;
    """
    df = pd.read_sql(query, engine)
    logging.info(f"Fetched {df.shape[0]} records from github_test table.")
    return df

def merge_data(stackoverflow_data, github_data):
    """Merge StackOverflow and GitHub data based on user_id and username."""
    logging.info(f"Unique user_ids from StackOverflow: {stackoverflow_data['user_id'].unique()}")
    logging.info(f"Unique usernames from GitHub: {github_data['username'].unique()}")
    
    logging.debug(f"StackOverflow Data Sample:\n{stackoverflow_data.head()}")
    logging.debug(f"GitHub Data Sample:\n{github_data.head()}")
    
    merged_data = pd.merge(stackoverflow_data, github_data, how='inner', left_on='user_id', right_on='username')
    
    logging.info(f"Merged data contains {merged_data.shape[0]} records.")
    
    # Log sample of the merged data
    logging.debug(f"Merged Data Sample:\n{merged_data.head()}")
    
    # Drop the 'username' column from the GitHub data since 'user_id' is now used
    merged_data = merged_data.drop(columns=['username'])
    return merged_data


def insert_master_candidates(db_connection, merged_data):
    """Insert merged data into the master_candidates table."""
    cursor = db_connection.cursor()

    insert_query = """
    INSERT INTO master_candidates (reputation, reached, answers, questions, gold_badge_score, silver_badge_score, 
                                   bronze_badge_score, followers, public_repos, total_stars, total_forks, 
                                   total_contributions, total_repos, commit_count, pull_request_count, issue_count, member_exp)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    records_to_insert = 0
    
    for _, row in merged_data.iterrows():
        # Calculate member experience as an example (could be based on data)
        member_exp = row['reputation'] / 10000.0
        
        cursor.execute(insert_query, (
            int(row['reputation']), int(row['reached']), int(row['answers']), int(row['questions']),
            int(row['gold_badge_score']), int(row['silver_badge_score']), int(row['bronze_badge_score']),
            int(row['followers']), int(row['public_repos']), int(row['total_stars']), int(row['total_forks']),
            int(row['total_contributions']), int(row['total_repos']), int(row['commit_count']),
            int(row['pull_request_count']), int(row['issue_count']), member_exp
        ))
        records_to_insert += 1
    
    db_connection.commit()
    logging.info(f"Inserted {records_to_insert} records into the master_candidates table.")
    cursor.close()

def main():
    # Create MySQL connection using mysql.connector for inserts
    db_conn = mysql.connector.connect(**db_config)
    
    try:
        # Fetch StackOverflow and GitHub data
        stackoverflow_data = fetch_stackoverflow_data(engine)
        github_data = fetch_github_data(engine)
        
        # Merge the data from both sources
        merged_data = merge_data(stackoverflow_data, github_data)
        
        # Check if there's any data to insert
        if not merged_data.empty:
            # Insert the merged data into the master_candidates table
            insert_master_candidates(db_conn, merged_data)
        else:
            logging.warning("No data to insert into master_candidates table.")
    
    finally:
        db_conn.close()

if __name__ == "__main__":
    # Run the script every 10 seconds for testing
    while True:
        main()
        # Sleep for 10 seconds (use 5 * 24 * 60 * 60 for 5 days in production)
        time.sleep(10)
