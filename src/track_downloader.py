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

    def _safe_filename(self, track_name, artist_name, track_index=None):
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", f"{artist_name} - {track_name}")
        if track_index is not None:
            return f"{track_index:02d} - {safe_name}"
        return safe_name

    def download_and_convert(self, track_name, artist_name, subfolder, track_index=None):
        filename_safe = self._safe_filename(track_name, artist_name, track_index)
        save_folder = Path(subfolder)
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

        # find the downloaded file
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


    def retrieve_and_convert(self, tracks, folder_name):
           """
               Retrieves audio tracks from YouTube and converts them to MP3 format.
               Parameters:
                   tracks (pd.DataFrame): Tracks to retrieve and convert.
                   folder_name (str): Folder name for storing MP3 files.
               Returns:
                   None
               Notes:
                   - Skips downloading if a track file already exists.
                   - Logs each successful download and conversion.
           """
           folder_path = os.path.join(config.TRACKS_DIR, folder_name)
           os.makedirs(folder_path, exist_ok=True)
           print(f"Downloading recommended tracks explicitly and converting to MP3 explicitly.\n"
                 f"Saving explicitly playlist to folder explicitly: '{folder_path}'\n")
           for idx, track in enumerate(tracks.itertuples()):
               track_number = idx + 1
               self.download_and_convert(
                   track.track_name,
                   track.artists,
                   folder_path,
                   track_index=track_number
               )



#  Example Usage:
if __name__ == "__main__":

    # Initialize TrackDownloader
    downloader = TrackDownloader()

    # Example track details
    track_name = "Blinding Lights"
    artist_name = "The Weeknd"
    subfolder = "test_download"

    # Execute download and conversion
    downloader.download_and_convert(track_name, artist_name, subfolder, 3)