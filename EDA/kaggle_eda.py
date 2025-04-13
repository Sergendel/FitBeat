import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import config

# load the dataset
# kaggle dataset path
script_dir = Path(__file__).resolve().parent
dataset_path = script_dir.parent / Path(config.FILE_PATH)
df = pd.read_csv(dataset_path)

# Check basic information explicitly
print("Dataset overview:")
print(df.info())

print("\nBasic statistics:")
print(df.describe())

# Selecting key numerical features
features = ['tempo', 'energy', 'danceability', 'mode', 'valence']

# Correlation matrix
corr_matrix = df[features].corr()
print("\nCorrelation matrix:")
print(corr_matrix)

# Visualize correlation matrix as a heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Heatmap of Song Features")
plt.tight_layout()
plt.show()

# Explore genre distribution
plt.figure(figsize=(12, 6))
genre_counts = df['track_genre'].value_counts().head(10)  # top 10 genres
sns.barplot(x=genre_counts.index, y=genre_counts.values)
plt.title("Top 10 Track Genres")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visualize relations between key features
sns.pairplot(df[features].sample(1000), diag_kind='kde')  # use smaller sample if needed
plt.suptitle("Pairwise relationships of key features", y=1.02)
plt.show()
