import pandas as pd

import pandas as pd

def explicit_filtering_logic(params_explicit, dataset, top_n=10):
    margins = {
        'tempo': 10,
        'energy': 0.05,
        'danceability': 0.1,
        'valence': 0.1,
        'loudness': 2,
        'speechiness': 0.05,
        'instrumentalness': 0.05,
        'acousticness': 0.05,
        'liveness': 0.05
    }

    attempt = 0
    max_attempts = 10

    filtered_tracks = pd.DataFrame()

    while attempt < max_attempts:
        conditions = []

        for feature in ['tempo', 'energy', 'danceability', 'valence', 'loudness', 'speechiness', 'instrumentalness', 'acousticness', 'liveness']:
            if feature in params_explicit and params_explicit[feature] is not None:
                conditions.append(dataset[feature].between(*params_explicit[feature]))

        if params_explicit.get('track_genre'):
            conditions.append(dataset['track_genre'].isin(params_explicit['track_genre']))

        if conditions:
            combined_conditions = pd.concat(conditions, axis=1).all(axis=1)
            filtered_tracks = dataset.loc[combined_conditions].drop_duplicates(subset=['track_name', 'artists']).sort_values(by='popularity', ascending=False)

        if len(filtered_tracks) >= top_n:
            break

        print(f"Only found {len(filtered_tracks)} tracks, explicitly relaxing parameters... (Attempt {attempt + 1})")

        # Relaxing parameters explicitly
        for param, margin in margins.items():
            if param in params_explicit and params_explicit[param] is not None:
                params_explicit[param][0] = max(0 if param != 'loudness' else -60, params_explicit[param][0] - margin)
                params_explicit[param][1] = min(1 if param != 'tempo' and param != 'loudness' else (200 if param == 'tempo' else 0), params_explicit[param][1] + margin)

        attempt += 1

    if filtered_tracks.empty:
        print("No matching tracks explicitly found after multiple attempts.")

    return filtered_tracks.head(top_n)

