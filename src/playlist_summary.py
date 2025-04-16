import logging
import pandas as pd

def summarize_results(tracks: pd.DataFrame) -> None:
    """
    Generates and explicitly displays a detailed summary of the final playlist recommendations.

    Parameters:
        tracks (pd.DataFrame):
            Tracks recommended explicitly by numeric filtering and/or semantic refinement.

    Returns:
        None
    """
    logging.info("\nFinal Recommendations:")
    for track_number, (_, row) in enumerate(tracks.iterrows()):
        logging.info(
            f"{track_number}. {row['track_name']} by {row['artists']} | "
            f"\n   Popularity: {row['popularity']} | Tempo: {row['tempo']} BPM | "
            f"Explicit: {row['explicit']} | Danceability: {row['danceability']} | "
            f"Energy: {row['energy']} | Loudness: {row['loudness']} dB | "
            f"Mode: {'Major' if row['mode'] == 1 else 'Minor'} | Speechiness: {row['speechiness']} | "
            f"Acousticness: {row['acousticness']} | Instrumentalness: {row['instrumentalness']} | "
            f"Liveness: {row['liveness']} | Valence: {row['valence']} | "
            f"Time Signature: {row['time_signature']} | Genre: {row['track_genre']}\n"
        )
