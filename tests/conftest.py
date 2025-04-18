import sys
from pathlib import Path

# explicitly add the root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
