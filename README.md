# 🎶 FitBeat: LLM-Based Music Recommendation Agent

## 🚀 Project Overview

**FitBeat** is an intelligent music recommendation agent powered by an LLM (Large Language Model) designed explicitly for context-driven music selection. Users describe emotional or situational contexts (e.g., \"energetic music for gym workout\"), and FitBeat automatically translates these descriptions into detailed song parameters such as tempo, energy, danceability, and retrieves suitable songs from a dataset. It then downloads and converts these tracks from YouTube into mp3 format.

The goal is to demonstrate robust ML engineering skills, particularly in developing LLM-driven autonomous agents.

---

## ⚙️ Key Functionalities

- **Context Interpretation via LLM (OpenAI API)**
- **Dataset Filtering based on audio parameters**
- **Automatic song downloading (yt-dlp) and conversion to mp3 (ffmpeg)**
- **Structured and modular Python codebase**

---

## 🗂️ Project Structure

```
.
├── audio
├── bin
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
├── config.py
├── corpus
│   ├── create_basic_corpus.py
│   └── genius_corpus_simple.py
├── data
│   └── kaggle
│       ├── check_genres.py
│       ├── dataset.csv
│       └── download_Kaggle_data.py
├── EDA
│   └── kaggle_eda.py
├── extract
│   ├── extract_base.py
│   └── extract_file.py
├── project_setup and commands.txt
├── src
│   ├── explicit_filtering_logic.py
│   ├── llm_executor.py
│   ├── orchestrator.py
│   ├── output_parser.py
│   ├── prompt_engineer.py
│   └── track_downloader.py
├── structure.txt
└── __pycache__
    └── config.cpython-311.pyc
```

---

## 🛠️ How It Works

1. **LLM Prompt Engineering**: Interprets the user's description and converts it into numeric audio features.
2. **Dataset Filtering**: Retrieves matching tracks from a Kaggle dataset based on these features.
3. **Audio Downloading and Conversion**: Downloads selected tracks from YouTube and converts them into mp3 format.

---

## 🔧 Setup & Installation

### Requirements

- Python 3.11
- OpenAI API key and Genius API key

### Installation

```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory of the project with the following content:

```env
OPENAI_API_KEY='your open ai api key'
GENIUS_API_KEY='your genius ai api key'
```

### Usage

Run the orchestrator:

```bash
python src/orchestrator.py
```

### Example

```python
user_prompt = \"music tracks for dancing party for 50+ years old\"
orchestrator.run_agent(user_prompt, num_tracks=10)
```

---

## 🎯 Future Enhancements

- ✅ **Explicit LLM-driven planning** (in progress)
- ✅ **Retrieval-Augmented Generation (RAG)** for improved recommendation quality (planned)
- ✅ Comprehensive **Unit Tests** and robust error handling (planned)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

## 🙌 Acknowledgments

- OpenAI API
- Kaggle Dataset
- `yt-dlp` and `ffmpeg`

---

Developed by Sergey Gendel. © 2024 FitBeat Project.

