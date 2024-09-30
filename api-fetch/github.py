import pandas as pd
import requests
from sqlalchemy import create_engine
import random

# Replace with your own database credentials
DATABASE_TYPE = 'mysql'
DBAPI = 'mysqlconnector'
HOST = 'localhost'  # Connect to the Docker container on localhost
USER = 'root'
PASSWORD = '9084Mysql#'
DATABASE = 'data_collection'
PORT = 3306

# Create the database engine
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# GitHub Personal Access Token (replace with your actual token)
GITHUB_TOKEN = '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'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

def get_large_set_github_users(pages=5, per_page=20):
    """
    Fetch a large set of GitHub users by iterating over multiple pages.
    """
    users = []
    for page in range(1, pages + 1):
        search_url = f"https://api.github.com/search/users?q=followers:>100&sort=followers&order=desc&per_page={per_page}&page={page}"
        response = requests.get(search_url, headers=HEADERS)
        
        if response.status_code == 200:
            users_data = response.json()['items']
            users.extend([user['login'] for user in users_data])
        else:
            print(f"Failed to fetch users on page {page}: {response.status_code}")
            break
    
    return users

def get_github_user_data(username):
    """
    Fetch detailed GitHub user data.
    """
    user_url = f"https://api.github.com/users/{username}"
    response = requests.get(user_url, headers=HEADERS)
    
    if response.status_code == 200:
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
    else:
        print(f"Failed to fetch user data for {username}: {response.status_code}")
        return None

def get_github_repos_data(username):
    """
    Fetch GitHub repository data and calculate additional metrics.
    """
    repos_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(repos_url, headers=HEADERS)
    
    if response.status_code == 200:
        repos_data = response.json()
        total_stars = sum(repo['stargazers_count'] for repo in repos_data)
        total_forks = sum(repo['forks_count'] for repo in repos_data)
        total_contributions = sum(repo['size'] for repo in repos_data)  # Size as a proxy for contributions
        total_repos = len(repos_data)
        languages = list(set(repo['language'] for repo in repos_data if repo['language']))

        # Fetch commits, pull requests, and issues
        commit_count = sum(get_commit_count(username, repo['name']) for repo in repos_data)
        pull_request_count = sum(get_pull_request_count(username, repo['name']) for repo in repos_data)
        issue_count = sum(get_issue_count(username, repo['name']) for repo in repos_data)

        return {
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_contributions': total_contributions,
            'total_repos': total_repos,
            'languages': ', '.join(filter(None, languages)),  # Join languages as a comma-separated string
            'commit_count': commit_count,
            'pull_request_count': pull_request_count,
            'issue_count': issue_count
        }
    else:
        print(f"Failed to fetch repository data for {username}: {response.status_code}")
        return None

def get_commit_count(username, repo_name):
    """
    Fetch the number of commits made by the user in a repository.
    """
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    response = requests.get(commits_url, headers=HEADERS)
    if response.status_code == 200:
        return len(response.json())
    return 0

def get_pull_request_count(username, repo_name):
    """
    Fetch the number of pull requests made by the user in a repository.
    """
    pulls_url = f"https://api.github.com/repos/{username}/{repo_name}/pulls?state=all"
    response = requests.get(pulls_url, headers=HEADERS)
    if response.status_code == 200:
        return len(response.json())
    return 0

def get_issue_count(username, repo_name):
    """
    Fetch the number of issues opened by the user in a repository.
    """
    issues_url = f"https://api.github.com/repos/{username}/{repo_name}/issues?state=all"
    response = requests.get(issues_url, headers=HEADERS)
    if response.status_code == 200:
        return len(response.json())
    return 0

def get_github_data(username):
    """
    Combine GitHub user data and repository data into a single dictionary.
    """
    user_data = get_github_user_data(username)
    repos_data = get_github_repos_data(username)
    
    if user_data and repos_data:
        return {
            'username': username,
            **user_data,
            **repos_data
        }
    else:
        print(f"Failed to fetch complete data for {username}")
        return None

def get_data_for_random_users():
    """
    Fetch data for 100 randomly selected GitHub users from a large set.
    """
    large_user_set = get_large_set_github_users(pages=5, per_page=20)
    random_users = random.sample(large_user_set, 100)
    
    users_data = []
    for username in random_users:
        user_data = get_github_data(username)
        if user_data:
            users_data.append(user_data)
    
    return users_data

# Fetch data for random users
random_users_data = get_data_for_random_users()

# Convert the data to a DataFrame
df = pd.DataFrame(random_users_data)

# Insert data into the database
df.to_sql('github_usersmain', con=engine, if_exists='replace', index=False)
print("Data inserted into the database successfully")
