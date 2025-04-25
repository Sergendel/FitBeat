import os
import lyricsgenius
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
genius = lyricsgenius.Genius(os.getenv('GENIUS_API_KEY'), timeout=15, verbose=False)


def get_song_description(song_url):
    response = requests.get(song_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    description_div = soup.find('div', class_=lambda x: x and x.startswith('RichText__Container'))
    return description_div.get_text(separator='\n', strip=True) if description_div else "No description found."


def generate_song_context(artist, title, verbose = False):
    """
    Generates a comprehensive textual context for a song given artist and title.

    Parameters:
        artist (str): Name of the song's artist.
        title (str): Title of the song.

    Returns :
        str or None: Complete textual context (title, artist, album, description, lyrics) if the song is found;
                     None if the song is not found.
    """
    song = genius.search_song(title, artist)
    if song:
        description = get_song_description(song.url)
        context = (
            f"Title: {song.title}\n"
            f"Artist: {song.artist}\n"
            f"Album: {song.album}\n\n"
            f"Description:\n{description}\n\n"
            f"Lyrics:\n{song.lyrics}"
        )
        return context
    else:
        if verbose: print(f"Genius did not find '{title}' by '{artist}'.")
        return None
