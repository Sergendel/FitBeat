import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
import pandas as pd

# Adjust sys.path explicitly to import project-specific configurations
sys.path.append(str(Path(__file__).resolve().parents[2]))
import config

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load corpus metadata (list of songs with associated details)
metadata_df = pd.read_csv(config.CORPUS_METADATA_PATH)

# Initialize ChromaDB client and collection for storing embeddings
chroma_client = chromadb.PersistentClient(path=str(config.EMBEDDINGS_DB_PATH))
collection = chroma_client.get_or_create_collection(name="genius_embeddings")

# Iterate over corpus metadata and generate embeddings for each song context
for idx, row in metadata_df.iterrows():
    song_path = config.CORPUS_DIR / row['filename']

    try:
        # Read comprehensive song context from file
        with open(song_path, 'r', encoding='utf-8') as file:
            song_context = file.read()

        # Generate embedding vector using the pre-trained model
        embedding = model.encode(song_context).tolist()

        # Explicitly add embedding to ChromaDB along with clearly defined metadata
        collection.add(
            ids=[row['filename']],
            embeddings=[embedding],
            documents=[song_context],
            metadatas=[{
                "artists": row["artist"],        # Explicitly corrected and consistent
                "track_name": row["title"],      # Explicitly corrected and consistent
                "genre": row["genre"]
            }]
        )

        print(f"Embedding generated and stored for: {row['filename']}")

    except Exception as e:
        print(f"Error processing '{row['filename']}': {e}")

print("All embeddings generated and stored successfully!")
