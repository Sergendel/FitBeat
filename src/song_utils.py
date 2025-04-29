import os
import lyricsgenius
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from types import SimpleNamespace

import config

# Load environment variables
load_dotenv()
genius = lyricsgenius.Genius(os.getenv('GENIUS_API_KEY'), timeout=15, verbose=False)


def get_song_description(song_url):
    response = requests.get(song_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    description_div = soup.find('div', class_=lambda x: x and x.startswith('RichText__Container'))
    return description_div.get_text(separator='\n', strip=True) if description_div else "No description found."


def generate_song_context(artist, track_name):
    """
    Generates a comprehensive textual context for a song given artist and track_name.

    Parameters:
        artist (str): Name of the song's artist.
        track_name (str): track_name of the song.

    Returns :
        str or None: Complete textual context (track_name, artist, album, description, lyrics) if the song is found;
                     None if the song is not found.
    """
    verbose = config.VERBOSE


    if os.getenv("GITHUB_ACTIONS") == "true":
        song = SimpleNamespace(
            title="Dummy Title",
            artist="Dummy Artist",
            album="Dummy Album",
            url="https://dummy.url",
            lyrics="Love is in the air"
        )
        description ="Make love not war"
    else:
        song = genius.search_song(title = track_name, artist = artist)
        description = get_song_description(song.url)

    if song:
        #time.sleep(1.5)
        context = (
            f"track_name: {song.title}\n"
            f"Artist: {song.artist}\n"
            f"Album: {song.album}\n\n"
            f"Description:\n{description}\n\n"
            f"Lyrics:\n{song.lyrics}"
        )
        return context
    else:
        if verbose: print(f"Genius did not find '{track_name}' by '{artist}'.")
        return None
