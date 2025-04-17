import json
from pathlib import Path

MEMORY_FILE = Path("conversation_memory.json")

def save_memory_to_file(memory_summary):
    with open(MEMORY_FILE, "w", encoding='utf-8') as f:
        json.dump({"summary": memory_summary}, f)

def load_memory_from_file():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding='utf-8') as f:
            data = json.load(f)
            return data.get("summary", "")
    else:
        return None



def confirm_clear_memory():
    """
    Prompts user to confirm if they start a new unrelated task.
    Returns True if memory should be cleared.
    """
    response = input("\n*****   Do you want to clear previous memory and start a new unrelated task? (y/n): ").strip().lower()
    return response in ("y", "yes")