import os
import mysql.connector
import pandas as pd
import logging
import pickle
import random
import string
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# MySQL database connection details for user data
# db_config = {
#     'user': os.getenv('DB_USER'),
#     'password': os.getenv('DB_PASSWORD'),
#     'host': os.getenv('DB_HOST'),
#     'database': os.getenv('DB_NAME')
# }

db_config = {
    'user': 'root',
    'password': '9084Mysql#',
    'host': '0.0.0.0',
    'database': 'doodle'
}

def create_db_connection(config):
    """Create a database connection."""
    return mysql.connector.connect(**config)

def fetch_new_candidates(db_connection):
    """Fetch data from the master_candidates table."""
    query = """
    SELECT candidate_id, reputation, reached, answers, questions, gold_badge_score,
           silver_badge_score, bronze_badge_score, followers, public_repos,
           total_stars, total_forks, total_contributions, total_repos, commit_count,
           pull_request_count, issue_count, member_exp
    FROM master_candidates;
    """
    df = pd.read_sql(query, db_connection)
    logging.info("Fetched candidate data from master_candidates table.")
    return df

def scale_features(df, scaler):
    """Scale the features using the provided scaler and return both original and scaled DataFrames."""
    
    features = ['reputation', 'reached', 'answers', 'questions', 'gold_badge_score',
                'silver_badge_score', 'bronze_badge_score', 'followers', 
                'public_repos', 'total_stars', 'total_forks', 'total_contributions',
                'total_repos', 'commit_count', 'pull_request_count', 'issue_count',
                'member_exp']
    
    logging.info(f'Df Before Scaling:\n{df[features]}')
    scaled_features = scaler.transform(df[features])
    
    df_scaled = pd.DataFrame(scaled_features, columns=features)
    df_scaled['candidate_id'] = df['candidate_id']  # retain candidate_id for later
    logging.info("Scaled features for prediction.")
    
    return df, df_scaled  # Return both original and scaled DataFrames


def load_model_and_scaler(model_file='/Users/anshkumar/Developer/code/node/node20.16.0/test/selectionalgorithm/model/logistic_regression_model.pkl', scaler_file='/Users/anshkumar/Developer/code/node/node20.16.0/test/selectionalgorithm/model/scaler.pkl'):
    """Load the logistic regression model and scaler from pickle files."""
    with open(model_file, 'rb') as model_f:
        model = pickle.load(model_f)
    
    with open(scaler_file, 'rb') as scaler_f:
        scaler = pickle.load(scaler_f)
    
    logging.info("Logistic regression model and scaler loaded from pickle files.")
    return model, scaler

def generate_username():
    """Generate a random 8-character alphanumeric username."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def predict_candidates(df_scaled, model):
    """Make predictions using the loaded model."""
    features = ['reputation', 'reached', 'answers', 'questions', 'gold_badge_score',
                'silver_badge_score', 'bronze_badge_score', 'followers',
                'public_repos', 'total_stars', 'total_forks', 'total_contributions',
                'total_repos', 'commit_count', 'pull_request_count', 'issue_count',
                'member_exp']
    
    predictions = model.predict(df_scaled[features])
    df_scaled['prediction'] = predictions
    logging.info("Predictions generated for candidates.")
    print(df_scaled['prediction'])
    return df_scaled

def insert_predictions_to_db(db_connection, df_scaled):
    """Insert the predictions into the suitable_candidates table."""
    cursor = db_connection.cursor()

    insert_query = """
    INSERT INTO suitable_candidates (user_id, username, email, reputation, reached, answers, 
        questions, gold_badge_score, silver_badge_score, bronze_badge_score, followers, 
        public_repos, total_stars, total_forks, total_contributions, total_repos, 
        commit_count, pull_request_count, issue_count, member_exp, prediction)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for _, row in df_scaled.iterrows():
        username = generate_username()
        email = f"{username}@gmail.com"
        
        cursor.execute(insert_query, (
            int(row['candidate_id']), username, email, int(row['reputation']), 
            int(row['reached']), int(row['answers']), int(row['questions']),
            int(row['gold_badge_score']), int(row['silver_badge_score']), 
            int(row['bronze_badge_score']), int(row['followers']),
            int(row['public_repos']), int(row['total_stars']), int(row['total_forks']), 
            int(row['total_contributions']), int(row['total_repos']), 
            int(row['commit_count']), int(row['pull_request_count']), 
            int(row['issue_count']), float(row['member_exp']), int(row['prediction'])
        ))
    
    db_connection.commit()
    logging.info("Inserted predictions into the suitable_candidates table.")
    cursor.close()

def truncate_suitable_candidates_table(db_connection):
    """Truncate the suitable_candidates table to ensure it's empty."""
    cursor = db_connection.cursor()
    truncate_query = "TRUNCATE TABLE suitable_candidates;"
    
    cursor.execute(truncate_query)
    db_connection.commit()
    
    logging.info("Truncated suitable_candidates table to remove old data.")
    cursor.close()

def main():
    # Create database connection
    db_conn = create_db_connection(db_config)
    
    # Truncate the suitable_candidates table to ensure it's empty
    truncate_suitable_candidates_table(db_conn)
    
    # Fetch new candidates from master_candidate_table
    candidate_data = fetch_new_candidates(db_conn)

    logging.info(f'Fetched Candidate Data:\n{candidate_data}')
    
    # Load the pre-trained model and scaler
    model, scaler = load_model_and_scaler()
    
    # Scale the features using the loaded scaler
    original_candidate_data, scaled_candidate_data = scale_features(candidate_data, scaler)
    
    # Predict the candidates using the loaded model
    predicted_data = predict_candidates(scaled_candidate_data, model)
    
    # Keep original features and add prediction
    original_candidate_data['prediction'] = predicted_data['prediction']
    
    # Insert predictions into the database
    insert_predictions_to_db(db_conn, original_candidate_data)
    
    # Close the DB connection
    db_conn.close()


if __name__ == "__main__":
    main()
