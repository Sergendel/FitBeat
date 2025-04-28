import os
import pandas as pd
import lyricsgenius
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import config
from src.song_utils import generate_song_context


# Load environment variables
load_dotenv()
genius = lyricsgenius.Genius(os.getenv('GENIUS_API_KEY'), timeout=15)

# kaggle dataset path
DATASET_PATH = config.FILE_PATH

# folders to store corpus and metadata (list of songs in the corpus)
CORPUS_DIR = config.CORPUS_DIR
CORPUS_METADATA_PATH = config.CORPUS_METADATA_PATH

# create folder
os.makedirs(CORPUS_DIR, exist_ok=True)



def create_basic_corpus(tempo=None, danceability=None, energy=None, mode=None, valence=None, track_genre=None,
                        max_songs=100):
    df = pd.read_csv(DATASET_PATH)

    # Build filters
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

    # Apply filters
    if filters:
        combined_filter = filters[0]
        for f in filters[1:]:
            combined_filter &= f
        filtered_df = df[combined_filter]
    else:
        filtered_df = df
    filtered_df = filtered_df.drop_duplicates(subset=['track_name', 'artists']).head(max_songs)

    metadata_records = []

    for i, (idx, track) in enumerate(filtered_df.iterrows()):
        track_name = track['track_name'].strip()
        artist = track['artists'].split(';')[0].strip()
        print(f"Processing: {artist} - {track_name}")

        try:
            # Get song context
            song_context = generate_song_context(artist, track_name)

            if song_context:
                filename = f"{artist} - {track_name}.txt"
                file_path = os.path.join(CORPUS_DIR, filename)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(song_context)

                print(f"Track {i} Saved: {filename}")

                metadata_records.append({
                    'artist': artist,
                    'track_name': track_name,
                    'filename': filename,
                    'tempo': track['tempo'],
                    'energy': track['energy'],
                    'danceability': track['danceability'],
                    'mode': track['mode'],
                    'valence': track['valence'],
                    'genre': track['track_genre']
                })
            else:
                print(f"Not found on Genius: {artist} - {track_name}")

        except Exception as e:
            print(f"Error processing {artist} - {track_name}: {e}")

    metadata_df = pd.DataFrame(metadata_records)
    metadata_df.to_csv(CORPUS_METADATA_PATH, index=False, encoding='utf-8')

    print(f"\nCorpus creation complete. {len(metadata_records)} songs saved.")
    print(f"Metadata explicitly saved in '{CORPUS_METADATA_PATH}'.")


# Explicitly call your function with example parameters:
if __name__ == "__main__":
    create_basic_corpus(
        tempo=120,
        danceability=0.7,
        energy=0.6,
        mode=None,
        valence=0.6,
        track_genre=None,
        max_songs=200
    )
