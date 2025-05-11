import os
import shutil
import sys
import time
from pathlib import Path

import chromadb
from chromadb.errors import NotFoundError
from dotenv import load_dotenv
from openai import OpenAI

from backend import config
from backend.core.song_utils import SongContextGenerator

# Load environment
load_dotenv()

# Import config
sys.path.append(str(Path(__file__).resolve().parents[2]))


def running_on_lambda():
    return "AWS_LAMBDA_FUNCTION_NAME" in os.environ


class SemanticRetrieval:
    def __init__(self, open_ai_key=None, genius_api_key=None):
        self.client = OpenAI(api_key=open_ai_key)
        self.collection = self.set_collection()
        self.SongContextGenerator = SongContextGenerator(genius_api_key=genius_api_key)

    def set_collection(self):
        collection_name = "genius_embeddings"

        if running_on_lambda():
            lambda_db_source = "/var/task/backend/corpus/embeddings/genius_corpus_db"
            lambda_db_destination = "/tmp/genius_corpus_db"

            # Copy DB to /tmp if it doesn't exist yet in this Lambda invocation
            if not os.path.exists(lambda_db_destination):
                shutil.copytree(lambda_db_source, lambda_db_destination)

            chroma_client = chromadb.PersistentClient(path=lambda_db_destination)

        elif os.getenv("GITHUB_ACTIONS") == "true":
            chroma_client = chromadb.Client()
            collection_name = "genius_embeddings_ci"

        else:
            chroma_client = chromadb.PersistentClient(
                path=str(config.EMBEDDINGS_DB_PATH)
            )

        try:
            collection = chroma_client.get_collection(name=collection_name)
        except NotFoundError:
            raise RuntimeError(
                f"Collection '{collection_name}' does not exist. "
                "Ensure it is created during initialization."
            )
        return collection

    def get_openai_embedding(self, text: str):
        response = self.client.embeddings.create(
            input=text, model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def find_semantically_similar_songs(self, query: str, top_k: int = 5):
        query_embedding = self.get_openai_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=top_k
        )
        return results["documents"][0], results["metadatas"][0]

    def embed_user_prompt(self, user_prompt: str):
        return self.get_openai_embedding(user_prompt)

    def get_or_create_song_embedding(self, artist: str, track_name: str):
        verbose = config.VERBOSE
        song_id = f"{artist} - {track_name}.txt"
        existing = self.collection.get(ids=[song_id])

        if existing["ids"]:
            if verbose:
                print("Song found in collection.")
            return existing["documents"][0]

        if verbose:
            print("Song not found. Fetching dynamically from Genius API...")

        song_context = self.SongContextGenerator.generate_song_context(
            artist, track_name
        )
        if song_context:
            embedding = self.get_openai_embedding(song_context)
            self.collection.add(
                ids=[song_id],
                embeddings=[embedding],
                documents=[song_context],
                metadatas=[{"artists": artist, "track_name": track_name}],
            )
            delay_sec = 2
            time.sleep(delay_sec)
            if verbose:
                print(f"Embedding added to corpus for: '{artist} - {track_name}'.")
            return song_context
        else:
            if verbose:
                print(
                    f"Genius does not have '{track_name}' by '{artist}'."
                    f" Falling back to numeric filtering."
                )
            return None


if __name__ == "__main__":
    semantic_retrieval = SemanticRetrieval(
        open_ai_key=os.getenv("OPENAI_API_KEY"),
        genius_api_key=os.getenv("GENIUS_API_KEY"),
    )

    query = "calm instrumental piano music"
    documents, metadata = semantic_retrieval.find_semantically_similar_songs(
        query, top_k=5
    )

    print("Retrieved Top Songs:")
    for doc, meta in zip(documents, metadata):
        print(
            f"- {meta['artists']} - {meta['track_name']} ({meta.get('genre', 'N/A')})"
        )

    artists = "Coldplay"
    track_name = "Adventure of a Lifetime"

    doc = semantic_retrieval.get_or_create_song_embedding(artists, track_name)
    if doc:
        print(f"Retrieved song : {track_name}")
