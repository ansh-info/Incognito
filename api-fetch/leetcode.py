import pandas as pd
import requests
from sqlalchemy import create_engine
import time
import random

# Replace with your own database credentials
DATABASE_TYPE = 'mysql'
DBAPI = 'mysqlconnector'
HOST = 'localhost'  # Connect to the Docker container on localhost
USER = 'root'
PASSWORD = '9084Mysql#'
DATABASE = 'data_collection'
PORT = 3306

# LeetCode GraphQL endpoint
LEETCODE_GRAPHQL_ENDPOINT = 'https://leetcode.com/graphql'

# GraphQL query to fetch user data
GRAPHQL_QUERY = '''
query getUserProfile($username: String!) {
  allQuestionsCount {
    difficulty
    count
  }
  matchedUser(username: $username) {
    username
    submitStats {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
    contestBadge {
      name
    }
    profile {
      ranking
      reputation
      userAvatar
      realName
      aboutMe
    }
  }
}
'''

# Create the database engine
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

def fetch_leetcode_user_data(username):
    """
    Fetch LeetCode user data using GraphQL.
    """
    response = requests.post(
        LEETCODE_GRAPHQL_ENDPOINT,
        json={'query': GRAPHQL_QUERY, 'variables': {'username': username}}
    )

    if response.status_code == 200:
        data = response.json().get('data', {})
        user_data = data.get('matchedUser', {})
        all_questions_count = data.get('allQuestionsCount', [])
        
        if user_data:
            return {
                'username': username,
                'ranking': user_data.get('profile', {}).get('ranking'),
                'reputation': user_data.get('profile', {}).get('reputation'),
                'real_name': user_data.get('profile', {}).get('realName'),
                'about_me': user_data.get('profile', {}).get('aboutMe'),
                'contest_badge': user_data.get('contestBadge', {}).get('name') if user_data.get('contestBadge') else None,
                'total_questions': sum(item['count'] for item in all_questions_count),
                'total_accepted_submissions': sum(item['count'] for item in user_data.get('submitStats', {}).get('acSubmissionNum', [])),
                'total_submissions': sum(item['submissions'] for item in user_data.get('submitStats', {}).get('acSubmissionNum', []))
            }
        else:
            print(f"No matched user found for {username}")
            return None
    else:
        print(f"Failed to fetch data for {username}: {response.status_code}, {response.json()}")
        return None

def get_top_leetcode_users():
    """
    Mock fetching top LeetCode users. Replace this with actual logic to fetch top users.
    """
    # This is a mocked list of top usernames
    return [f"user{i}" for i in range(1, 101)]  # Mocking top 50 users

def get_data_for_top_leetcode_users():
    """
    Fetch data for the top LeetCode users.
    """
    top_users = get_top_leetcode_users()
    users_data = []
    
    for username in top_users:
        user_data = fetch_leetcode_user_data(username)
        if user_data:
            users_data.append(user_data)
            time.sleep(random.uniform(1, 3))  # Random sleep to avoid hitting rate limits
    
    return users_data

# Fetch data for top users
top_users_data = get_data_for_top_leetcode_users()

# Convert the data to a DataFrame
df = pd.DataFrame(top_users_data)

# Ensure DataFrame is not empty
if not df.empty:
    # Insert data into the database
    df.to_sql('leetcode_users', con=engine, if_exists='replace', index=False)
    print("Data inserted into the database successfully")
else:
    print("No data to insert into the database.")