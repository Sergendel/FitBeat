import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import lyricsgenius
import os
from dotenv import load_dotenv
from src.song_utils import generate_song_context
from chromadb.errors import NotFoundError


# Load environment
load_dotenv()

# Import config
sys.path.append(str(Path(__file__).resolve().parents[2]))
import config

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def set_collection():

    # set collection
    if os.getenv("GITHUB_ACTIONS") == "true":
        # CI environment: in-memory ephemeral storage
        chroma_client = chromadb.Client()
        collection_name = "genius_embeddings_ci"
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine",
                "hnsw:num_threads": 1
            }
        )
    else:
        # Set ChromaDB collection
        collection_name = "genius_embeddings"
        chroma_client = chromadb.PersistentClient(path=str(config.EMBEDDINGS_DB_PATH))
        try:
            collection = chroma_client.get_collection(name=collection_name)
        except NotFoundError:
            raise RuntimeError(f"Collection '{collection_name}' does not exist. "
                               f"Ensure it is created during initialization.")
    return collection

# find similar tracks (semantic) to user provided track (name and artist)
# TODO: PREPARATION FOR "Semantic_Search" ACTION,  MEANWHILE NOT IN USE  !!!
def find_semantically_similar_songs(query, collection , top_k=5):
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
            - metadatas (list[dict]): Associated metadata (artist, track_name, genre) for each song.

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


def get_or_create_song_embedding(artist: str, track_name: str, collection) -> object:
    """
        Get the embedding and context for a given song from the local ChromaDB corpus.
        If the song isn't available locally, dynamically fetch context from Genius API, generate the embedding,
        and add it to the corpus.

        Parameters:
            artist (str): Artist name associated with the song.
            track_name (str): Song track_name.

        Returns:
            str or None: The context of the song if found or fetched, else e None.
        """
    verbose = config.VERBOSE
    song_id = f"{artist} - {track_name}.txt"
    existing = collection.get(ids=[song_id])

    if existing['ids']:
        if verbose: print("Song found in collection.")
        return existing['documents'][0]

    if verbose: print("Song not found. Fetching dynamically from Genius API...")

    # generate song context
    song_context = generate_song_context(artist, track_name)
    if song_context:
        embedding = model.encode(song_context).tolist()
        collection.add(
            ids=[song_id],
            embeddings=[embedding],
            documents=[song_context],
            metadatas=[{"artists": artist, "track_name": track_name}]
        )
        if verbose: print(f"Embedding added to corpus for: '{artist} - {track_name}'.")
        # TODO: add song to corpus_metadata.csv if needed
        return song_context
    else:
        if verbose: print( f"Genius does not have '{track_name}' by '{artist}'. Falling back to numeric filtering.")
        return None


if __name__ == "__main__":
    query = "calm instrumental piano music"
    collection_for_test = set_collection()
    documents, metadata = find_semantically_similar_songs(query, collection = collection_for_test, top_k=5)

    print("Retrieved Top Songs:")
    for doc, meta in zip(documents, metadata):
        print(f"- {meta['artists']} - {meta['track_name']} ({meta['genre']})")

    # Retrieve on-the-fly:
    artists = "Coldplay"
    track_name = "Adventure of a Lifetime"

    doc = get_or_create_song_embedding(artists, track_name, collection_for_test)
    if doc:
        print(f"Retrieved song : {track_name}")

