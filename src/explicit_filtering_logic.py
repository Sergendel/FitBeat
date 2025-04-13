import pandas as pd

def explicit_filtering_logic(params_explicit, dataset, top_n=10):
    tempo_margin = 10
    energy_margin = 0.05
    dance_margin = 0.1
    valence_margin = 0.1
    loudness_margin = 2
    speechiness_margin = 0.05
    instrumentalness_margin = 0.05

    attempt = 0
    max_attempts = 10

    filtered_tracks = pd.DataFrame()

    while attempt < max_attempts:
        conditions = [
            dataset['tempo'].between(*params_explicit['tempo']),
            dataset['energy'].between(*params_explicit['energy']),
            dataset['danceability'].between(*params_explicit['danceability']),
            dataset['valence'].between(*params_explicit['valence']),
            dataset['loudness'].between(*params_explicit['loudness']),
            dataset['speechiness'].between(*params_explicit['speechiness']),
            dataset['instrumentalness'].between(*params_explicit['instrumentalness'])
        ]

        # Explicit check for track_genre to handle NoneType
        if params_explicit.get('track_genre') is not None:
            conditions.append(dataset['track_genre'].isin(params_explicit['track_genre']))

        filtered_tracks = dataset.loc[pd.concat(conditions, axis=1).all(axis=1)]
        filtered_tracks = filtered_tracks.drop_duplicates(subset=['track_name', 'artists']).sort_values(by='popularity', ascending=False)

        if len(filtered_tracks) >= top_n:
            break

        print(f"Only found {len(filtered_tracks)} tracks, explicitly relaxing parameters... (Attempt {attempt + 1})")

        params_explicit['tempo'][0] = max(60, params_explicit['tempo'][0] - tempo_margin)
        params_explicit['tempo'][1] = min(200, params_explicit['tempo'][1] + tempo_margin)
        params_explicit['energy'][0] = max(0.0, params_explicit['energy'][0] - energy_margin)
        params_explicit['energy'][1] = min(1.0, params_explicit['energy'][1] + energy_margin)
        params_explicit['danceability'][0] = max(0.0, params_explicit['danceability'][0] - dance_margin)
        params_explicit['danceability'][1] = min(1.0, params_explicit['danceability'][1] + dance_margin)
        params_explicit['valence'][0] = max(0.0, params_explicit['valence'][0] - valence_margin)
        params_explicit['valence'][1] = min(1.0, params_explicit['valence'][1] + valence_margin)
        params_explicit['loudness'][0] = max(-60, params_explicit['loudness'][0] - loudness_margin)
        params_explicit['loudness'][1] = min(0, params_explicit['loudness'][1] + loudness_margin)
        params_explicit['speechiness'][0] = max(0.0, params_explicit['speechiness'][0] - speechiness_margin)
        params_explicit['speechiness'][1] = min(1.0, params_explicit['speechiness'][1] + speechiness_margin)
        params_explicit['instrumentalness'][0] = max(0.0, params_explicit['instrumentalness'][0] - instrumentalness_margin)
        params_explicit['instrumentalness'][1] = min(1.0, params_explicit['instrumentalness'][1] + instrumentalness_margin)

        attempt += 1

    if filtered_tracks.empty:
        print("No matching tracks explicitly found after multiple attempts.")

    return filtered_tracks.head(top_n)
