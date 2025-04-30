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

### 2. Hybrid Semantic Ranking (Embeddings & RAG)

- Retrieves track contexts (lyrics and descriptions) from [Genius](https://genius.com/)
- Initially ranks candidate tracks based on embedding similarity between the user's prompt embedding and the tracks' context embeddings, then selects the top-k candidates.
- Performs further semantic refinement (RAG-based) using LLM-based semantic analysis to finalize rankings based on emotional and contextual relevance.

### 3. Final Track Retrieval and Conversion

- Downloads selected tracks from YouTube.
- Converts tracks to MP3 for easy listening.
---

## 🚀 **Agent's Internal Workflow (Pipeline)**

FitBeat operates according to the following structured pipeline:

### 1. **Memory Initialization (User-Controlled, Optional)**

At the start of each session, the agent asks if the user wants to use previously stored conversation context (memory):

```
⚠️ Do you want to clear previous memory and start a new unrelated task? (y/n):
```

- If **"n"**, the agent combines previous summarized prompts with the current prompt, enhancing context.
- If **"y"**, memory resets, starting fresh contextually.

### 2. **Action Plan Creation (LLM-based, Textual)**

FitBeat analyzes the (combined or standalone) user prompt to generate a clear, human-readable textual action plan outlining necessary steps.

### 3. **Action Plan Structuring (LLM-based, Structured JSON)**

Translates the textual action plan into structured, machine-readable JSON actions, selected from the following available actions:

- **Analyze:** Convert user's prompt into numeric audio parameters.
- **Filter:** Filter tracks from the dataset based on numeric audio parameters.
- **Refine:**  Hybrid Semantic Ranking (Embeddings & RAG) of tracks.
- **Retrieve_and_Convert:** Download selected tracks from YouTube and convert to MP3.
- **Summarize:** Generate and present a concise summary of the final playlist.

### 4. **Execute Actions (Agent Tools)**

Executes each structured action using dedicated agent tools (listed in the tools section).



## **Agent Tools (Operational Components)**

FitBeat utilizes explicit, concrete operational tools to execute the generated action plan:

- **Filter Tracks (Numeric Filtering):**  
  Filters tracks from the Kaggle dataset using numeric audio parameters derived by the LLM.

- **Hybrid Semantic Ranking (Embeddings & RAG):**  
  Ranks candidate tracks based on semantic relevance by analyzing lyrics and descriptions retrieved from Genius.com, using the embeddings similaruty and LLM through (RAG).

- **Retrieve and Convert:**  
  Downloads refined tracks from YouTube (`yt-dlp`) and converts them to MP3 (`ffmpeg`).

- **Summarize Playlist:**  
  Provides a summary of the final recommended playlist.

> **The agent may selectively apply some (or all) of these tools, based on the action plan it autonomously generates.**


## 🧠 **Agent Memory (Persistent Context Management)**

FitBeat features persistent memory, enabling context preservation across multiple interactions and separate runs to refine recommendations based on previous user requests.

### 📌 **How It Works:**

- **Persistent Storage (LLM-based Summarization):**
  User prompts are summarized by the LLM (GPT-3.5 Turbo), and these concise summaries (rather than full prompts) are stored in a dedicated file (`conversation_memory.json`). 
  This ensures relevant context is maintained efficiently and clearly.

- **User-Controlled Memory:**
  At each session's start, FitBeat asks:
  ```
  ⚠️ Do you want to clear previous memory and start a new unrelated task? (y/n):
  ```
  - Answering **"y"** clears memory and starts fresh.
  - Answering **"n"** retains existing summarized memory.

## 🧪 Testing and CI/CD

FitBeat includes basic unit tests to ensure robustness and correctness of core functionalities. Tests are implemented using **`pytest`**.

### 📌 Running Tests Locally

Ensure dependencies are installed:

```bash
pip install -r requirements.txt
```

Run tests with the command:

```bash
pytest tests/
```

## 📌 Continuous Integration (CI)

FitBeat utilizes **GitHub Actions** to ensure code reliability, maintainability, and adherence to best practices.
Every push or pull request to the `main` branch automatically triggers the following checks and tests:

### ✅ Automated Tests

- **Unit Tests**  
  Fast, isolated tests verifying individual components. These tests run against ChromaDB’s in-memory storage to maximize speed and isolation.

- **End-to-End (E2E) Tests**  
  Comprehensive integration tests covering the full workflow of the application, ensuring FitBeat works seamlessly from the user's perspective.

### 🧹 Code Quality & Style Checks

- **Flake8 Linting**  
  Enforces adherence to [PEP8](https://www.python.org/dev/peps/pep-0008/) guidelines and detects common Python anti-patterns. Configurations are defined in `pyproject.toml`.

- **Black & Isort Formatting**  
  Ensures consistent code style (`black`) and correct import ordering (`isort`), configured via `pyproject.toml`.

### 🛠️ Testing Environments

- **Testing Environment** (`GITHUB_ACTIONS=true`)  
  Uses in-memory databases and mock services to provide maximum isolation and performance during continuous integration runs.

- **Production Environment**  
  Clearly separated from testing configurations, using persistent storage and secure settings for real-world deployment.


##  **FitBeat Execution Examples**

These examples demonstrate how FitBeat autonomously creates an action plan and selectively chooses tools based on the user's prompt.

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
- FitBeat considers both prompts, refining recommendations based on cumulative context.
- Agent autonomously decides which tools are required given the additional context.

---

These scenarios clearly show FitBeat's flexible, context-aware decision-making and dynamic tool selection capability.

## 📂 **Project Structure**

```
# 📂 FitBeat Project Structure

```
FitBeat/
├── .env.example
├── .gitignore
├── config.py
├── README.md
├── .github/
├── bin/
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
├── corpus/
│   ├── corpus_metadata.csv
│   ├── create_basic_corpus.py
│   ├── genius_corpus_simple.py
│   ├── __init__.py
│   └── embeddings/
│       ├── generate_embeddings.py
│       ├── semantic_retrieval.py
│       ├── __init__.py
│       └── genius_corpus_db/
│           ├── chroma.sqlite3
│           └── eb90c47c-e55c-4bf5-84b4-517c051c9c83/
│               ├── data_level0.bin
│               ├── header.bin
│               ├── length.bin
│               └── link_lists.bin
├── data/
│   └── kaggle/
│       ├── check_genres.py
│       ├── dataset.csv
│       └── download_Kaggle_data.py
├── eda/
│   └── kaggle_eda.py
├── extract/
│   ├── extract_base.py
│   ├── extract_file.py
│   └── __init__.py
├── src/
│   ├── dataset_genres.py
│   ├── filtering_utils.py
│   ├── llm_executor.py
│   ├── memory_manager.py
│   ├── orchestrator.py
│   ├── output_parser.py
│   ├── playlist_summary.py
│   ├── prompt_engineer.py
│   ├── rag_semantic_refiner.py
│   ├── song_utils.py
│   ├── track_downloader.py
│   ├── user_prompt_utils.py
│   └── __init__.py
└── tests/
    ├── conftest.py
    ├── __init__.py
    ├── e2e/
    │   ├── test_e2e_orchestrator.py
    │   └── __init__.py
    └── unit/
        ├── test_fitbeat.py
        └── __init__.py
```

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

### ✅ 3. API Keys Configuration

To run this project, you must set up API keys as environment variables:

**Step 1:** Copy the `.env.example` file and rename it to `.env`:

```bash
cp .env.example .env
```

**Step 2:** Edit the `.env` file and insert your API keys:

```ini
OPENAI_API_KEY="your-openai-api-key"
GENIUS_API_KEY="your-genius-api-key"
```

### Getting API Keys:

- **OpenAI:** Obtain your API key [here](https://platform.openai.com/api-keys)
- **Genius:** Obtain your free API key [here](https://docs.genius.com/#/getting-started-h1)

> **Note:** Genius API keys are free and publicly available.


### ✅ **4. Run the Application**

Execute the orchestrator script with your desired prompt:

```bash
python src/orchestrator.py
```

The application will ask if you wish to continue using existing memory or clear it:

```
Do you want to clear previous memory and start a new unrelated task? (y/n):
```

- Answering `y` clears previous memory.
- Answering `n` retains memory across interactions.

---

### ✅ **5. Example of execution **

```bash
# # Scenario 4: memory
    # # first run with
    # user_prompt = "playlist for romantic date, tracks with deeply meaningful and romantic lyrics"
    # # next run
    user_prompt = "I forgot to say that we would probably dance during our date"

    orchestrator.run_planning_agent(user_prompt, num_tracks=20)
```
execution log: 
```bash
\orchestrator.py 

####################################################################################################
### Step 1: Loading existing memory (if available) and constructing the combined prompt:

Existing memory loaded:
       "The human asks the AI for a playlist for a romantic date, specifically with tracks that have deeply meaningful and romantic lyrics."

*****   Do you want to clear previous memory and start a new unrelated task? (y/n): n

Continuing with existing memory.

Combined Prompt (with memory context): 
     "The human asks the AI for a playlist for a romantic date, specifically with tracks that have deeply meaningful and romantic lyrics.
New request: I forgot to say that we would probably dance during our date"



####################################################################################################
### Step 2: LLM is analyzing user request and generating the textual plan of actions...:

Textual Plan of Actions:
 1. Analyze emotional description into numeric parameters.
2. Filter dataset based on numeric audio parameters.
3. Refine using semantic analysis (lyrics, meaning, context).
4. Retrieve_and_Convert tracks from YouTube.
5. Summarize and present final playlist.


####################################################################################################
### Step 3: LLM is converting textual plan of actions to the structured one...

Structured Plan of Actions:
 {'actions': ['Analyze', 'Filter', 'Refine', 'Retrieve_and_Convert', 'Summarize']}


####################################################################################################
### Step 4: Executing actions...

--------------------------------------------------
Action # 1. Analyze

LLM is analyzing the user prompt: "The human asks the AI for a playlist for a romantic date, specifically with tracks that have deeply meaningful and romantic lyrics.
New request: I forgot to say that we would probably dance during our date"
to derive numeric audio parameters.
Additionally, the LLM suggests a suitable folder name for the playlist.

Resulting ranges of numerical audio parameters:
  - Explicit: False
  - Danceability: [0.6, 0.8]
  - Energy: [0.4, 0.7]
  - Loudness: [-20, -8]
  - Mode: [1, 1]
  - Speechiness: [0, 0.4]
  - Acousticness: [0.2, 0.6]
  - Instrumentalness: [0, 0.3]
  - Liveness: [0, 0.3]
  - Valence: [0.6, 1]
  - Tempo: [80, 120]
  - Time_signature: [3, 4]
  - Track_genre: None

****   The tracks will be stored in the folder 'romantic_dance'   *****.


--------------------------------------------------
Action # 2. Filter

Searching Kaggle dataset for matching tracks...

 20 Selected Tracks :
    -56050 Sofia – Clairo
    -25054 Wake Me Up Before You Go-Go – Wham!
    -8309 For What It's Worth – Buffalo Springfield
    -37557 Lovely Day – Bill Withers
    -8533 Listen to the Music – The Doobie Brothers
    -19608 The Gambler – Kenny Rogers
    -37252 I Just Called To Say I Love You – Stevie Wonder
    -99826 I'm On Fire – Bruce Springsteen
    -19611 Jolene – Dolly Parton
    -80045 Chola Chola – Sathyaprakash;VM Mahalingam;Nakul Abhyankar
    -107222 Relax – Frankie Goes To Hollywood
    -106174 Super Trouper – ABBA
    -488 Blister In The Sun – Violent Femmes
    -5052 4:00A.M. – Taeko Onuki
    -80089 Chola Chola (From "Ponniyin Selvan Part -1") – A.R. Rahman;Sathyaprakash;VM Mahalingam;Nakul Abhyankar
    -90260 You Got It – Roy Orbison
    -31952 Showed Me (How I Fell In Love With You) – Madison Beer
    -47412 Burning Heart - From "Rocky IV" Soundtrack – Survivor
    -25727 Addicted To Love – Robert Palmer;Eric 'ET' Thorngren
    -56700 Dissolve – Absofacto

--------------------------------------------------
Action # 3. Refine

Ranking tracks using the hybrid method:
   1. Embedding Ranking: Rank candidate tracks based on embedding similarity to the user's prompt embedding and select the top 10 tracks.
   2. Refine the ranking of selected tracks using LLM-based semantic relevance (RAG) to the user's prompt.

----- Performing Embedding Ranking...  -------
----- Performing LLM-based semantic relevance ranking ----- ...


******   LLM is ranking candidate tracks based on semantic relevance to user prompt...

Semantic refinement (RAG) completed successfully!

Ranked Playlist:
1. I Just Called To Say I Love You by Stevie Wonder
2. Sofia by Clairo
3. Showed Me (How I Fell In Love With You) by Madison Beer
4. Lovely Day by Bill Withers
5. Jolene by Dolly Parton
6. Super Trouper by ABBA
7. Dissolve by Absofacto
8. The Gambler by Kenny Rogers
9. Blister In The Sun by Violent Femmes

--------------------------------------------------
Action # 4. Retrieve_and_Convert

Downloading recommended tracks and converting to MP3...
Saving playlist to folder: 'C:\work\INTERVIEW_PREPARATION\FitBeat\audio\downloaded_tracks\romantic_date_dance_playlist'

Downloaded and converted: 01 - Stevie Wonder - I Just Called To Say I Love You.mp3
Downloaded and converted: 02 - Clairo - Sofia.mp3
Downloaded and converted: 03 - Madison Beer - Showed Me (How I Fell In Love With You).mp3
Downloaded and converted: 04 - Bill Withers - Lovely Day.mp3
Downloaded and converted: 05 - Dolly Parton - Jolene.mp3
Downloaded and converted: 06 - ABBA - Super Trouper.mp3
Downloaded and converted: 07 - Absofacto - Dissolve.mp3
Downloaded and converted: 08 - Kenny Rogers - The Gambler.mp3
Downloaded and converted: 09 - Violent Femmes - Blister In The Sun.mp3

--------------------------------------------------
Action # 5. Summarize

Final Recommendations:
1. I Just Called To Say I Love You by Stevie Wonder | 
   Popularity: 75 | Tempo: 113.535 BPM | Explicit: False | Danceability: 0.748 | Energy: 0.551 | Loudness: -9.054 dB | Mode: Major | Speechiness: 0.0239 | Acousticness: 0.243 | Instrumentalness: 1.57e-06 | Liveness: 0.0943 | Valence: 0.65 | Time Signature: 4 | Genre: funk

2. Sofia by Clairo | 
   Popularity: 81 | Tempo: 112.997 BPM | Explicit: False | Danceability: 0.744 | Energy: 0.619 | Loudness: -9.805 dB | Mode: Major | Speechiness: 0.039 | Acousticness: 0.598 | Instrumentalness: 0.00372 | Liveness: 0.231 | Valence: 0.641 | Time Signature: 4 | Genre: indie-pop

3. Showed Me (How I Fell In Love With You) by Madison Beer | 
   Popularity: 69 | Tempo: 95.02 BPM | Explicit: False | Danceability: 0.723 | Energy: 0.542 | Loudness: -8.5 dB | Mode: Minor | Speechiness: 0.026 | Acousticness: 0.476 | Instrumentalness: 0.0826 | Liveness: 0.0928 | Valence: 0.675 | Time Signature: 4 | Genre: electro

4. Lovely Day by Bill Withers | 
   Popularity: 76 | Tempo: 97.923 BPM | Explicit: False | Danceability: 0.692 | Energy: 0.651 | Loudness: -8.267 dB | Mode: Major | Speechiness: 0.0324 | Acousticness: 0.292 | Instrumentalness: 0.00241 | Liveness: 0.105 | Valence: 0.706 | Time Signature: 4 | Genre: funk

5. Jolene by Dolly Parton | 
   Popularity: 73 | Tempo: 110.578 BPM | Explicit: False | Danceability: 0.674 | Energy: 0.537 | Loudness: -10.971 dB | Mode: Minor | Speechiness: 0.0363 | Acousticness: 0.566 | Instrumentalness: 0.0 | Liveness: 0.131 | Valence: 0.809 | Time Signature: 4 | Genre: country

6. Super Trouper by ABBA | 
   Popularity: 72 | Tempo: 118.34 BPM | Explicit: False | Danceability: 0.764 | Energy: 0.626 | Loudness: -8.274 dB | Mode: Major | Speechiness: 0.0288 | Acousticness: 0.457 | Instrumentalness: 6.35e-06 | Liveness: 0.201 | Valence: 0.961 | Time Signature: 4 | Genre: swedish

7. Dissolve by Absofacto | 
   Popularity: 68 | Tempo: 85.486 BPM | Explicit: False | Danceability: 0.688 | Energy: 0.582 | Loudness: -10.668 dB | Mode: Minor | Speechiness: 0.0542 | Acousticness: 0.23 | Instrumentalness: 0.000157 | Liveness: 0.0663 | Valence: 0.872 | Time Signature: 4 | Genre: indie-pop

8. The Gambler by Kenny Rogers | 
   Popularity: 75 | Tempo: 87.04 BPM | Explicit: False | Danceability: 0.671 | Energy: 0.501 | Loudness: -13.119 dB | Mode: Major | Speechiness: 0.0594 | Acousticness: 0.342 | Instrumentalness: 0.0 | Liveness: 0.194 | Valence: 0.86 | Time Signature: 4 | Genre: country

9. Blister In The Sun by Violent Femmes | 
   Popularity: 71 | Tempo: 96.889 BPM | Explicit: False | Danceability: 0.726 | Energy: 0.537 | Loudness: -8.896 dB | Mode: Major | Speechiness: 0.114 | Acousticness: 0.316 | Instrumentalness: 0.0 | Liveness: 0.0707 | Valence: 0.882 | Time Signature: 4 | Genre: acoustic


All actions executed successfully!

Memory updated and saved for future sessions.

Process finished with exit code 0


```



## 👤 **Author**

This project (**FitBeat**) was created and developed by **Sergey Gendel**.

---

## ⚠️ **Legal Disclaimer (YouTube Downloads)**

Downloading content directly from YouTube may violate YouTube's [Terms of Service](https://www.youtube.com/t/terms), specifically regarding unauthorized downloading and distribution.  
**FitBeat** is provided for demonstration, educational, and personal use only.  
Ensure you have permission or rights to any content downloaded using this tool. **The author is not responsible for misuse or violations of applicable laws or terms of service.**