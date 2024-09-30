# import pandas as pd
# import requests
# from sqlalchemy import create_engine
# import time
# import random

# # Replace with your own database credentials
# DATABASE_TYPE = 'mysql'
# DBAPI = 'mysqlconnector'
# HOST = 'localhost'  # Connect to the Docker container on localhost
# USER = 'root'
# PASSWORD = '9084Mysql#'
# DATABASE = 'data_collection'
# PORT = 3306

# # Replace with your Stack Exchange API key
# API_KEY = 'rl_dYf11SKPnAWT2EeqFVCZfLKFG'

# # Create the database engine
# engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# def get_top_stackexchange_users(site='stackoverflow', pagesize=100):
#     """
#     Fetch the top Stack Exchange users based on reputation.
#     """
#     url = f"https://api.stackexchange.com/2.3/users?order=desc&sort=reputation&site={site}&pagesize={pagesize}&key={API_KEY}"
#     response = requests.get(url)
    
#     if response.status_code == 200:
#         users_data = response.json()['items']
#         return users_data
#     else:
#         print(f"Failed to fetch top users: {response.status_code}, message: {response.json().get('error_message', 'Unknown error')}")
#         return []

# def get_stackexchange_user_data(user_id, site='stackoverflow'):
#     """
#     Fetch Stack Exchange user data including reputation, badges, and counts.
#     """
#     user_url = f"https://api.stackexchange.com/2.3/users/{user_id}?site={site}&key={API_KEY}"
#     response = requests.get(user_url)
    
#     if response.status_code == 200:
#         user_data = response.json()['items'][0]
#         return {
#             'user_id': user_id,
#             'display_name': user_data['display_name'],
#             'reputation': user_data['reputation'],
#             'badge_counts': user_data.get('badge_counts', {})
#         }
#     else:
#         print(f"Failed to fetch user data for {user_id}: {response.status_code}")
#         return None

# def get_stackexchange_user_activity(user_id, site='stackoverflow'):
#     """
#     Fetch Stack Exchange user activity including answers and questions counts.
#     """
#     answers_url = f"https://api.stackexchange.com/2.3/users/{user_id}/answers?site={site}&filter=total&key={API_KEY}"
#     questions_url = f"https://api.stackexchange.com/2.3/users/{user_id}/questions?site={site}&filter=total&key={API_KEY}"

#     answer_count = 0
#     question_count = 0
#     up_vote_count = 0
#     down_vote_count = 0

#     answers_response = requests.get(answers_url)
#     if answers_response.status_code == 200:
#         answer_data = answers_response.json()
#         if 'total' in answer_data:
#             answer_count = answer_data['total']
#         if 'items' in answer_data:
#             up_vote_count = sum(item.get('up_vote_count', 0) for item in answer_data['items'])
#             down_vote_count = sum(item.get('down_vote_count', 0) for item in answer_data['items'])
    
#     questions_response = requests.get(questions_url)
#     if questions_response.status_code == 200:
#         question_data = questions_response.json()
#         if 'total' in question_data:
#             question_count = question_data['total']

#     return {
#         'answer_count': answer_count,
#         'question_count': question_count,
#         'up_vote_count': up_vote_count,
#         'down_vote_count': down_vote_count
#     }

# def get_data_for_top_stackexchange_users():
#     """
#     Fetch data for the top Stack Exchange users.
#     """
#     top_users = get_top_stackexchange_users()
#     users_data = []
    
#     for user in top_users:
#         basic_data = get_stackexchange_user_data(user['user_id'])
#         if basic_data:
#             activity_data = get_stackexchange_user_activity(user['user_id'])
#             combined_data = {**basic_data, **activity_data}
#             users_data.append(combined_data)
#             time.sleep(random.uniform(1, 3))  # Random sleep to avoid hitting rate limits
    
#     return users_data

# # Fetch data for top users
# top_users_data = get_data_for_top_stackexchange_users()

# # Convert the data to a DataFrame
# df = pd.DataFrame(top_users_data)

# # Normalize badge_counts into separate columns
# if 'badge_counts' in df.columns:
#     badge_counts_df = df['badge_counts'].apply(pd.Series)
#     df = df.drop('badge_counts', axis=1).join(badge_counts_df)

# # Insert data into the database
# df.to_sql('stackexchange_users', con=engine, if_exists='replace', index=False)
# print("Data inserted into the database successfully")


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

# Replace with your Stack Exchange API key
API_KEY = 'rl_dYf11SKPnAWT2EeqFVCZfLKFG'

# Create the database engine
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

def get_random_stackexchange_users(site='stackoverflow', pagesize=100):
    """
    Fetch random Stack Exchange users.
    """
    page = random.randint(1, 100)  # Choose a random page number
    url = f"https://api.stackexchange.com/2.3/users?site={site}&page={page}&pagesize={pagesize}&key={API_KEY}"
    
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            users_data = response.json()['items']
            return users_data
        elif response.status_code == 429:
            print(f"Rate limit hit. Retrying after delay: {response.headers.get('Retry-After', 1)} seconds.")
            time.sleep(int(response.headers.get('Retry-After', 1)))
        else:
            print(f"Failed to fetch users: {response.status_code}, message: {response.json().get('error_message', 'Unknown error')}")
            return []

def get_stackexchange_user_data(user_id, site='stackoverflow'):
    """
    Fetch Stack Exchange user data including reputation, badges, and counts.
    """
    user_url = f"https://api.stackexchange.com/2.3/users/{user_id}?site={site}&key={API_KEY}"
    
    while True:
        response = requests.get(user_url)
        if response.status_code == 200:
            user_data = response.json()['items'][0]
            return {
                'user_id': user_id,
                'display_name': user_data['display_name'],
                'reputation': user_data['reputation'],
                'badge_counts': user_data.get('badge_counts', {})
            }
        elif response.status_code == 429:
            print(f"Rate limit hit. Retrying after delay: {response.headers.get('Retry-After', 1)} seconds.")
            time.sleep(int(response.headers.get('Retry-After', 1)))
        else:
            print(f"Failed to fetch user data for {user_id}: {response.status_code}")
            return None

def get_stackexchange_user_activity(user_id, site='stackoverflow'):
    """
    Fetch Stack Exchange user activity including answers and questions counts.
    """
    answers_url = f"https://api.stackexchange.com/2.3/users/{user_id}/answers?site={site}&filter=total&key={API_KEY}"
    questions_url = f"https://api.stackexchange.com/2.3/users/{user_id}/questions?site={site}&filter=total&key={API_KEY}"

    answer_count = 0
    question_count = 0
    up_vote_count = 0
    down_vote_count = 0

    while True:
        answers_response = requests.get(answers_url)
        if answers_response.status_code == 200:
            answer_data = answers_response.json()
            if 'total' in answer_data:
                answer_count = answer_data['total']
            if 'items' in answer_data:
                up_vote_count = sum(item.get('up_vote_count', 0) for item in answer_data['items'])
                down_vote_count = sum(item.get('down_vote_count', 0) for item in answer_data['items'])
            break
        elif answers_response.status_code == 429:
            print(f"Rate limit hit. Retrying after delay: {answers_response.headers.get('Retry-After', 1)} seconds.")
            time.sleep(int(answers_response.headers.get('Retry-After', 1)))
        else:
            print(f"Failed to fetch answers data for {user_id}: {answers_response.status_code}")
            break

    while True:
        questions_response = requests.get(questions_url)
        if questions_response.status_code == 200:
            question_data = questions_response.json()
            if 'total' in question_data:
                question_count = question_data['total']
            break
        elif questions_response.status_code == 429:
            print(f"Rate limit hit. Retrying after delay: {questions_response.headers.get('Retry-After', 1)} seconds.")
            time.sleep(int(questions_response.headers.get('Retry-After', 1)))
        else:
            print(f"Failed to fetch questions data for {user_id}: {questions_response.status_code}")
            break

    return {
        'answer_count': answer_count,
        'question_count': question_count,
        'up_vote_count': up_vote_count,
        'down_vote_count': down_vote_count
    }

def get_data_for_random_stackexchange_users():
    """
    Fetch data for random Stack Exchange users.
    """
    random_users = get_random_stackexchange_users()
    users_data = []
    
    for user in random_users:
        basic_data = get_stackexchange_user_data(user['user_id'])
        if basic_data:
            activity_data = get_stackexchange_user_activity(user['user_id'])
            combined_data = {**basic_data, **activity_data}
            users_data.append(combined_data)
            time.sleep(random.uniform(1, 3))  # Random sleep to avoid hitting rate limits
    
    return users_data

# Fetch data for random users
random_users_data = get_data_for_random_stackexchange_users()

# Convert the data to a DataFrame
df = pd.DataFrame(random_users_data)

# Normalize badge_counts into separate columns
if 'badge_counts' in df.columns:
    badge_counts_df = df['badge_counts'].apply(pd.Series)
    df = df.drop('badge_counts', axis=1).join(badge_counts_df)

# Insert data into the database
df.to_sql('stackexchange_users_test', con=engine, if_exists='replace', index=False)
print("Data inserted into the database successfully")
