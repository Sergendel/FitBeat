from pathlib import Path

# Project root path
PROJECT_ROOT = Path(__file__).resolve().parent


#data
FILE_PATH = PROJECT_ROOT / 'data' / 'kaggle' / 'dataset.csv'

# Paths
FFMPEG_PATH = PROJECT_ROOT / 'bin' / 'ffmpeg.exe'
TRACKS_DIR = PROJECT_ROOT / 'audio' / 'downloaded_tracks'

# Corpus and Embedding Paths
CORPUS_DIR = PROJECT_ROOT / "corpus" / "genius_corpus"
CORPUS_METADATA_PATH = PROJECT_ROOT / "corpus" / "corpus_metadata.csv"
EMBEDDINGS_DIR = PROJECT_ROOT / "corpus" / "embeddings"
EMBEDDINGS_DB_PATH = PROJECT_ROOT / "corpus" / "embeddings" / "genius_corpus_db"