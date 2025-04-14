import os
import subprocess
import re
from yt_dlp import YoutubeDL
from pathlib import Path
import config

class TrackDownloader:
    def __init__(self):
        self.ffmpeg_path = config.FFMPEG_PATH
        self.TRACKS_DIR = config.TRACKS_DIR

    def _safe_filename(self, track_name, artist_name):
        return re.sub(r'[\\/*?:"<>|]', "_", f"{artist_name} - {track_name}")

    def download_and_convert(self, track_name, artist_name, subfolder):
        filename_safe = self._safe_filename(track_name, artist_name)
        save_folder = self.TRACKS_DIR/ subfolder
        save_folder.mkdir(parents=True, exist_ok=True)
        output_mp3 = save_folder / f"{filename_safe}.mp3"

        # Check if the file already exists
        if output_mp3.exists():
            print(f"'{output_mp3.name}' already exists, skipping download.")
            return

        query = f"{track_name} {artist_name} audio"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"{save_folder}/{filename_safe}.%(ext)s",
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])

        downloaded_file = next(save_folder.glob(f"{filename_safe}.*"))

        subprocess.run(
            [self.ffmpeg_path, "-i", str(downloaded_file), "-vn",
             "-acodec", "libmp3lame", "-y", str(output_mp3)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        downloaded_file.unlink(missing_ok=True)

        print(f"Downloaded and converted: {output_mp3.name}")



#  Example Usage:
if __name__ == "__main__":

    # Initialize TrackDownloader
    downloader = TrackDownloader()

    # Example track details
    track_name = "Blinding Lights"
    artist_name = "The Weeknd"
    subfolder = "test_download"

    # Execute download and conversion
    downloader.download_and_convert(track_name, artist_name, subfolder)