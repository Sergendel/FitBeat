import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import lyricsgenius
import os
from dotenv import load_dotenv
import pandas as pd
from src.song_utils import generate_song_context
import multiprocessing

# Load environment
load_dotenv()

# Import config
sys.path.append(str(Path(__file__).resolve().parents[2]))
import config

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path=str(config.EMBEDDINGS_DB_PATH))
num_threads = min(2, multiprocessing.cpu_count())
collection_name = "genius_embeddings"
try:
    chroma_client.delete_collection(name=collection_name)
except Exception:
    pass  # Ignore if it doesn't exist
collection = chroma_client.get_or_create_collection(
    name="genius_embeddings",
    metadata={
        "hnsw:space": "cosine",             # Adjust if needed
        "hnsw:num_threads": 1 #num_threads     # This correctly sets thread count
    }
)
# Initialize Genius API
genius = lyricsgenius.Genius(os.getenv("GENIUS_API_KEY"), timeout=15, verbose=False)

# find similar tracks (semantic) to user provided track (name and artist)
# TODO: PREPARATION FOR "Semantic_Search" ACTION,  MEANWHILE NOT IN USE  !!!
def find_semantically_similar_songs(query, top_k=5):
    """
    Find and return the top-k semantically similar songs from the ChromaDB embedding collection,
    based on the provided free-text query.

    Parameters:
        query (str):
            A textual query describing desired characteristics or examples of the tracks.
            Examples: "calm instrumental music", "songs similar to 'Blinding Lights'".
            top_k (int, optional, default=5): The number of similar songs to return.

    Returns:
        tuple:
            - documents (list[str]): Context of the similar songs.
            - metadatas (list[dict]): Associated metadata (artist, title, genre) for each song.

    Example:
         documents, metadata = find_semantically_similar_songs("calm piano music", top_k=3)
    """

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0], results['metadatas'][0]

def embed_user_prompt(user_prompt):
    return model.encode(user_prompt).tolist()


def get_or_create_song_embedding(artist: str, title: str, verbose=False) -> object:
    """
        Get the embedding and context for a given song from the local ChromaDB corpus.
        If the song isn't available locally, dynamically fetch context from Genius API, generate the embedding,
        and add it to the corpus.

        Parameters:
            artist (str): Artist name associated with the song.
            title (str): Song title.

        Returns:
            str or None: The context of the song if found or fetched, else e None.
        """

    song_id = f"{artist} - {title}.txt"
    existing = collection.get(ids=[song_id])

    if existing['ids']:
        if verbose: print("Song found in collection.")
        return existing['documents'][0]

    if verbose: print("Song not found. Fetching dynamically from Genius API...")

    # generate song context
    song_context = generate_song_context(artist, title)
    if song_context:
        embedding = model.encode(song_context).tolist()
        collection.add(
            ids=[song_id],
            embeddings=[embedding],
            documents=[song_context],
            metadatas=[{"artists": artist, "track_name": title}]
        )
        if verbose: print(f"Embedding added to corpus for: '{artist} - {title}'.")
        # TODO: add song to corpus_metadata.csv if needed
        return song_context
    else:
        if verbose: print( f"Genius does not have '{title}' by '{artist}'. Falling back to numeric filtering.")
        return None


if __name__ == "__main__":
    query = "calm instrumental piano music"
    documents, metadata = find_semantically_similar_songs(query, top_k=5)

    print("Retrieved Top Songs:")
    for doc, meta in zip(documents, metadata):
        print(f"- {meta['artists']} - {meta['track_name']} ({meta['genre']})")

    # Retrieve on-the-fly:
    artists = "Coldplay"
    track_name = "Adventure of a Lifetime"

    doc = get_or_create_song_embedding(artists, track_name)
    if doc:
        print(f"Retrieved song : {track_name}")

