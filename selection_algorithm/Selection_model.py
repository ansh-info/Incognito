import sys
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score,accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import resample
import pickle

github_uers = pd.read_csv('github.csv', on_bad_lines='skip')
sof_users = pd.read_csv('stackoverflow.csv')

sof_users['github_username'] = sof_users['githubUrl'].apply(lambda x: x.split('/').pop() if isinstance(x, str) else None) #applying this function on the whole column also checking conv nans

# print(github_uers.head())
# print(sof_users.head())

# print(len(github_uers))
# print(len(sof_users))

merged_df = pd.merge(sof_users,github_uers, left_on='github_username', right_on='username')
# print(merged_df.head())
# print(len(merged_df))

#print(merged_df.columns)

merged_df['created_at'] = pd.to_datetime(merged_df['created_at'], errors='coerce')
merged_df['updated_at'] = pd.to_datetime(merged_df['updated_at'], errors='coerce')

merged_df['member_exp'] = (merged_df['updated_at'] - merged_df['created_at']).dt.days

#print(merged_df.dtypes)

selected_features=['reputation', 'reached', 'answers', 'questions', 'gold_badge_score',
       'silver_badge_score', 'bronze_badge_score', 'followers',
       'public_repos', 'total_stars', 'total_forks', 'total_contributions',
       'total_repos', 'commit_count', 'pull_request_count', 'issue_count',
       'member_exp']

#print(selected_features)

# Checking for missing values in the dataset
missing_values = merged_df[selected_features].isnull().sum()

# Getting summary statistics for the dataset
summary_statistics = merged_df[selected_features].describe()

#print(missing_values, summary_statistics)

df=merged_df[selected_features]
# Set up the matplotlib figure for the correlation matrix
# plt.figure(figsize=(12, 10))

# # # Compute the correlation matrix
# correlation_matrix = df[selected_features].corr()

# # # Generate a heatmap
# sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
# plt.title('Correlation Matrix')
# plt.show()

# Visualizing the dataset for correlation of 2 variables
#plt.figure(figsize=(16, 10))

# Scatter plot for the original data
#plt.subplot(1, 2, 1)
# plt.scatter(df['followers'], df['reputation'], alpha=0.6, edgecolors='w', s=50)
# plt.title('Before Outlier Removal')
# plt.xlabel('Followers')
# plt.ylabel('Reputation')

# plt.show()

#PCA for clustering

# Standardizing the data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df)

# Applying PCA
pca = PCA()
pca.fit(scaled_data)

# Explained variance for each principal component
explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

# Visualizing the explained variance
# plt.figure(figsize=(10, 6))
# plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, marker='o', linestyle='--')
# plt.title('Cumulative Explained Variance by Principal Components')
# plt.xlabel('Number of Principal Components')
# plt.ylabel('Cumulative Explained Variance')
# plt.grid()
# plt.show()

# Retain 5 principal components and transform the data
pca = PCA(n_components=7)
pca_transformed_data = pca.fit_transform(scaled_data)

# Determine the optimal number of clusters using the elbow method and silhouette scores##
wcss = []
silhouette_scores = []
k_range = range(2, 11)  # Testing for clusters from 2 to 10

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(pca_transformed_data)
    wcss.append(kmeans.inertia_)  # Within-cluster sum of squares
    silhouette_scores.append(silhouette_score(pca_transformed_data, kmeans.labels_))

# Plot the elbow method
# plt.figure(figsize=(12, 5))

# plt.subplot(1, 2, 1)
# plt.plot(k_range, wcss, marker='o', linestyle='--')
# plt.title('Elbow Method for Optimal K')
# plt.xlabel('Number of Clusters (K)')
# plt.ylabel('WCSS')
# plt.grid()

# # Plot the silhouette scores
# plt.subplot(1, 2, 2)
# plt.plot(k_range, silhouette_scores, marker='o', linestyle='--')
# plt.title('Silhouette Scores for Different K')
# plt.xlabel('Number of Clusters (K)')
# plt.ylabel('Silhouette Score')
# plt.grid()

# plt.tight_layout()
# plt.show()

# Apply K-means clustering with K=2
kmeans_final = KMeans(n_clusters=3, random_state=42)
cluster_labels = kmeans_final.fit_predict(pca_transformed_data)

# Add cluster labels to the remaining data
original_df = df.copy()
original_df['Cluster'] = cluster_labels

# Visualize the clusters in the first two principal components
# plt.figure(figsize=(10, 6))
# plt.scatter(pca_transformed_data[:, 0], pca_transformed_data[:, 1], c=cluster_labels, cmap='viridis', s=50)
# plt.title('K-means Clustering with K=2 (First Two Principal Components)')
# plt.xlabel('Principal Component 1')
# plt.ylabel('Principal Component 2')
# plt.colorbar(label='Cluster')
# plt.show()

# print(original_df[original_df.Cluster==0].head()) #Good - Best fit for selection
# print(original_df[original_df.Cluster==1].head()) #Decent - Reject candidates
# print(original_df[original_df.Cluster==2].head()) #Exceptional - Most likely they will not accept interviews

#Data for logistic regression
df_lr=original_df.copy()
# print(df_lr.head())

# Splitting the data
X = df_lr.drop(columns=['Cluster'])
y = df_lr['Cluster']

# print(X.head())
# print(y.head())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# Train the logistic regression model
logreg = LogisticRegression(max_iter=200)
logreg.fit(X_train_scaled, y_train)

# Make predictions on the test set
y_pred = logreg.predict(X_test_scaled)

# Saving the trained logistic regression model to a pickle file
with open('logistic_regression_model.pkl', 'wb') as file:    
    pickle.dump(logreg, file)

# Optionally, save the scaler too if you need to reuse it
with open('scaler.pkl', 'wb') as file:    
    pickle.dump(scaler, file)

print("Logistic regression model and scaler saved to logistic_regression_model.pkl and scaler.pkl")

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print(df_lr[df_lr.Cluster==2])