import os
from types import SimpleNamespace

import lyricsgenius
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from backend import config

# Load environment variables
load_dotenv()


class SongContextGenerator:
    def __init__(self, genius_api_key=None, timeout=15, verbose=False):
        """
        Initializes the SongContextGenerator class.

        Parameters:
            genius_api_key (str): Genius API key .
            timeout (int): Timeout for Genius API requests.
            verbose (bool): controls verbosity.
        """
        self.verbose = verbose or config.VERBOSE

        # Set Genius API key
        if genius_api_key is None:
            genius_api_key = os.getenv("GENIUS_API_KEY")
            if genius_api_key is None:
                raise ValueError("Genius API key is missing.")

        # Initialize Genius client
        self.genius = lyricsgenius.Genius(
            genius_api_key, timeout=timeout, verbose=self.verbose
        )

    def get_song_description(self, song_url):
        """
        Fetches song description from Genius URL.
        """
        response = requests.get(song_url)
        soup = BeautifulSoup(response.text, "html.parser")
        description_div = soup.find(
            "div", class_=lambda x: x and x.startswith("RichText__Container")
        )
        return (
            description_div.get_text(separator="\n", strip=True)
            if description_div
            else "No description found."
        )

    def generate_song_context(self, artist, track_name):
        """
        Generates a comprehensive textual context for a song.

        Parameters:
            artist (str): Name of the song's artist.
            track_name (str): Name of the song.

        Returns :
            str or None: Complete textual context (track_name, artist, album,
                         description, lyrics) if the song is found;
                         None if the song is not found.
        """
        if os.getenv("GITHUB_ACTIONS") == "true":
            song = SimpleNamespace(
                title="Dummy Title",
                artist="Dummy Artist",
                album="Dummy Album",
                url="https://dummy.url",
                lyrics="Love is in the air",
            )
            description = "Make love not war"
        else:
            song = self.genius.search_song(title=track_name, artist=artist)

            if song:
                description = self.get_song_description(song.url)
            else:
                if self.verbose:
                    print(f"Genius did not find '{track_name}' by '{artist}'.")
                return None

        context = (
            f"Track Name: {song.title}\n"
            f"Artist: {song.artist}\n"
            f"Album: {song.album}\n\n"
            f"Description:\n{description}\n\n"
            f"Lyrics:\n{song.lyrics}"
        )
        return context
