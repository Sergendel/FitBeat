# 🎧 FitBeat: LLM-Powered Music Recommendation Agent

**Author:** Sergey Gendel

---

## 🚀 Project Overview

**FitBeat** — LLM-powered Music Recommendation Agent

FitBeat transforms your emotional or situational descriptions 
(e.g., "music for intense gym training" or "playlist for a child's birthday party")
into personalized MP3 playlists.

## 📌 How It Works (Quick Overview)

### 1. Initial Filtering (Numeric Analysis)

- Converts user prompts into numeric audio features (tempo, energy, danceability, etc.).
- Filters tracks from a large Kaggle [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset), containing over 114,000 annotated tracks.

### 2.  Semantic Refinement (Lyrics & Context)

- Retrieves lyrics and descriptions from [Genius](https://genius.com/)
- Uses semantic analysis (RAG) to rank tracks according to emotional and contextual relevance.

### 3. Final Track Retrieval and Conversion

- Downloads selected tracks from YouTube.
- Converts tracks to MP3 for easy listening.
---

## 🚀 **Agent's Internal Workflow (Pipeline)**

FitBeat explicitly operates according to the following structured pipeline:

### 1. **Memory Initialization (User-Controlled, Optional)**

At the start of each session, the agent explicitly asks if the user wants to use previously stored conversation context (memory):

```
⚠️ Do you want to clear previous memory and start a new unrelated task? (y/n):
```

- If **"n"**, the agent explicitly combines previous summarized prompts with the current prompt, enhancing context.
- If **"y"**, memory explicitly resets, starting fresh contextually.

### 2. **Action Plan Creation (LLM-based, Textual)**

FitBeat explicitly analyzes the (combined or standalone) user prompt to generate a clear, human-readable textual action plan outlining necessary steps.

### 3. **Action Plan Structuring (LLM-based, Structured JSON)**

Translates the textual action plan explicitly into structured, machine-readable JSON actions, selected from the following available actions:

- **Analyze:** Convert user's prompt into numeric audio parameters.
- **Filter:** Filter tracks from the dataset based on numeric audio parameters.
- **Rank:** Semantic ranking of candidate tracks using lyrics and descriptions (RAG-based).
- **Retrieve_and_Convert:** Download selected tracks from YouTube and convert to MP3.
- **Summarize:** Generate and present a concise summary of the final playlist.

### 4. **Execute Actions (Agent Tools)**

Executes each structured action explicitly using dedicated agent tools (listed in the tools section).



## **Agent Tools (Operational Components)**

FitBeat utilizes explicit, concrete operational tools to execute the generated action plan:

- **Filter Tracks (Numeric Filtering):**  
  Filters tracks from the Kaggle dataset using numeric audio parameters derived by the LLM.

- **Semantic Ranking (RAG, LLM-based):**  
  Ranks candidate tracks based on semantic relevance by analyzing lyrics and descriptions retrieved from Genius.com, using the LLM through (RAG).

- **Retrieve and Convert:**  
  Downloads refined tracks from YouTube (`yt-dlp`) and converts them to MP3 (`ffmpeg`).

- **Summarize Playlist:**  
  Provides a clear, explicit summary of the final recommended playlist.

> **The agent may selectively apply some (or all) of these tools, based explicitly on the action plan it autonomously generates.**


## 🧠 **Agent Memory (Persistent Context Management)**

FitBeat features persistent memory, enabling context preservation across multiple interactions and separate runs to refine recommendations based on previous user requests.

### 📌 **How It Works:**

- **Persistent Storage (LLM-based Summarization):**
  User prompts are summarized by the LLM (GPT-3.5 Turbo), and these concise summaries (rather than full prompts) are stored in a dedicated file (`conversation_memory.json`). 
  This ensures relevant context is maintained efficiently and clearly.

- **User-Controlled Memory:**
  At each session's start, FitBeat asks explicitly:
  ```
  ⚠️ Do you want to clear previous memory and start a new unrelated task? (y/n):
  ```
  - Answering **"y"** explicitly clears memory and starts fresh.
  - Answering **"n"** explicitly retains existing summarized memory.

## 🧪 Testing and CI/CD

FitBeat explicitly includes basic unit tests to ensure robustness and correctness of core functionalities. Tests are implemented explicitly using **`pytest`**.

### 📌 Running Tests Locally

Ensure dependencies are explicitly installed:

```bash
pip install -r requirements.txt
```

Run tests explicitly with the command:

```bash
pytest tests/
```

### 📌 Continuous Integration (CI)

FitBeat explicitly utilizes **GitHub Actions** to automatically run unit tests upon each push or pull request. This ensures continuous code quality and early detection of issues.

- View CI workflows explicitly under your repository's **Actions** tab.


##  **FitBeat Execution Examples**

These examples explicitly demonstrate how FitBeat autonomously creates an action plan and selectively chooses tools based on the user's prompt.

---

### **Examples Without Memory**

####  **Scenario 1:** `Analyze → Filter → Retrieve_and_Convert → Summarize`

- **Prompt:** `"music for romantic date"`
- **Actions:**
  1. Analyze prompt into numeric audio parameters.
  2. Filter tracks numerically.
  3. Retrieve tracks from YouTube and convert to MP3.
  4. Summarize playlist.

####  **Scenario 2:** `Analyze → Filter → Rank → Retrieve_and_Convert → Summarize`

- **Prompt:** `"playlist for romantic date, tracks with deeply meaningful and romantic lyrics"`
- **Actions:**
  1. Analyze prompt into numeric audio parameters.
  2. Filter tracks numerically.
  3. Rank tracks semantically (using lyrics/context via RAG).
  4. Retrieve tracks from YouTube and convert to MP3.
  5. Summarize playlist.

#### **Scenario 3:** `Retrieve_and_Convert → Summarize`

- **Prompt:**
  ```
  I already have a list of specific songs:
  - The Weeknd - Blinding Lights
  - Eminem - Lose Yourself
  - Coldplay - Adventure of a Lifetime

  Just download these exact songs from YouTube, convert them to mp3,
  and summarize the resulting playlist. No additional analysis or recommendations are needed.
  ```
- **Actions:**
  1. Retrieve provided tracks from YouTube and convert to MP3.
  2. Summarize playlist.

---

###  **Example With Memory (Persistent Context)**

Demonstrates memory across sequential interactions:

- **Initial Prompt:** `"playlist for romantic date, tracks with deeply meaningful and romantic lyrics"`
- **Next Prompt (with memory):** `"I forgot to say that we would probably dance during our date"`

**Behavior:**
- FitBeat explicitly considers both prompts, refining recommendations based on cumulative context.
- Agent autonomously decides which tools are required given the additional context.

---

These scenarios clearly show FitBeat's flexible, context-aware decision-making and dynamic tool selection capability.

## 📂 **Project Structure**

```
FitBeat/
├── audio/                     # MP3 playlists generated here
├── bin/                       # External binaries (ffmpeg)
├── corpus/                    # Lyrics and descriptions corpus
├── data/                      # Datasets (Kaggle)
├── EDA/                       # Exploratory data analysis scripts
├── extract/                   # Data extraction utilities
├── src/                       # Core project scripts
│   ├── orchestrator.py        # Main orchestration logic
│   ├── memory_manager.py      # Persistent memory management
│   ├── prompt_engineer.py     # Prompt construction logic
│   ├── llm_executor.py        # LLM interaction handling
│   ├── filtering_utils.py     # Numeric track filtering utilities
│   ├── RAG_semantic_refiner.py# Semantic ranking via RAG
│   ├── track_downloader.py    # YouTube track retrieval/conversion
│   └── playlist_summary.py    # Playlist summarization
├── .env                       # Environment variables (OpenAI API, Genius API keys)
└── README.md                  # Project documentation
```

---

## 🚀 **How to Run**

### ✅ **1. Clone the Repository**
```bash
git clone https://github.com/your-repo/FitBeat.git
cd FitBeat
```

### ✅ **2. Install Requirements**
```bash
pip install -r requirements.txt
```

### ✅ **3. Set Up Environment Variables**

Create a `.env` file in the root directory with your API keys:

```bash
OPENAI_API_KEY="your-openai-api-key"
GENIUS_API_KEY='4wrpRJc6wtzjNstx1LmnTDreTZ_khfbCadjQpMq2WXjiEnb1OmGTaWhk6EXfL-Ad'
```

### ✅ **4. Run the Application**

Execute the orchestrator script with your desired prompt:

```bash
python src/orchestrator.py
```

The application will ask explicitly if you wish to continue using existing memory or clear it:

```
Do you want to clear previous memory and start a new unrelated task? (y/n):
```

- Answering `y` clears previous memory.
- Answering `n` retains memory across interactions.

---
## 👤 **Author**

This project (**FitBeat**) was explicitly created and developed by **Sergey Gendel**.

---

## ⚠️ **Legal Disclaimer (YouTube Downloads)**

Downloading content directly from YouTube may violate YouTube's [Terms of Service](https://www.youtube.com/t/terms), specifically regarding unauthorized downloading and distribution.  
**FitBeat** is provided for demonstration, educational, and personal use only.  
Ensure you have explicit permission or rights to any content downloaded using this tool. **The author is not responsible for misuse or violations of applicable laws or terms of service.**