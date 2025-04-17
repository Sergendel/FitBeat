import pandas as pd

def filtering_logic(params_explicit, dataset, top_n=10):
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

        print(f"Only found {len(filtered_tracks)} tracks, relaxing parameters... (Attempt {attempt + 1})")

        # Relaxing parameters explicitly
        for param, margin in margins.items():
            if param in params_explicit and params_explicit[param] is not None:
                params_explicit[param][0] = max(0 if param != 'loudness' else -60, params_explicit[param][0] - margin)
                params_explicit[param][1] = min(1 if param != 'tempo' and param != 'loudness' else (200 if param == 'tempo' else 0), params_explicit[param][1] + margin)

        attempt += 1

    if filtered_tracks.empty:
        print("No matching tracks found after multiple attempts.")

    return filtered_tracks.head(top_n)


def filter_tracks_by_audio_params(dataset, params, folder_name, num_tracks=10):
    """
        Filters tracks from the Kaggle dataset based on numeric audio parameters derived from user input.
        Parameters:
            params (dict):
                Dictionary containing numeric audio parameter ranges or values.
            folder_name (str):
                Name used for storing tracks and associated outputs resulting from this filtering step.
            num_tracks (int, optional, default=10):
                Maximum number of tracks to retrieve from numeric filtering.
        Returns:
            pd.DataFrame:
                DataFrame containing tracks that match numeric filtering criteria,
                including columns such as:
                    - 'track_name': Title of the track.
                    - 'artists': Artist name(s).
                    - 'popularity', 'tempo', 'explicit', 'danceability', 'energy', etc.
                If no tracks match criteria, returns an empty DataFrame.
    """
    filtered_tracks = filtering_logic(params, dataset, num_tracks)

    if filtered_tracks.empty:
        print("No tracks match criteria.")
        return filtered_tracks

    print("\nSearching Kaggle dataset for matching tracks...")
    unique_tracks_count = filtered_tracks[['track_name', 'artists']].drop_duplicates().shape[0]
    print(f"\n {unique_tracks_count} Selected Tracks :")
    for idx, row in filtered_tracks.iterrows():
        print(f"    -{idx} {row['track_name']} – {row['artists']}")
        # print(f"   • Tempo: {row['tempo']}")
        # print(f"   • Energy: {row['energy']}")
        # print(f"   • Danceability: {row['danceability']}")
        # print(f"   • Valence: {row['valence']}")
        # print(f"   • Loudness: {row['loudness']} dB")
        # print(f"   • Speechiness: {row['speechiness']}")
        # print(f"   • Instrumentalness: {row['instrumentalness']}")
        # print(f"   • Acousticness: {row['acousticness']}")
        # print(f"   • Liveness: {row['liveness']}")
        # print(f"   • Genre: {row['track_genre']}")
        # print(f"   • Popularity: {row['popularity']}")
    #print(
    #    f"\n***The tracks will be stored in the folder '{folder_name}'.\n")
    return filtered_tracks