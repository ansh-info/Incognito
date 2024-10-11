import os
import logging
import pandas as pd
from datetime import datetime, timedelta
import time
from __init__ import path
path()

from connection.db_connection import get_db_connection, get_sqlalchemy_engine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_stackoverflow_data(engine):
    """Fetch data from the stackoverflow_fetch table using SQLAlchemy."""
    query = """
    SELECT user_id, reputation, reached, answers, questions, gold_badge_score,
           silver_badge_score, bronze_badge_score, githubUrl
    FROM stackoverflow_fetch;
    """
    df = pd.read_sql(query, engine)
    logging.info(f"Fetched {df.shape[0]} records from stackoverflow_fetch table.")
    return df

def fetch_github_data(engine):
    """Fetch data from the github_fetch table using SQLAlchemy."""
    query = """
    SELECT username, followers, public_repos, total_stars, total_forks, total_contributions,
           total_repos, commit_count, pull_request_count, issue_count
    FROM github_fetch;
    """
    df = pd.read_sql(query, engine)
    logging.info(f"Fetched {df.shape[0]} records from github_fetch table.")
    return df

def merge_data(stackoverflow_data, github_data):
    """Merge StackOverflow and GitHub data based on GitHub usernames."""
    
    # Extract GitHub usernames from the 'githubUrl' in StackOverflow data
    stackoverflow_data['github_username'] = stackoverflow_data['githubUrl'].apply(lambda x: x.split('/')[-1] if pd.notnull(x) else None)

    logging.info(f"Unique user_ids from StackOverflow: {stackoverflow_data['user_id'].unique()}")
    logging.info(f"Unique GitHub usernames from StackOverflow: {stackoverflow_data['github_username'].unique()}")
    logging.info(f"Unique usernames from GitHub: {github_data['username'].unique()}")
    
    # Merge the data based on the extracted GitHub username
    merged_data = pd.merge(stackoverflow_data, github_data, how='inner', left_on='github_username', right_on='username')
    
    logging.info(f"Merged data contains {merged_data.shape[0]} records.")
    
    # Log sample of the merged data
    logging.debug(f"Merged Data Sample:\n{merged_data.head()}")
    
    # Drop the 'username' and 'github_username' columns as they are not needed after the merge
    merged_data = merged_data.drop(columns=['username', 'github_username'])
    return merged_data

def insert_master_candidates(db_connection, merged_data):
    """Insert merged data into the master_candidates table, skipping existing records."""
    cursor = db_connection.cursor()

    insert_query = """
    INSERT INTO master_candidates (reputation, reached, answers, questions, gold_badge_score, silver_badge_score, 
                                   bronze_badge_score, followers, public_repos, total_stars, total_forks, 
                                   total_contributions, total_repos, commit_count, pull_request_count, issue_count, member_exp)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    select_query = """
    SELECT COUNT(*) FROM master_candidates WHERE reputation = %s AND reached = %s AND answers = %s AND questions = %s
    AND gold_badge_score = %s AND silver_badge_score = %s AND bronze_badge_score = %s AND followers = %s
    AND public_repos = %s AND total_stars = %s AND total_forks = %s AND total_contributions = %s
    AND total_repos = %s AND commit_count = %s AND pull_request_count = %s AND issue_count = %s
    """

    records_to_insert = 0
    
    for _, row in merged_data.iterrows():
        # Calculate member experience as an example (could be based on data)
        member_exp = row['reputation'] / 10000.0
        
        # Check if the record already exists in the database
        cursor.execute(select_query, (
            int(row['reputation']), int(row['reached']), int(row['answers']), int(row['questions']),
            int(row['gold_badge_score']), int(row['silver_badge_score']), int(row['bronze_badge_score']),
            int(row['followers']), int(row['public_repos']), int(row['total_stars']), int(row['total_forks']),
            int(row['total_contributions']), int(row['total_repos']), int(row['commit_count']),
            int(row['pull_request_count']), int(row['issue_count'])
        ))
        
        # Fetch the result of the query (count of existing records)
        count = cursor.fetchone()[0]
        
        if count == 0:
            # If the record does not exist, insert it
            cursor.execute(insert_query, (
                int(row['reputation']), int(row['reached']), int(row['answers']), int(row['questions']),
                int(row['gold_badge_score']), int(row['silver_badge_score']), int(row['bronze_badge_score']),
                int(row['followers']), int(row['public_repos']), int(row['total_stars']), int(row['total_forks']),
                int(row['total_contributions']), int(row['total_repos']), int(row['commit_count']),
                int(row['pull_request_count']), int(row['issue_count']), member_exp
            ))
            records_to_insert += 1
    
    db_connection.commit()
    logging.info(f"Inserted {records_to_insert} new records into the master_candidates table.")
    cursor.close()


def main():
    # Get MySQL connection using the centralized connection handler
    db_conn, _ = get_db_connection()
    
    try:
        # Get SQLAlchemy engine from the centralized connection handler
        engine, _ = get_sqlalchemy_engine()

        if engine is None:
            logging.error("Failed to create SQLAlchemy engine. Exiting.")
            return

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
        if db_conn and db_conn.is_connected():
            db_conn.close()

if __name__ == "__main__":
    # Run the script every 10 seconds for fetching
    while True:
        main()
        # Sleep for 10 seconds (use 5 * 24 * 60 * 60 for 5 days in production)
        time.sleep(10)
