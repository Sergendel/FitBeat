# 🎧 FitBeat: LLM-Powered Music Recommendation Agent

**Author:** Sergey Gendel

---

## 🚀 Project Overview

**FitBeat** is an LLM-powered music recommendation agent.

FitBeat takes user prompts describing emotional or situational contexts
 (e.g., "music for intense gym training" or "playlist for a child's birthday party") 
 and generates playlists matching the user's requests.

## 📌 How it Works

### 1. Initial Track Filtering

The agent first translates user prompts into numeric audio parameters, such as tempo, energy, danceability, etc. 
It then retrieves suitable tracks from a large Kaggle dataset (`dataset.csv`),
 containing approximately 114,000 tracks, each annotated with detailed numeric audio features
  (danceability, energy, loudness, tempo, etc.). An initial list of candidate tracks is created after this step.

### 2. Semantic Refinement using RAG (Retrieval-Augmented Generation)

FitBeat refines and ranks these candidate tracks using RAG. 
It retrieves track descriptions and lyrics from the Genius website, then uses semantic analysis to determine 
how well each track matches the user's request emotionally and contextually. 
After this refinement, tracks are re-ranked according to semantic relevance.

### 3. Final Track Retrieval and Conversion

Finally, FitBeat downloads the highest-ranked tracks from YouTube and converts them into MP3 files for convenient listening.

---

## 🛠️ Tools & Resources Used

- **OpenAI GPT API (via LangChain)**: Dynamic planning, numeric parameter extraction, semantic ranking
- **Kaggle Dataset**: Numeric audio feature filtering
- **YouTube (via yt-dlp & ffmpeg)**: Track downloading and conversion
- **Genius API**: Semantic context retrieval for RAG

---

## 🔍 Project Structure

```
FitBeat
├── audio/
│   └── downloaded_tracks/
├── bin/
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
├── corpus/
│   ├── embeddings/
│   └── genius_corpus/
├── data/
│   └── kaggle/
│       └── dataset.csv
├── src/
│   ├── filtering_logic.py
│   ├── llm_executor.py
│   ├── orchestrator.py
│   ├── output_parser.py
│   ├── prompt_engineer.py
│   └── track_downloader.py
├── config.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 📦 Dependencies:
```bash
pip install -r requirements.txt
```

### 🔑 API Keys:
- Create a `.env` file with the following:
```env
OPENAI_API_KEY='your_openai_api_key'
GENIUS_API_KEY='your_genius_api_key'
```

### 🖥️ Running the Agent:

Run the orchestrator:
```bash
python src/orchestrator.py
```

Modify the `orchestrator.py` main section with desired user prompts to explicitly run different scenarios.

---

## 📝 Examples of Usage

### 📌 Example 1: Emotional/Situational Prompt
```python
user_prompt = "music for romantic date"
orchestrator.run_planning_agent(user_prompt, num_tracks=20)
```

### 📌 Example 2: Direct Download Request
```python
prompt_simple = (
    "I already have a list of specific songs:\n"
    "- The Weeknd - Blinding Lights\n"
    "- Eminem - Lose Yourself\n"
    "- Coldplay - Adventure of a Lifetime\n\n"
    "Just download these exact songs from YouTube, convert them to mp3, "
    "and summarize the resulting playlist. No additional analysis or recommendations are needed."
)
orchestrator.run_planning_agent(prompt_simple, num_tracks=3)
```

---

## 💡 Future Improvements (Optional)
- Enhanced memory/contextual planning across multiple sessions
- Further optimization of semantic refinement
- Additional external tools for broader capabilities (e.g., live web search)


## 🚨 Troubleshooting
- Verify `.env` file for correct API keys
- Ensure `ffmpeg` binaries are correctly placed in `bin`

---

