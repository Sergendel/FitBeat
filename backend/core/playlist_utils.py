import json
import os

import pandas as pd
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL

from backend import config


class YouTubeSearcher:
    def __init__(self, youtube_api_key=None):
        if youtube_api_key is None:
            self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        else:
            self.youtube_api_key = youtube_api_key

    def search_top_result(self, query):
        if os.getenv("GITHUB_ACTIONS") == "true":
            return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        youtube = build("youtube", "v3", developerKey=self.youtube_api_key)

        search_response = (
            youtube.search()
            .list(q=query, part="id,snippet", maxResults=1, type="video")
            .execute()
        )

        items = search_response.get("items", [])
        if not items:
            return None

        video_id = items[0]["id"]["videoId"]
        youtube_link = f"https://www.youtube.com/watch?v={video_id}"

        return youtube_link

    def youtube_search_top_result_yt_dlp(self, query):
        if os.getenv("GITHUB_ACTIONS") == "true":
            return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        ydl_opts = {
            "default_search": "ytsearch1",
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "ffmpeg_location": "",
            "logger": None,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(query, download=False)
            video_url = info_dict["entries"][0]["webpage_url"]
            return video_url

    @staticmethod
    def summarize_results(tracks: pd.DataFrame) -> None:
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
                f"Time Signature: {row['time_signature']} | "
                f"Genre: {row['track_genre']}\n"
            )

    def create_recommendation_table(self, tracks, folder_name):
        tracks = tracks.copy()

        if os.getenv("GITHUB_ACTIONS") == "true":
            tracks["youtube_link"] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        else:
            tracks["youtube_link"] = tracks.apply(
                lambda row: self.search_top_result(
                    f"{row['artists']} {row['track_name']}"
                ),
                axis=1,
            )

        table_df = tracks[["artists", "track_name", "youtube_link"]].copy()
        table_df.columns = ["Artist", "Track Name", "Official YouTube Link"]

        print("\n\nRecommended Playlist:\n")
        print(table_df.to_string(index=False, justify="left"))

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
            save_path = os.path.join(config.PLAYLISTS_DIR, folder_name)
            os.makedirs(save_path, exist_ok=True)

            json_file = os.path.join(save_path, "playlist.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(playlist_json, f, indent=4)
            relative_json_file = os.path.relpath(json_file, config.PROJECT_ROOT)
            print(f"\nJSON playlist saved to '{relative_json_file}'")

            csv_file = os.path.join(save_path, "playlist.csv")
            table_df.to_csv(csv_file, index=False, encoding="utf-8")
            relative_csv_file = os.path.relpath(csv_file, config.PROJECT_ROOT)

            print(f"CSV playlist saved to '{relative_csv_file}'\n")

        return playlist_json
