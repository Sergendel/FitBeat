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

        top_k (int, optional, default=5):
            The number of similar songs to return.

    Returns:
        tuple:
            - documents (list[str]):
                Lyrics and descriptions of the similar songs.
            - metadatas (list[dict]):
                Associated metadata (artist, title, genre) for each song.

    Example:
         documents, metadata = find_semantically_similar_songs("calm piano music", top_k=3)
    """

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0], results['metadatas'][0]



def get_or_create_song_embedding(artist: object, title: object) -> object:
    """
        Get the embedding and lyrics for a given song from the local ChromaDB corpus.
        If the song isn't available locally, dynamically fetch lyrics from Genius API, generate the embedding,
        and add it to the corpus.

        Parameters:
            artist (str):
                Artist name associated with the song.
            title (str):
                Song title.

        Returns:
            str or None:
                The lyrics of the song if found or fetched, else e None.
        """
    
    song_id = f"{artist} - {title}.txt"
    existing = collection.get(ids=[song_id])

    if existing['ids']:
        print("Song found in corpus.")
        return existing['documents'][0]

    print("Song not found. Fetching dynamically from Genius API...")
    song = genius.search_song(title, artist)

    # if song already in embedding:
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

    # On-the-fly embedding:
    # TODO: add the song to config.CORPUS_METADATA_PATH csv file
    else:
        print(f"Genius doesn't have '{title}' by {artist}. Falling back to numeric filtering.")
        return None

if __name__ == "__main__":
    query = "calm instrumental piano music"
    documents, metadata = find_semantically_similar_songs(query, top_k=5)

    print("Retrieved Top Songs:")
    for doc, meta in zip(documents, metadata):
        print(f"- {meta['artist']} - {meta['title']} ({meta['genre']})")

    # Retrieve on-the-fly:
    artist = "Coldplay"
    title = "Adventure of a Lifetime"

    doc = get_or_create_song_embedding(artist, title)
    if doc:
        print(f"Retrieved song : {title}")

