import pandas as pd
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


# Display the first few rows of GitHub data
print(github_data.head())

# Display the first few rows of Stack Overflow data
print(stackoverflow_data.head())

# Extracting the username from the githubUrl in Stack Overflow data
stackoverflow_data['username'] = stackoverflow_data['githubUrl'].apply(lambda url: url.split('/')[-1] if isinstance(url, str) else None)

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
print(missing_values)

# Check the number of rows and columns in the dataframe
rows, columns = merged_data.shape
print(f"The dataframe has {rows} rows and {columns} columns.")

from sklearn.preprocessing import StandardScaler

# Initialize the StandardScaler
scaler = StandardScaler()

# Scale the selected features
scaled_features = scaler.fit_transform(merged_data[selected_features])

# Convert the scaled features back into a DataFrame for easier analysis
scaled_df = pd.DataFrame(scaled_features, columns=selected_features)

# Display the first few rows of the scaled data
print(scaled_df.head())

from sklearn.cluster import DBSCAN
import pandas as pd

# Initialize DBSCAN (tune eps and min_samples as needed)
dbscan = DBSCAN(eps=0.5, min_samples=5)  # You can experiment with these values

# Fit DBSCAN model on the scaled features
dbscan.fit(scaled_df)

# Assign cluster labels to each user (outliers will be labeled as -1)
merged_data['dbscan_cluster'] = dbscan.labels_

# Display the number of users in each cluster (-1 means outliers)
print(merged_data['dbscan_cluster'].value_counts())

# Display the first few rows with the cluster labels
print(merged_data[['username', 'dbscan_cluster']].head())

# First, select only the numeric columns
numeric_columns = merged_data.select_dtypes(include=['float64', 'int64']).columns

# Then, group by the 'dbscan_cluster' and calculate the mean for the numeric columns
cluster_summary = merged_data.groupby('dbscan_cluster')[numeric_columns].mean()

# Display the cluster summary
print(cluster_summary)

# You can also check the size of each cluster (how many users in each cluster)
print(merged_data['dbscan_cluster'].value_counts())

from sklearn.neighbors import NearestNeighbors
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

# Adjust the eps value based on your observation from the graph
eps_value = 3  # Set this to your identified value
dbscan = DBSCAN(eps=eps_value, min_samples=3)
dbscan.fit(scaled_df)

# Assign new cluster labels to each user
merged_data['dbscan_cluster'] = dbscan.labels_

# Check the new cluster distribution
print(merged_data['dbscan_cluster'].value_counts())

# Analyze the updated clusters by checking the mean values of features
cluster_summary = merged_data.groupby('dbscan_cluster')[numeric_columns].mean()
print(cluster_summary)

# Label suitable candidates based on cluster analysis
merged_data['suitable_candidate'] = merged_data['dbscan_cluster'].apply(
    lambda x: 'Highly Suitable' if x == 0 else 'Less Suitable' if x == 1 else 'Not Suitable'
)

# Display the result
print(merged_data[['username', 'dbscan_cluster', 'suitable_candidate']].head(20))  # Show more rows if needed

import matplotlib.pyplot as plt
import seaborn as sns

# Visualize the clusters using two key features, such as 'reputation' and 'total_stars'
plt.figure(figsize=(8,6))
sns.scatterplot(x=scaled_df['reputation'], y=scaled_df['total_stars'], hue=merged_data['dbscan_cluster'], palette='Set2')
plt.title('DBSCAN Clusters Based on Reputation and Total Stars')
plt.xlabel('Reputation')
plt.ylabel('Total Stars')
plt.show()

merged_data['suitable_candidate_numeric'] = merged_data['suitable_candidate'].apply(
    lambda x: 1 if x == 'Highly Suitable' else 0
)

selected_features = ['reputation', 'answers', 'questions', 'gold_badge_score', 
                     'silver_badge_score', 'bronze_badge_score', 'total_stars', 
                     'total_forks', 'total_contributions', 'commit_count', 
                     'pull_request_count', 'issue_count']

X = merged_data[selected_features]
y = merged_data['suitable_candidate_numeric']  # Target variable

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

from sklearn.metrics import classification_report, accuracy_score

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
}

grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

print("Best Parameters:", grid_search.best_params_)

best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)

# Make final predictions
final_y_pred = best_model.predict(X_test)

# Evaluate the final model
print("Final Accuracy:", accuracy_score(y_test, final_y_pred))
print(classification_report(y_test, final_y_pred))

from imblearn.over_sampling import SMOTE

# Create an instance of SMOTE
smote = SMOTE(random_state=42)

# Fit and resample the training data
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# Train the model on the resampled data
best_model.fit(X_resampled, y_resampled)

# Make predictions on the test set
final_y_pred = best_model.predict(X_test)

# Evaluate the final model
print("Final Accuracy after SMOTE:", accuracy_score(y_test, final_y_pred))
print(classification_report(y_test, final_y_pred))

importances = best_model.feature_importances_
feature_importances = pd.DataFrame(importances, index=X.columns, columns=["Importance"]).sort_values("Importance", ascending=False)
print(feature_importances)

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_test, final_y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Not Suitable", "Highly Suitable"], yticklabels=["Not Suitable", "Highly Suitable"])
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion Matrix')
plt.show()

# Count the number of candidates in each category
candidate_counts = merged_data['suitable_candidate'].value_counts()

# Display the counts
print(candidate_counts)
