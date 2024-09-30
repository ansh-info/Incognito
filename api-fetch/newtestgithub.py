import pandas as pd
import requests
from sqlalchemy import create_engine
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your own database credentials
DATABASE_TYPE = 'mysql'
DBAPI = 'mysqlconnector'
HOST = 'localhost'
USER = 'root'
PASSWORD = '9084Mysql#'
DATABASE = 'data_collection'
PORT = 3306

# Create the database engine
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# GitHub Personal Access Token
GITHUB_TOKEN = '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'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

# Set up retry strategy
retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"],
    backoff_factor=2
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

def get_large_set_github_users(pages=5, per_page=20):
    users = []
    for page in range(1, pages + 1):
        search_url = f"https://api.github.com/search/users?q=followers:>100&sort=followers&order=desc&per_page={per_page}&page={page}"
        try:
            response = http.get(search_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            users_data = response.json()['items']
            users.extend([user['login'] for user in users_data])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch users on page {page}: {e}")
            break
    
    return users

def handle_rate_limit(response):
    if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
        reset_time = int(response.headers['X-RateLimit-Reset'])
        sleep_time = max(1, reset_time - int(time.time()))
        logger.warning(f"Rate limit exceeded. Retrying after {sleep_time} seconds...")
        time.sleep(sleep_time)
        return True
    return False

def get_github_user_data(username):
    user_url = f"https://api.github.com/users/{username}"
    try:
        response = http.get(user_url, headers=HEADERS, timeout=10)
        if handle_rate_limit(response):
            response = http.get(user_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        user_data = response.json()
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
            'created_at': user_data['created_at'],
            'updated_at': user_data['updated_at']
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch user data for {username}: {e}")
        return None

def get_github_repos_data(username):
    repos_url = f"https://api.github.com/users/{username}/repos"
    try:
        response = http.get(repos_url, headers=HEADERS, timeout=10)
        if handle_rate_limit(response):
            response = http.get(repos_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        repos_data = response.json()
        total_stars = sum(repo['stargazers_count'] for repo in repos_data)
        total_forks = sum(repo['forks_count'] for repo in repos_data)
        total_contributions = sum(repo['size'] for repo in repos_data)
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
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch repository data for {username}: {e}")
        return None

def get_commit_count(username, repo_name):
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    try:
        response = http.get(commits_url, headers=HEADERS, timeout=10)
        if response.status_code == 409:
            logger.warning(f"Conflict error for commits in {username}/{repo_name}")
            return 0
        if handle_rate_limit(response):
            response = http.get(commits_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return len(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch commits for {username}/{repo_name}: {e}")
        return 0

def get_pull_request_count(username, repo_name):
    pulls_url = f"https://api.github.com/repos/{username}/{repo_name}/pulls?state=all"
    try:
        response = http.get(pulls_url, headers=HEADERS, timeout=10)
        if response.status_code == 409:
            logger.warning(f"Conflict error for pull requests in {username}/{repo_name}")
            return 0
        if handle_rate_limit(response):
            response = http.get(pulls_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return len(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch pull requests for {username}/{repo_name}: {e}")
        return 0

def get_issue_count(username, repo_name):
    issues_url = f"https://api.github.com/repos/{username}/{repo_name}/issues?state=all"
    try:
        response = http.get(issues_url, headers=HEADERS, timeout=10)
        if response.status_code == 409:
            logger.warning(f"Conflict error for issues in {username}/{repo_name}")
            return 0
        if handle_rate_limit(response):
            response = http.get(issues_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return len(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch issues for {username}/{repo_name}: {e}")
        return 0

def get_github_data(username):
    user_data = get_github_user_data(username)
    repos_data = get_github_repos_data(username)
    
    if user_data and repos_data:
        return {
            'username': username,
            **user_data,
            **repos_data
        }
    else:
        logger.warning(f"Failed to fetch complete data for {username}")
        return None

def get_data_for_random_users(sample_size=100):
    large_user_set = get_large_set_github_users(pages=5, per_page=20)
    if len(large_user_set) < sample_size:
        logger.warning(f"Only {len(large_user_set)} users found. Using all available users.")
        sample_size = len(large_user_set)
    
    random_users = random.sample(large_user_set, sample_size)
    
    users_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_username = {executor.submit(get_github_data, username): username for username in random_users}
        for future in as_completed(future_to_username):
            username = future_to_username[future]
            try:
                user_data = future.result()
                if user_data:
                    users_data.append(user_data)
            except Exception as e:
                logger.error(f"Failed to fetch data for {username}: {e}")
    
    return users_data

# Fetch data for random users
random_users_data = get_data_for_random_users()

# Convert the data to a DataFrame
if random_users_data:
    df = pd.DataFrame(random_users_data)
    try:
        df.to_sql('github_usersnew', con=engine, if_exists='replace', index=False)
        logger.info("Data inserted into the database successfully")
    except Exception as e:
        logger.error(f"Failed to insert data into the database: {e}")
else:
    logger.warning("No data to insert into the database")
