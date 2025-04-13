import lyricsgenius
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
genius = lyricsgenius.Genius(os.getenv('GENIUS_API_KEY'))

tracks = [
    {"title": "Ferrari", "artist": "James Hype"},
    {"title": "I'm Good (Blue)", "artist": "David Guetta"},
    {"title": "INDUSTRY BABY", "artist": "Lil Nas X"},
    {"title": "Unholy", "artist": "Sam Smith"},
    {"title": "Mr. Brightside", "artist": "The Killers"}
]

output_folder = "genius_corpus_simple"
os.makedirs(output_folder, exist_ok=True)

def get_song_description(song_url):
    response = requests.get(song_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # get description
    description_div = soup.find('div', class_=lambda x: x and x.startswith('RichText__Container'))

    if description_div:
        return description_div.get_text(separator='\n', strip=True)
    else:
        return "No description found."



for track in tracks:
    song = genius.search_song(track["title"], track["artist"])
    if song:
        filename = f"{track['artist']} - {track['title']}.txt"
        file_path = os.path.join(output_folder, filename)

        # description
        description = get_song_description(song.url)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {song.title}\n")
            f.write(f"Artist: {song.artist}\n")
            f.write(f"Album: {song.album}\n\n")

            # song description
            f.write(f"Description:\n{description}\n\n")

            # lyrics
            f.write(f"Lyrics:\n{song.lyrics}\n")

        print(f"Song's lyrics and description downloaded: {filename}")
    else:
        print(f"The song was not found: {track['artist']} - {track['title']}")

print("Done.")
