import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import lyricsgenius
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import config
sys.path.append(str(Path(__file__).resolve().parents[2]))
import config

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path=str(config.EMBEDDINGS_DB_PATH))
collection = chroma_client.get_or_create_collection(name="genius_embeddings")

# Initialize Genius API
genius = lyricsgenius.Genius(os.getenv("GENIUS_API_KEY"), timeout=15)


def retrieve_similar_songs(query, top_k=5):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0], results['metadatas'][0]


# On-the-fly embedding
def retrieve_or_add_song(artist, title):
    song_id = f"{artist} - {title}.txt"
    existing = collection.get(ids=[song_id])

    if existing['ids']:
        print("Song found in corpus.")
        return existing['documents'][0]

    print("Song not found. Fetching dynamically from Genius API...")
    song = genius.search_song(title, artist)

    if song:
        song_text = song.lyrics

        embedding = model.encode(song_text).tolist()
        collection.add(
            ids=[song_id],
            embeddings=[embedding],
            documents=[song_text],
            metadatas=[{"artist": artist, "title": title}]
        )

        print("Added dynamically to corpus!")
        return song_text
    else:
        print(f"Genius doesn't have '{title}' by {artist}. Falling back to numeric filtering.")
        return None

if __name__ == "__main__":
    query = "calm instrumental piano music"
    documents, metadata = retrieve_similar_songs(query, top_k=5)

    print("Retrieved Top Songs:")
    for doc, meta in zip(documents, metadata):
        print(f"- {meta['artist']} - {meta['title']} ({meta['genre']})")

    # Retrieve on-the-fly:
    artist = "Coldplay"
    title = "Adventure of a Lifetime"

    doc = retrieve_or_add_song(artist, title)
    if doc:
        print(f"Retrieved song : {title}")

