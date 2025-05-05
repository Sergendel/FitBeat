from pathlib import Path

FRONTEND_MODE = False

# Project root path
PROJECT_ROOT = Path(__file__).resolve().parent


# data
FILE_PATH = PROJECT_ROOT / "data_management" / "data" / "kaggle" / "dataset.csv"

# Paths
FFMPEG_PATH = PROJECT_ROOT / "resources" / "bin" / "ffmpeg.exe"
TRACKS_DIR = PROJECT_ROOT / "output" / "audio" / "downloaded_tracks"
PLAYLISTS_DIR = PROJECT_ROOT / "output" / "playlists"


# Corpus and Embedding Paths
CORPUS_DIR = PROJECT_ROOT / "corpus" / "genius_corpus"
CORPUS_METADATA_PATH = PROJECT_ROOT / "corpus" / "corpus_metadata.csv"
EMBEDDINGS_DIR = PROJECT_ROOT / "corpus" / "embeddings"
EMBEDDINGS_DB_PATH = PROJECT_ROOT / "corpus" / "embeddings" / "genius_corpus_db"

# memory file
MEMORY_FILE_PATH = PROJECT_ROOT / "core" / "conversation_memory.json"

# verbose
VERBOSE = False
