import os
import pandas as pd
import lyricsgenius
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import config
from pathlib import Path


# Load environment variables
load_dotenv()
genius = lyricsgenius.Genius(os.getenv('GENIUS_API_KEY'), timeout=15)

# kaggle dataset path
script_dir = Path(__file__).resolve().parent
DATASET_PATH = script_dir.parent / Path(config.FILE_PATH)

# folders to store corpus and metadata (list of songs in the corpus)
CORPUS_DIR = "genius_corpus"
METADATA_FILE = "corpus_metadata.csv"

# create folder
os.makedirs(CORPUS_DIR, exist_ok=True)


def get_song_description(song_url):
    response = requests.get(song_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    description_div = soup.find('div', class_=lambda x: x and x.startswith('RichText__Container'))
    return description_div.get_text(separator='\n', strip=True) if description_div else "No description found."


def create_basic_corpus(tempo=None, danceability=None, energy=None, mode=None, valence=None, track_genre=None,
                        max_songs=100):
    df = pd.read_csv(DATASET_PATH)

    # Explicitly build filters
    filters = []
    if tempo is not None:
        filters.append(df['tempo'] > tempo)
    if danceability is not None:
        filters.append(df['danceability'] > danceability)
    if energy is not None:
        filters.append(df['energy'] > energy)
    if mode is not None:
        filters.append(df['mode'] == mode)
    if valence is not None:
        filters.append(df['valence'] > valence)
    if track_genre is not None:
        filters.append(df['track_genre'].str.lower() == track_genre.strip().lower())

    # Apply filters explicitly
    if filters:
        filtered_df = df
        for f in filters:
            filtered_df = filtered_df[f]
    else:
        filtered_df = df  # if no filter, use full dataset clearly

    filtered_df = filtered_df.drop_duplicates(subset=['track_name', 'artists']).head(max_songs)

    metadata_records = []

    for idx, track in filtered_df.iterrows():
        title = track['track_name'].strip()
        artist = track['artists'].split(';')[0].strip()
        print(f"Processing: {artist} - {title}")

        try:
            song = genius.search_song(title, artist)
            if song:
                filename = f"{artist} - {title}.txt"
                file_path = os.path.join(CORPUS_DIR, filename)

                description = get_song_description(song.url)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {song.title}\n")
                    f.write(f"Artist: {song.artist}\n")
                    f.write(f"Album: {song.album}\n\n")
                    f.write(f"Description:\n{description}\n\n")
                    f.write(f"Lyrics:\n{song.lyrics}\n")

                print(f"Saved: {filename}")

                metadata_records.append({
                    'artist': artist,
                    'title': title,
                    'filename': filename,
                    'tempo': track['tempo'],
                    'energy': track['energy'],
                    'danceability': track['danceability'],
                    'mode': track['mode'],
                    'valence': track['valence'],
                    'genre': track['track_genre']
                })

            else:
                print(f"Not found on Genius: {artist} - {title}")

        except Exception as e:
            print(f"Error processing {artist} - {title}: {e}")

    metadata_df = pd.DataFrame(metadata_records)
    metadata_df.to_csv(METADATA_FILE, index=False, encoding='utf-8')

    print(f"\nCorpus creation complete. {len(metadata_records)} songs saved.")
    print(f"Metadata explicitly saved in '{METADATA_FILE}'.")


# Explicitly call your function with example parameters:
if __name__ == "__main__":
    create_basic_corpus(
        tempo=130,
        danceability=0.8,
        energy=0.8,
        mode=None,
        valence=0.8,
        track_genre=None,
        max_songs=100
    )
