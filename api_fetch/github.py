import pandas as pd
import requests
from db_operations import fetch_github_urls_from_table
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the path and database connection logic
from __init__ import path
path()

from connection.db_connection import get_db_connection
import mysql.connector
from mysql.connector import errorcode

# Establish the database connection
cnx, DB_NAME = get_db_connection()

# Fetch token and count file from the .env file
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
COUNT_FILE = os.getenv('COUNT_FILE')

# Headers for GitHub API
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

def extract_github_username(url):
    """Extract GitHub username from a GitHub URL."""
    if url:
        print(f"Extracting GitHub username from URL: {url}")
        return url.split('/')[-1]  # Assumes URL is well-formed and username is the last component
    print("URL is None or invalid.")
    return None

def convert_to_mysql_datetime(iso_datetime):
    """Convert ISO 8601 datetime (from GitHub) to MySQL DATETIME format."""
    try:
        return datetime.strptime(iso_datetime, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(f"Error converting datetime: {iso_datetime}, Error: {e}")
        return None

def get_github_user_data(username):
    """Fetch detailed GitHub user data using the GitHub API."""
    print(f"Fetching user data for GitHub username: {username}")
    user_url = f"https://api.github.com/users/{username}"
    response = requests.get(user_url, headers=HEADERS)

    if response.status_code == 200:
        user_data = response.json()
        created_at_mysql = convert_to_mysql_datetime(user_data['created_at'])
        updated_at_mysql = convert_to_mysql_datetime(user_data['updated_at'])

        return {
            'username': username,
            'followers': user_data['followers'],
            'following': user_data['following'],
            'public_repos': user_data['public_repos'],
            'public_gists': user_data['public_gists'],
            'hireable': user_data.get('hireable'),
            'bio': user_data.get('bio'),
            'location': user_data.get('location'),
            'company': user_data.get('company'),
            'email': user_data.get('email'),
            'created_at': created_at_mysql,
            'updated_at': updated_at_mysql
        }
    else:
        print(f"Failed to fetch user data for {username}: {response.status_code}")
        return None

def get_github_repos_data(username):
    """Fetch GitHub repository data and calculate additional metrics."""
    repos_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(repos_url, headers=HEADERS)

    if response.status_code == 200:
        try:
            repos_data = response.json()
            if isinstance(repos_data, dict) and repos_data.get('message') == 'Not Found':
                print(f"Repositories not found for username: {username}")
                return None

            total_stars = sum(repo['stargazers_count'] for repo in repos_data)
            total_forks = sum(repo['forks_count'] for repo in repos_data)
            total_contributions = sum(repo['size'] for repo in repos_data)  # Size as a proxy for contributions
            total_repos = len(repos_data)
            languages = list(set(repo['language'] for repo in repos_data if repo['language']))

            commit_count = sum(get_commit_count(username, repo['name']) for repo in repos_data)
            pull_request_count = sum(get_pull_request_count(username, repo['name']) for repo in repos_data)
            issue_count = sum(get_issue_count(username, repo['name']) for repo in repos_data)

            return {
                'total_stars': total_stars,
                'total_forks': total_forks,
                'total_contributions': total_contributions,
                'total_repos': total_repos,
                'languages': ', '.join(filter(None, languages)),
                'commit_count': commit_count,
                'pull_request_count': pull_request_count,
                'issue_count': issue_count
            }
        except Exception as e:
            print(f"Error processing repository data for {username}: {e}")
            return None
    else:
        print(f"Failed to fetch repository data for {username}: {response.status_code}")
        return None

def get_commit_count(username, repo_name):
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    response = requests.get(commits_url, headers=HEADERS)
    return len(response.json()) if response.status_code == 200 else 0

def get_pull_request_count(username, repo_name):
    pulls_url = f"https://api.github.com/repos/{username}/{repo_name}/pulls?state=all"
    response = requests.get(pulls_url, headers=HEADERS)
    return len(response.json()) if response.status_code == 200 else 0

def get_issue_count(username, repo_name):
    issues_url = f"https://api.github.com/repos/{username}/{repo_name}/issues?state=all"
    response = requests.get(issues_url, headers=HEADERS)
    return len(response.json()) if response.status_code == 200 else 0

def get_github_data(username):
    """Combine GitHub user data and repository data into a single dictionary."""
    user_data = get_github_user_data(username)
    repos_data = get_github_repos_data(username)

    if user_data and repos_data:
        return {**user_data, **repos_data}
    elif user_data:
        return user_data  # Return at least the user data if repo data fetching fails
    else:
        return None

def get_last_processed_record():
    """Fetch the last processed record ID from the count file or return None if the file does not exist."""
    try:
        with open(COUNT_FILE, 'r') as file:
            last_processed = int(file.read().strip())
            return last_processed
    except FileNotFoundError:
        return None

def update_last_processed_record(record_id):
    """Update the last processed record ID in the count file."""
    os.makedirs(os.path.dirname(COUNT_FILE), exist_ok=True)
    with open(COUNT_FILE, 'w') as file:
        file.write(str(record_id))

def fetch_data_for_github_usernames_in_batches(table_name, batch_size=10, sleep_time=5):
    """Fetch GitHub data for usernames retrieved from a specific table in batches of specified size."""
    print(f"Fetching GitHub URLs from table: {table_name}")
    
    last_processed = get_last_processed_record()  # Fetch last processed ID from the count file
    github_records = fetch_github_urls_from_table(table_name, last_processed)
    
    if not github_records or len(github_records) == 0:
        print("No valid records found in the table.")
        return []

    users_data = []

    # Function to split records into batches
    def chunk_data(data, chunk_size):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    # Only process the first batch
    for batch_index, batch in enumerate(chunk_data(github_records, batch_size)):
        print(f"Processing batch {batch_index + 1} of {len(batch)} records...")

        for record in batch:
            github_url = record.get('githubUrl')
            record_id = record.get('id')

            if github_url:
                username = extract_github_username(github_url)
                if username:
                    try:
                        user_data = get_github_data(username)
                        if user_data:
                            users_data.append(user_data)
                            print(f"Fetched and processed data for username: {username}")
                        else:
                            print(f"Data fetch failed for username: {username}")
                    except Exception as e:
                        print(f"Error processing GitHub data for {username}: {e}")
                else:
                    print(f"Failed to extract username from URL: {github_url}")

            # After processing the record, update the last processed record ID
            update_last_processed_record(record_id)  # Save the last processed record ID

        print(f"Finished processing batch {batch_index + 1}. Waiting for {sleep_time} seconds before next batch...")
        time.sleep(sleep_time)  # Wait for the specified time before processing the next batch
        
        # Exit after processing one batch
        break

    return users_data

def insert_data_in_batches(data, batch_size=10):
    """Insert fetched GitHub data into the database in batches of a specified size."""
    total_records = len(data)
    records_inserted = 0
    failed_records = 0

    try:
        if cnx.is_connected():
            cursor = cnx.cursor()

            # Create table if it doesn't exist
            check_table_query = """
            CREATE TABLE IF NOT EXISTS github_fetch (
                username VARCHAR(255) PRIMARY KEY,
                followers INT,
                following INT,
                public_repos INT,
                public_gists INT,
                hireable BOOLEAN,
                bio TEXT,
                location VARCHAR(255),
                company VARCHAR(255),
                email VARCHAR(255),
                created_at DATETIME,
                updated_at DATETIME,
                total_stars INT,
                total_forks INT,
                total_contributions INT,
                total_repos INT,
                languages TEXT,
                commit_count INT,
                pull_request_count INT,
                issue_count INT
            )
            """
            cursor.execute(check_table_query)

            # Function to break data into chunks
            def chunk_data(data, chunk_size):
                for i in range(0, len(data), chunk_size):
                    yield data[i:i + chunk_size]

            # Insert data batch-wise
            for batch in chunk_data(data, batch_size):
                for user_data in batch:
                    try:
                        insert_query = """
                        INSERT INTO github_fetch (username, followers, following, public_repos, public_gists, hireable, bio, location, company, email, created_at, updated_at, total_stars, total_forks, total_contributions, total_repos, languages, commit_count, pull_request_count, issue_count)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        username=VALUES(username),
                        followers=VALUES(followers),
                        following=VALUES(following),
                        public_repos=VALUES(public_repos),
                        public_gists=VALUES(public_gists),
                        hireable=VALUES(hireable),
                        bio=VALUES(bio),
                        location=VALUES(location),
                        company=VALUES(company),
                        email=VALUES(email),
                        created_at=VALUES(created_at),
                        updated_at=VALUES(updated_at),
                        total_stars=VALUES(total_stars),
                        total_forks=VALUES(total_forks),
                        total_contributions=VALUES(total_contributions),
                        total_repos=VALUES(total_repos),
                        languages=VALUES(languages),
                        commit_count=VALUES(commit_count),
                        pull_request_count=VALUES(pull_request_count),
                        issue_count=VALUES(issue_count)
                        """

                        values = (
                            user_data['username'],
                            user_data['followers'],
                            user_data['following'],
                            user_data['public_repos'],
                            user_data['public_gists'],
                            user_data.get('hireable', 0),
                            user_data.get('bio', ''),  # Default to empty string if not present
                            user_data.get('location', ''),
                            user_data.get('company', ''),
                            user_data.get('email', ''),
                            user_data['created_at'],
                            user_data['updated_at'],
                            user_data.get('total_stars', 0),  # Default to 0 if not present
                            user_data.get('total_forks', 0),
                            user_data.get('total_contributions', 0),
                            user_data.get('total_repos', 0),
                            user_data.get('languages', ''),
                            user_data.get('commit_count', 0),
                            user_data.get('pull_request_count', 0),
                            user_data.get('issue_count', 0)
                        )

                        # Log the data we are trying to insert for tracking
                        print(f"Attempting to insert: {values} (Columns: {len(values)})")

                        cursor.execute(insert_query, values)
                        records_inserted += 1

                    except Exception as e:
                        failed_records += 1
                        print(f"Error inserting record for username: {user_data['username']}. Error: {e}")

                cnx.commit()
                print(f"Batch processed successfully. {records_inserted}/{total_records} inserted. {failed_records} failed.")

    except mysql.connector.Error as e:
        print(f"Error while inserting data into MySQL: {e}")

    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()
            print(f"Connection closed. {records_inserted}/{total_records} records inserted successfully. {failed_records} failed.")

# Example usage
if __name__ == "__main__":
    try:
        github_data_batch = fetch_data_for_github_usernames_in_batches('stackoverflow_fetch', batch_size=5)
        if github_data_batch:
            insert_data_in_batches(github_data_batch, batch_size=5)
    except Exception as e:
        print(f"An error occurred during processing: {e}")
