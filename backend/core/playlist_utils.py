import json
import os

import pandas as pd
from yt_dlp import YoutubeDL
from googleapiclient.discovery import build
from backend import config
from dotenv import load_dotenv

def summarize_results(tracks: pd.DataFrame) -> None:
    """
    Generates and displays a detailed summary of the final playlist recommendations.

    Parameters:
        tracks (pd.DataFrame):
            Tracks recommended by numeric filtering and/or semantic refinement.

    Returns:
        None
    """
    print("\nFinal Recommendations:")
    for track_number, (_, row) in enumerate(tracks.iterrows(), start=1):
        print(
            f"{track_number}. {row['track_name']} by {row['artists']} | "
            f"\n   Popularity: {row['popularity']} | Tempo: {row['tempo']} BPM | "
            f"Explicit: {row['explicit']} | Danceability: {row['danceability']} | "
            f"Energy: {row['energy']} | Loudness: {row['loudness']} dB | "
            f"Mode: {'Major' if row['mode'] == 1 else 'Minor'} |"
            f" Speechiness: {row['speechiness']} | "
            f"Acousticness: {row['acousticness']} | "
            f"Instrumentalness: {row['instrumentalness']} | "
            f"Liveness: {row['liveness']} | Valence: {row['valence']} | "
            f"Time Signature: {row['time_signature']} | Genre: {row['track_genre']}\n"
        )


def youtube_search_top_result_old(query):
    """
    Returns top YouTube video URL, suppressing ffmpeg warnings.
    """
    # Handle testing environment
    if os.getenv("GITHUB_ACTIONS") == "true":
        # Return dummy URL explicitly for tests:
        return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # Production/default behavior
    ydl_opts = {
        "default_search": "ytsearch1",  # top result
        "quiet": True,  # reduce verbosity
        "no_warnings": True,  # suppress all warnings
        "skip_download": True,  # avoid downloads
        "ffmpeg_location": "",  # avoids ffmpeg check
        "logger": None,  # disables logger
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(query, download=False)
        video_url = info_dict["entries"][0]["webpage_url"]
        return video_url


def youtube_search_top_result(query):
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=1,
        type='video'
    ).execute()

    items = search_response.get('items', [])
    if not items:
        return None

    video_id = items[0]['id']['videoId']
    youtube_link = f"https://www.youtube.com/watch?v={video_id}"

    return youtube_link





def create_recommendation_table(tracks, folder_name):
    """
    Generates recommendation table:
    - Artist name
    - Track name
    - Official YouTube Link created here

    Returns structured JSON for API/frontend,and saves as CSV file clearly.
    """

    # Construct YouTube links:
    tracks = tracks.copy()

    # Handle GitHub Actions environment:
    if os.getenv("GITHUB_ACTIONS") == "true":
        # Assign dummy URL for tests:
        tracks["youtube_link"] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    else:
        # Production behavior:
        tracks["youtube_link"] = tracks.apply(
            lambda row: youtube_search_top_result(
                f"{row['artists']} {row['track_name']}"
            ),
            axis=1,
        )

    # Prepare DataFrame for output:
    table_df = tracks[["artists", "track_name", "youtube_link"]].copy()
    table_df.columns = ["Artist", "Track Name", "Official YouTube Link"]

    # Print formatted interactive table:
    print("\n\nRecommended Playlist:\n")
    print(table_df.to_string(index=False, justify="left"))

    # Structured JSON (for API response):
    playlist_json = {
        "playlist": [
            {
                "artist": row["Artist"],
                "track": row["Track Name"],
                "youtube_link": row["Official YouTube Link"],
            }
            for _, row in table_df.iterrows()
        ]
    }
    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        # Set save path:
        save_path = os.path.join(config.PLAYLISTS_DIR, folder_name)
        os.makedirs(save_path, exist_ok=True)
        # Save structured JSON:
        json_file = os.path.join(save_path, "playlist.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(playlist_json, f, indent=4)
        relative_json_file = os.path.relpath(json_file, config.PROJECT_ROOT)
        print(f"\nJSON playlist saved to '{relative_json_file}'")

        # Save as CSV:
        csv_file = os.path.join(save_path, "playlist.csv")
        table_df.to_csv(csv_file, index=False, encoding="utf-8")
        relative_csv_file = os.path.relpath(csv_file, config.PROJECT_ROOT)

        print(f"CSV playlist saved to '{relative_csv_file}'\n")

    # Return JSON for API response (Future task):
    return playlist_json
