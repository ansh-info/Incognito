import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
import numpy as np

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

# # Display the first few rows of GitHub data
print(github_data.head())

# # Display the first few rows of Stack Overflow data
print(stackoverflow_data.head())

# Extracting the username from the githubUrl in Stack Overflow data
stackoverflow_data['username'] = stackoverflow_data['githubUrl'].apply(lambda url: url.split('/')[-1] if isinstance(url, str) else None)

# Perform the join on the 'username' column
merged_data = pd.merge(stackoverflow_data, github_data, on='username', how='inner')

# # Display the first few rows of the merged dataset
print(merged_data.head())

# Select the relevant features
selected_features = ['reputation', 'answers', 'questions', 'gold_badge_score', 
                     'silver_badge_score', 'bronze_badge_score', 'total_stars', 
                     'total_forks', 'total_contributions', 'commit_count', 
                     'pull_request_count', 'issue_count']

# Select only numeric columns for filling missing values
numeric_columns = merged_data.select_dtypes(include=['float64', 'int64']).columns

# Step 1: Handle missing values by filling them with the mean of each numeric column
merged_data[numeric_columns] = merged_data[numeric_columns].fillna(merged_data[numeric_columns].mean())

# Step 2: Select the relevant features for modeling
X = merged_data[selected_features]

# Step 3: Normalize (standardize) the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Display the normalized data
print(X_scaled[:5])

# Step 3: Split the data into training and testing sets
X_train, X_test = train_test_split(X_scaled, test_size=0.3, random_state=42)

# Display the shape of the training and testing sets
print("Training set shape:", X_train.shape)
print("Testing set shape:", X_test.shape)

# Step 1: Increase eps for more relaxed clustering
dbscan = DBSCAN(eps=1.5, min_samples=3)  # Increase eps to 1.5 or 2.0

# Step 2: Fit DBSCAN to the scaled data
dbscan.fit(X_scaled)

# Step 3: Get the updated cluster labels
dbscan_labels = dbscan.labels_

# Step 4: Add the new cluster labels to the data
merged_data['cluster'] = dbscan_labels

cluster_0_candidates = merged_data[merged_data['cluster'] == 0]

# Step 5: Display the number of candidates in each cluster
unique, counts = np.unique(dbscan_labels, return_counts=True)
print("Number of candidates in each cluster:", dict(zip(unique, counts)))

# Step 6: Inspect the first few rows
print(merged_data[['username', 'cluster']].head())

# Analyze candidates in cluster 0
cluster_0_data = merged_data[merged_data['cluster'] == 0]

# Get descriptive statistics for cluster 0
print(cluster_0_data.describe())

# Display the top candidates in cluster 0
print(cluster_0_data[['username', 'reputation', 'total_contributions', 'gold_badge_score']].head())

# Analyze the outliers (cluster -1)
outliers = merged_data[merged_data['cluster'] == -1]

# Display the first few rows of the outliers
print(outliers[['username', 'reputation', 'total_contributions', 'gold_badge_score']].head())

# Analyze the candidates in cluster 1
cluster_1_data = merged_data[merged_data['cluster'] == 1]

# Display the candidates in cluster 1
print(cluster_1_data[['username', 'reputation', 'total_contributions', 'gold_badge_score']])

# Display the full range of candidates in Cluster 0
full_cluster_0_range = cluster_0_candidates[['username', 'reputation', 'total_contributions', 'gold_badge_score']].sort_values(by=['reputation', 'total_contributions'], ascending=False)

# Display the full range of candidates
print(full_cluster_0_range)

# Step 1: Standardize the selected features
selected_features = ['reputation', 'answers', 'questions', 'gold_badge_score', 
                     'silver_badge_score', 'bronze_badge_score', 'total_stars', 
                     'total_forks', 'total_contributions', 'commit_count', 
                     'pull_request_count', 'issue_count']

scaler = StandardScaler()
scaled_features = scaler.fit_transform(cluster_0_candidates[selected_features])

# # Step 2: Generate the linkage matrix and plot the dendrogram
linked = linkage(scaled_features, method='ward')

plt.figure(figsize=(10, 7))
dendrogram(linked)
plt.title("Dendrogram for Agglomerative Clustering")
plt.xlabel("Candidate Index")
plt.ylabel("Distance")
plt.show()

# Step 3: Choose the number of clusters based on the dendrogram
# Let's assume from the dendrogram that 3 clusters look natural

agglomerative = AgglomerativeClustering(n_clusters=3)
agglomerative_labels = agglomerative.fit_predict(scaled_features)

# Step 4: Add the cluster labels to the dataset
cluster_0_candidates['agglomerative_cluster'] = agglomerative_labels

# Step 5: Review the clusters
print(cluster_0_candidates['agglomerative_cluster'].value_counts())
print(cluster_0_candidates[['username', 'reputation', 'agglomerative_cluster']].head())

# # Analyze the clusters
for cluster_num in [0, 1, 2]:
    print(f"\nCluster {cluster_num} summary statistics:")
    print(cluster_0_candidates[cluster_0_candidates['agglomerative_cluster'] == cluster_num].describe())

# Filter out candidates in Cluster 1
cluster_1_candidates = cluster_0_candidates[cluster_0_candidates['agglomerative_cluster'] == 1]

# Inspect the top candidates sorted by reputation (or other features)
cluster_1_candidates_sorted = cluster_1_candidates.sort_values(by='reputation', ascending=False)
print(cluster_1_candidates_sorted[['username', 'reputation', 'total_contributions', 'gold_badge_score']].head())



# # Boxplot for reputation across clusters
plt.figure(figsize=(10, 6))
sns.boxplot(x='agglomerative_cluster', y='reputation', data=cluster_0_candidates)
plt.title('Reputation Distribution Across Clusters')
plt.show()

# # Bar plot for the number of candidates in each cluster
cluster_sizes = cluster_0_candidates['agglomerative_cluster'].value_counts()
plt.figure(figsize=(8, 5))
cluster_sizes.plot(kind='bar', color='skyblue')
plt.title('Cluster Sizes')
plt.xlabel('Cluster')
plt.ylabel('Number of Candidates')
plt.show()

# # Boxplots for key features across clusters
features_to_plot = ['reputation', 'total_contributions', 'gold_badge_score', 'silver_badge_score', 'bronze_badge_score']
plt.figure(figsize=(15, 10))
for i, feature in enumerate(features_to_plot):
    plt.subplot(2, 3, i+1)
    sns.boxplot(x='agglomerative_cluster', y=feature, data=cluster_0_candidates)
    plt.title(f'{feature} Across Clusters')
plt.tight_layout()
plt.show()



# # Correlation heatmap of selected features
plt.figure(figsize=(10, 8))
corr_matrix = cluster_0_candidates[selected_features].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation Heatmap of Selected Features')
plt.show()

# Save the DBSCAN model
with open('selection_algorithm/dbscan_model.pkl', 'wb') as dbscan_file:
    pickle.dump(dbscan, dbscan_file)

# Save the Agglomerative Clustering model
with open('selection_algorithm/agglomerative_model.pkl', 'wb') as agglomerative_file:
    pickle.dump(agglomerative, agglomerative_file)

print("Models have been saved as pickle files.")
