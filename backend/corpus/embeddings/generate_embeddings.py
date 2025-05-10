import os
import sys
from pathlib import Path

import chromadb
import pandas as pd
from openai import OpenAI

from backend import config

# Adjust sys.path explicitly to import project-specific configurations
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Initialize OpenAI client with API key explicitly from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load corpus metadata (list of songs with associated details)
metadata_df = pd.read_csv(config.CORPUS_METADATA_PATH)

# Initialize ChromaDB client and collection for storing embeddings
if os.getenv("GITHUB_ACTIONS") == "true":
    # CI environment: in-memory ephemeral storage
    chroma_client = chromadb.Client()
    collection_name = "genius_embeddings_ci"

    collection = chroma_client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine", "hnsw:num_threads": 1}
    )
else:
    # Production environment: persistent storage
    chroma_client = chromadb.PersistentClient(path=str(config.EMBEDDINGS_DB_PATH))
    collection_name = "genius_embeddings"

    collection = chroma_client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )


# Iterate over corpus metadata and generate embeddings for each song context
for idx, row in metadata_df.iterrows():
    song_path = config.CORPUS_DIR / row["filename"]

    try:
        # Read comprehensive song context from file
        with open(song_path, "r", encoding="utf-8") as file:
            song_context = file.read()

        # Generate embedding vector explicitly using OpenAI's embeddings API
        response = client.embeddings.create(
            input=song_context, model="text-embedding-ada-002"
        )

        embedding = response.data[0].embedding

        # Explicitly add embedding to ChromaDB along with clearly defined metadata
        collection.add(
            ids=[row["filename"]],
            embeddings=[embedding],
            documents=[song_context],
            metadatas=[
                {
                    "artists": row["artist"],
                    "track_name": row["track_name"],
                    "genre": row["genre"],
                }
            ],
        )

        print(f"Embedding generated and stored for: {row['filename']}")

    except Exception as e:
        print(f"Error processing '{row['filename']}': {e}")

print("All embeddings generated and stored successfully!")
