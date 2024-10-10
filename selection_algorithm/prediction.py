import os
import pandas as pd
import logging
import pickle
import random
import string
from sklearn.preprocessing import StandardScaler
from __init__ import path
path()

from connection.db_connection import get_sqlalchemy_engine
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_new_candidates(engine):
    """Fetch data from the master_candidates table using SQLAlchemy."""
    query = """
    SELECT candidate_id, reputation, reached, answers, questions, gold_badge_score,
           silver_badge_score, bronze_badge_score, followers, public_repos,
           total_stars, total_forks, total_contributions, total_repos, commit_count,
           pull_request_count, issue_count, member_exp
    FROM master_candidates;
    """
    df = pd.read_sql(query, engine)
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


def load_model_and_scaler(model_file='models/logistic_regression_model.pkl', scaler_file='models/scaler.pkl'):
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

def insert_predictions_to_db(engine, df_scaled):
    """Insert the predictions into the suitable_candidates table using SQLAlchemy."""
    insert_query = text("""
    INSERT INTO suitable_candidates (user_id, username, email, reputation, reached, answers, 
        questions, gold_badge_score, silver_badge_score, bronze_badge_score, followers, 
        public_repos, total_stars, total_forks, total_contributions, total_repos, 
        commit_count, pull_request_count, issue_count, member_exp, prediction)
    VALUES (:user_id, :username, :email, :reputation, :reached, :answers, 
        :questions, :gold_badge_score, :silver_badge_score, :bronze_badge_score, 
        :followers, :public_repos, :total_stars, :total_forks, :total_contributions, 
        :total_repos, :commit_count, :pull_request_count, :issue_count, :member_exp, :prediction)
    """)

    with engine.begin() as conn:
        for _, row in df_scaled.iterrows():
            username = generate_username()
            email = f"{username}@gmail.com"
            
            conn.execute(insert_query, {
                'user_id': int(row['candidate_id']), 'username': username, 'email': email,
                'reputation': int(row['reputation']), 'reached': int(row['reached']),
                'answers': int(row['answers']), 'questions': int(row['questions']),
                'gold_badge_score': int(row['gold_badge_score']), 'silver_badge_score': int(row['silver_badge_score']),
                'bronze_badge_score': int(row['bronze_badge_score']), 'followers': int(row['followers']),
                'public_repos': int(row['public_repos']), 'total_stars': int(row['total_stars']),
                'total_forks': int(row['total_forks']), 'total_contributions': int(row['total_contributions']),
                'total_repos': int(row['total_repos']), 'commit_count': int(row['commit_count']),
                'pull_request_count': int(row['pull_request_count']), 'issue_count': int(row['issue_count']),
                'member_exp': float(row['member_exp']), 'prediction': int(row['prediction'])
            })
    
    logging.info("Inserted predictions into the suitable_candidates table.")

def truncate_suitable_candidates_table(engine):
    """Truncate the suitable_candidates table using SQLAlchemy."""
    truncate_query = text("TRUNCATE TABLE suitable_candidates;")
    
    with engine.begin() as conn:
        conn.execute(truncate_query)
    
    logging.info("Truncated suitable_candidates table to remove old data.")

def main():
    # Get the SQLAlchemy engine from the centralized handler
    engine, _ = get_sqlalchemy_engine()
    
    # Truncate the suitable_candidates table to ensure it's empty
    truncate_suitable_candidates_table(engine)
    
    # Fetch new candidates from the master_candidates table
    candidate_data = fetch_new_candidates(engine)

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
    insert_predictions_to_db(engine, original_candidate_data)


if __name__ == "__main__":
    main()
