import pandas as pd  # For data manipulation and analysis
import numpy as np  # For numerical operations
import xgboost as xgb  # For the XGBoost algorithm
from sklearn.model_selection import train_test_split, GridSearchCV  # For splitting data and hyperparameter tuning
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix  # For model evaluation
import seaborn as sns  # For data visualization
import matplotlib.pyplot as plt  # For plotting graphs

from __init__ import path
path()
from connection.db_connection import get_sqlalchemy_engine

# Get SQLAlchemy engine and database name
engine, DB_NAME = get_sqlalchemy_engine()

# Fetch data from 'github' table
query_github = "SELECT * FROM github_fetch"
github_data = pd.read_sql(query_github, engine)

# Fetch data from 'stackoverflow' table
query_stackoverflow = "SELECT * FROM stackoverflow_fetch"
stackoverflow_data = pd.read_sql(query_stackoverflow, engine)

# Extracting the username from the githubUrl in Stack Overflow data
stackoverflow_data['username'] = stackoverflow_data['githubUrl'].apply(
    lambda url: url.split('/')[-1] if isinstance(url, str) else None
)

# Perform the join on the 'username' column
merged_data = pd.merge(stackoverflow_data, github_data, on='username', how='inner')

# Display the first few rows of the merged dataset
print(merged_data.head())

# Select the relevant features
selected_features = ['reputation', 'answers', 'questions', 'gold_badge_score', 
                     'silver_badge_score', 'bronze_badge_score', 'total_stars', 
                     'total_forks', 'total_contributions', 'commit_count', 
                     'pull_request_count', 'issue_count']

# Check for missing values
missing_values = merged_data[selected_features].isnull().sum()
print("Missing values in selected features:\n", missing_values)

# Check the number of rows and columns in the dataframe
rows, columns = merged_data.shape
print(f"The merged dataset has {rows} rows and {columns} columns.")

from sklearn.preprocessing import StandardScaler

# Initialize the StandardScaler
scaler = StandardScaler()

# Scale the selected features
scaled_features = scaler.fit_transform(merged_data[selected_features])

# Convert the scaled features back into a DataFrame for easier analysis
scaled_df = pd.DataFrame(scaled_features, columns=selected_features)

# Display the first few rows of the scaled data
print(scaled_df.head())

from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import numpy as np

# Calculate the distance to the k-th nearest neighbor
k = 5  # You can use the same value as min_samples or adjust as needed
nbrs = NearestNeighbors(n_neighbors=k).fit(scaled_df)
distances, indices = nbrs.kneighbors(scaled_df)

# Sort the distances to plot
distances = np.sort(distances[:, k-1], axis=0)

# Plot the k-distance graph
plt.figure(figsize=(8, 5))
plt.plot(distances)
plt.title('K-Distance Graph')
plt.xlabel('Points sorted by distance')
plt.ylabel('Distance to {}-th Nearest Neighbor'.format(k))
plt.grid()
plt.show()

# Based on the K-Distance Graph, set the eps value
eps_value = 5  # Adjust based on the graph

# Initialize DBSCAN with the chosen parameters
dbscan = DBSCAN(eps=eps_value, min_samples=5)  # min_samples can also be adjusted
dbscan.fit(scaled_df)

# Assign cluster labels to each user (outliers will be labeled as -1)
merged_data['dbscan_cluster'] = dbscan.labels_

# Display the number of users in each cluster (-1 means outliers)
print(merged_data['dbscan_cluster'].value_counts())

# Display the first few rows with the cluster labels
print(merged_data[['username', 'dbscan_cluster']].head())

# Check the number of users in each cluster
cluster_counts = merged_data['dbscan_cluster'].value_counts()
print(cluster_counts)

# Display the first few rows with the cluster labels
print(merged_data[['username', 'dbscan_cluster']].head(20))

# First, select only the numeric columns
numeric_columns = merged_data.select_dtypes(include=['float64', 'int64']).columns

# Group by the 'dbscan_cluster' and calculate the mean for the numeric columns
cluster_summary = merged_data.groupby('dbscan_cluster')[numeric_columns].mean()

# Display the cluster summary
print(cluster_summary)

# Label suitable candidates based on cluster analysis
merged_data['suitable_candidate'] = merged_data['dbscan_cluster'].apply(
    lambda x: 'Highly Suitable' if x == 0 else 'Not Suitable' 
)

# Display the result
print(merged_data[['username', 'dbscan_cluster', 'suitable_candidate']].head(20))  # Show more rows if needed

import matplotlib.pyplot as plt
import seaborn as sns

# Visualize the clusters using two key features, such as 'reputation' and 'total_stars'
plt.figure(figsize=(10, 6))
sns.scatterplot(x=merged_data['reputation'], 
                 y=merged_data['total_stars'], 
                 hue=merged_data['dbscan_cluster'], 
                 palette='Set2', 
                 style=merged_data['suitable_candidate'],
                 markers={'Highly Suitable': 'o', 'Not Suitable': 'X'})

plt.title('DBSCAN Clusters Based on Reputation and Total Stars')
plt.xlabel('Reputation')
plt.ylabel('Total Stars')
plt.legend(title='Clusters')
plt.grid()
plt.show()

# Count the number of candidates in each category
candidate_counts = merged_data['suitable_candidate'].value_counts()

# Display the counts
print(candidate_counts)

# Create a numeric target variable based on suitable candidates
merged_data['suitable_candidate_numeric'] = merged_data['suitable_candidate'].apply(
    lambda x: 1 if x == 'Highly Suitable' else 0
)

# Define features and target variable
selected_features = ['reputation', 'answers', 'questions', 'gold_badge_score', 
                     'silver_badge_score', 'bronze_badge_score', 'total_stars', 
                     'total_forks', 'total_contributions', 'commit_count', 
                     'pull_request_count', 'issue_count']

X = merged_data[selected_features]
y = merged_data['suitable_candidate_numeric']  # Target variable

# Split the data into training and test sets
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit a model (for example, XGBoost)
from xgboost import XGBClassifier
model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# Make predictions and evaluate the model
y_pred = model.predict(X_test)

from sklearn.metrics import accuracy_score, classification_report
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Define the selected features
selected_features = ['reputation', 'answers', 'questions', 'gold_badge_score', 
                     'silver_badge_score', 'bronze_badge_score', 'total_stars', 
                     'total_forks', 'total_contributions', 'commit_count', 
                     'pull_request_count', 'issue_count']

# Select only highly suitable candidates
highly_suitable_candidates = merged_data[merged_data['suitable_candidate'] == 'Highly Suitable']

# Calculate a composite score for each candidate (average of the selected features)
highly_suitable_candidates['composite_score'] = highly_suitable_candidates[selected_features].mean(axis=1)

# Display the candidates with their scores
print(highly_suitable_candidates[['username', 'composite_score'] + selected_features].head(20))

# Determine the threshold for the top x% of candidates based on the composite score
score_threshold = highly_suitable_candidates['composite_score'].quantile(0.90)  # 90th percentile

# Filter candidates who meet or exceed the composite score threshold
top_candidates = highly_suitable_candidates[highly_suitable_candidates['composite_score'] >= score_threshold]

# Display the selected top candidates
print(top_candidates[['username', 'composite_score'] + selected_features])

from sklearn.cluster import DBSCAN

# Define your eps and min_samples
eps_value = 5  # Example value, adjust as necessary
min_samples_value = 5  # Example value, adjust as necessary

# Initialize DBSCAN
dbscan = DBSCAN(eps=eps_value, min_samples=min_samples_value)

# Fit DBSCAN model on the scaled features
dbscan.fit(scaled_df)

# Assign cluster labels to each user (outliers will be labeled as -1)
merged_data['dbscan_cluster'] = dbscan.labels_

# Check the number of users in each cluster
cluster_counts = merged_data['dbscan_cluster'].value_counts()
print(cluster_counts)

import pandas as pd

# Assuming 'merged_data' is your DataFrame after DBSCAN

# Create a numeric target variable based on dbscan_cluster
merged_data['suitable_candidate_numeric'] = merged_data['dbscan_cluster'].apply(
    lambda x: 1 if x == 0 else 0  # Cluster 0 is considered suitable
)

# Define the features to use for the model
selected_features = ['reputation', 'answers', 'questions', 'gold_badge_score', 
                     'silver_badge_score', 'bronze_badge_score', 'total_stars', 
                     'total_forks', 'total_contributions', 'commit_count', 
                     'pull_request_count', 'issue_count']

# Create feature matrix (X) and target vector (y)
X = merged_data[selected_features]  # Features
y = merged_data['suitable_candidate_numeric']  # Target variable

# Display the first few rows of X and y to ensure they are correct
print(X.head())
print(y.head())

from sklearn.model_selection import train_test_split

# Assuming merged_data is your DataFrame
X = merged_data[selected_features]  # Replace selected_features with your actual features
y = merged_data['suitable_candidate_numeric']  # Your target variable

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

from imblearn.over_sampling import SMOTE

# Initialize SMOTE with a lower n_neighbors value
smote = SMOTE(random_state=42, k_neighbors=3)  # Set to 3 or lower than your minority class size

# Fit and resample the training data
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# You can also calculate class weights, but since we're using SMOTE, we may skip that
# class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)

from xgboost import XGBClassifier

# Create the model with class weights
model = XGBClassifier(
    use_label_encoder=False,
    eval_metric='logloss',
    max_depth=3,
    n_estimators=100,
    learning_rate=0.1,
    scale_pos_weight=len(y_train[y_train == 0]) / len(y_train[y_train == 1])  # Adjust class weights
)

# Fit the model
model.fit(X_train, y_train)

model.fit(X_resampled, y_resampled)


# Step 1: Make Predictions
y_pred = model.predict(X_test)

# Step 2: Convert predictions to DataFrame
predicted_df = pd.DataFrame(y_pred, columns=['suitable_candidate_numeric'])
results_df = pd.concat([merged_data[['username']], predicted_df], axis=1)

# Step 3: Map Numeric Predictions to Categorical Labels
results_df['suitable_candidate'] = results_df['suitable_candidate_numeric'].apply(
    lambda x: 'Highly Suitable' if x == 1 else 'Not Suitable'
)

# Step 4: Count Suitable Candidates
suitable_counts = results_df['suitable_candidate'].value_counts()
print(suitable_counts)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
print(classification_report(y_test, y_pred))

import matplotlib.pyplot as plt
from xgboost import plot_importance

# Plot feature importance
plt.figure(figsize=(10, 6))
plot_importance(model, importance_type='weight', max_num_features=10)
plt.title('Feature Importance')
plt.show()

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Assuming you have trained your model and have X_test available
final_y_pred = model.predict(X_test)  # Replace 'model' with your actual model variable

# Generate the confusion matrix
cm = confusion_matrix(y_test, final_y_pred)

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", 
            xticklabels=["Not Suitable", "Highly Suitable"], 
            yticklabels=["Not Suitable", "Highly Suitable"])
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion Matrix')
plt.show()

from sklearn.metrics import classification_report

# Generate and display the classification report
print(classification_report(y_test, final_y_pred))
