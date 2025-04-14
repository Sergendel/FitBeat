import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
import pandas as pd

# Adjust sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))
import config

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load metadata
df = pd.read_csv(config.CORPUS_METADATA_PATH)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=str(config.EMBEDDINGS_DB_PATH))
collection = chroma_client.get_or_create_collection(name="genius_embeddings")

# Generate embeddings for each song
for idx, row in df.iterrows():
    filepath = config.CORPUS_DIR / row['filename']

    with open(filepath, 'r', encoding='utf-8') as file:
        song_text = file.read()

    embedding = model.encode(song_text).tolist()

    collection.add(
        ids=[row['filename']],
        embeddings=[embedding],
        documents=[song_text],
        metadatas=[{
            "artist": row["artist"],
            "title": row["title"],
            "genre": row["genre"]
        }]
    )

    print(f"Embedding generated for: {row['filename']}")

print("All embeddings generated and stored successfully!")
