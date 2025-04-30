import pandas as pd

# kaggle dataset path
dataset_path = r"C:\work\INTERVIEW_PREPARATION\FitBeat\data\kaggle\dataset.csv"
df = pd.read_csv(dataset_path)

# Explicitly checking unique genres:
genres = df["track_genre"].unique()
print("Explicitly listed genres in the dataset:")
for genre in sorted(genres):
    print(f"- {genre}")
