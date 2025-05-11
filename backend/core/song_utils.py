import json
import os
from types import SimpleNamespace

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
        self.genius_api_key = genius_api_key

        # Initialize Genius client
        # self.genius = lyricsgenius.Genius(
        #     genius_api_key, timeout=timeout, verbose=self.verbose
        # )

    def search_song(self, title, artist):
        headers = {"Authorization": f"Bearer {self.genius_api_key}"}
        search_url = f"https://api.genius.com/search?q={artist}%20{title}"

        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            if self.verbose:
                print(f"Genius API explicitly failed: {response.status_code}")
            return None

        data = response.json()
        hits = data.get("response", {}).get("hits", [])

        if not hits:
            if self.verbose:
                print("No song matches found explicitly")
            return None

        # Pick the best match
        song_info = hits[0]["result"]

        song = SimpleNamespace(
            title=song_info.get("title"),
            artist=song_info["primary_artist"].get("name"),
            album=None,  # Genius search doesn't directly return album info.
            url=song_info["url"],
            lyrics=self.get_lyrics_from_url(song_info["url"]),
        )

        return song

    import requests
    from bs4 import BeautifulSoup

    def get_lyrics_from_url(self, song_url):
        page = requests.get(song_url)
        if page.status_code != 200:
            if self.verbose:
                print(f"Failed to retrieve lyrics page explicitly: {page.status_code}")
            return None

        html = BeautifulSoup(page.text, "html.parser")

        # Genius lyrics are stored in multiple specific divs
        lyrics_containers = html.select('div[class^="Lyrics__Container"], .lyrics')

        if not lyrics_containers:
            if self.verbose:
                print("Lyrics explicitly not found using known Genius containers.")
            return None

        # Explicitly retrieve only the lyrics text without unrelated content
        lyrics = "\n".join(
            div.get_text(separator="\n", strip=True) for div in lyrics_containers
        )

        # Explicitly truncate lyrics if too long
        # (e.g., 4000 tokens max ~3200 words explicitly)
        MAX_WORDS = 3200
        lyrics_words = lyrics.split()
        if len(lyrics_words) > MAX_WORDS:
            lyrics = " ".join(lyrics_words[:MAX_WORDS])
            if self.verbose:
                print(
                    "Lyrics explicitly truncated to avoid"
                    " exceeding embedding limits explicitly."
                )

        return lyrics.strip()

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
            try:
                # song = self.genius.search_song(title=track_name, artist=artist)
                song = self.search_song(title=track_name, artist=artist)

            except requests.exceptions.RequestException as e:
                print(f"Network-related error during Genius API call: {str(e)}")
                return None
            except json.JSONDecodeError as e:
                print(f"JSON decoding error from Genius API: {str(e)}")
                return None
            except Exception as e:
                print(f"Unexpected error from Genius API: {str(e)}")
                return None

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
