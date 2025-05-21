# FitBeat: LLM-Powered Music Recommendation Agent

**Author:** Sergey Gendel
**Live Demo:** [https://main.dxpisg36o3xzj.amplifyapp.com](https://main.dxpisg36o3xzj.amplifyapp.com)

---

## Demo Video

Watch FitBeat in action:

https://main.dxpisg36o3xzj.amplifyapp.com


---

## Project Overview

FitBeat is an AI-driven music recommendation agent that converts emotional or situational descriptions (e.g., "music for intense gym training") into personalized playlists using advanced NLP techniques and cloud-based infrastructure.

---

## Technology Stack

* **Languages & Libraries:** Python, Langchain, ChromaDB, Sentence-Transformers, OpenAI API, Genius API
* **Machine Learning Techniques:** Retrieval-Augmented Generation (RAG), Embedding-based Semantic Ranking
* **Cloud Infrastructure:** AWS Lambda, API Gateway, S3, Secrets Manager, CloudWatch
* **Deployment Tools:** AWS SAM, Docker, GitHub Actions (CI/CD)
* **Testing & Quality:** Pytest, Flake8, Black, Isort

---

##  How It Works (Quick Overview)

### 1. Initial Filtering (Numeric Analysis)

- Converts user prompts into numeric audio features (tempo, energy, danceability, etc.).
- Filters tracks from a large Kaggle [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset), containing over 114,000 annotated tracks.

### 2. Hybrid Semantic Ranking (Embeddings & RAG)

- Retrieves track contexts (lyrics and descriptions) from [Genius](https://genius.com/)
- Initially ranks candidate tracks based on embedding similarity between the user's prompt embedding and the tracks' context embeddings, then selects the top-k candidates.
- Performs further semantic refinement (RAG-based) using LLM-based semantic analysis to finalize rankings based on emotional and contextual relevance.


### 3. Final Recommendation & Output (Conditional)
Depending on the application configuration (FRONTEND_MODE), FitBeat provides one of two outputs:

- Frontend Mode (FRONTEND_MODE=True):

- - Creates a structured, interactive recommendation table (Artist, Track Name, YouTube link).

- - Does not download or convert audio.

- Full Mode (FRONTEND_MODE=False):

- - Creates the recommendation table.

- - Additionally, downloads selected tracks from YouTube and converts them to MP3 format.
---

---



## Deployment Overview

FitBeat uses an asynchronous, two-Lambda AWS deployment architecture with AWS SAM. The setup includes:

* **Lambda #1 (Lightweight Lambda)**: Receives initial API requests, generates Job IDs, and triggers the Heavyweight Lambda asynchronously.
* **Lambda #2 (Heavyweight Lambda)**: Handles intensive tasks, including playlist generation and YouTube link retrieval, and stores the results in AWS S3.
* **AWS API Gateway**: Provides explicit, secure endpoints for interacting with Lambdas.
* **AWS S3**: Stores generated playlists.

### Architecture Flowchart

```
Frontend          Lambda #1 (Light)          Lambda #2 (Heavy)          S3 (Storage)
  │                      │                           │                       │
  ├───(HTTP POST)───────>│                           │                       │
  │                      ├── Generate Job ID         │                       │
  │                      ├── Async Invoke ──────────>│                       │
  │                      │                           ├─── Perform Heavy Task │
  │<─────(Job ID)────────┤                           │                       │
  │                      │                           ├─── Save Result ──────>│
  │                      │                           │                       │
(Polling starts)         │                           │                       │
  │                      │                           │                       │
  ├─(HTTP GET: status)──>│                           │                       │
  │                      ├───(Check S3 status)──────────────────────────────>│
  │                      │<───("processing"/no file)─────────────────────────┤
  │<─("processing")──────┤                           │                       │
  │                      │                           │                       │
  ├─(HTTP GET: status)──>│                           │                       │
  │                      ├───(Check S3 status)──────────────────────────────>│
  │                      │<───("completed"/file found + data)────────────────┤
  │<─("completed"+data)──┤                           │                       │
  │                      │                           │                       │
  ├─ Display Results ───>│                           │                       │
```




## How to Run Locally

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/FitBeat.git
cd FitBeat
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys

Copy `.env.example` to `.env` and insert your OpenAI and Genius API keys:

```ini
OPENAI_API_KEY="your-openai-api-key"
GENIUS_API_KEY="your-genius-api-key"
```

### Step 4: Run Application

```bash
python -m core.orchestrator
```

---

##  **FitBeat Execution Examples**

These examples demonstrate how FitBeat autonomously creates an action plan and selectively chooses tools based on the user's prompt.

---

### **Examples Without Memory**

####  **Scenario 1:** `Analyze → Filter → Retrieve_and_Convert → Summarize`

- **Prompt:** `"music for romantic date"`
- **Actions:**
  1. Analyze prompt into numeric audio parameters.
  2. Filter tracks numerically.
  3. Create_Recommendation_Table.
  4. Retrieve tracks from YouTube and convert to MP3. # ONLY if config.FRONTEND_MODE == FALSE
  5. Summarize playlist.

####  **Scenario 2:** `Analyze → Filter → Rank → Retrieve_and_Convert → Summarize`

- **Prompt:** `"playlist for romantic date, tracks with deeply meaningful and romantic lyrics"`
- **Actions:**
  1. Analyze prompt into numeric audio parameters.
  2. Filter tracks numerically.
  3. Rank tracks semantically (using lyrics/context via RAG).
  4. Create_Recommendation_Table
  5. Retrieve tracks from YouTube and convert to MP3. # ONLY if config.FRONTEND_MODE == FALSE
  6. Summarize playlist.

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
  1. Create_Recommendation_Table
  2. Retrieve provided tracks from YouTube and convert to MP3. # ONLY if config.FRONTEND_MODE == FALSE
  3. Summarize playlist.

---

###  **Example With Memory (Persistent Context)**

Demonstrates memory across sequential interactions:

- **Initial Prompt:** `"playlist for romantic date, tracks with deeply meaningful and romantic lyrics"`
- **Next Prompt (with memory):** `"I forgot to say that we would probably dance during our date"`

**Behavior:**
- FitBeat considers both prompts, refining recommendations based on cumulative context.
- Agent autonomously decides which tools are required given the additional context.

---


##  **How to Run Locally**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-repo/FitBeat.git
cd FitBeat
```

### **2. Install Requirements**
```bash
pip install -r requirements.txt
```

### 3. API Keys Configuration

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


### **4. Run the Application**

Execute the orchestrator script with your desired prompt:

```bash
python -m core.orchestrator
```

The application will ask if you wish to continue using existing memory or clear it:

```
Do you want to clear previous memory and start a new unrelated task? (y/n):
```

- Answering `y` clears previous memory.
- Answering `n` retains memory across interactions.

---

### **5. Example of execution **

```bash
C:\Users\serge\miniconda3\envs\validate_env\python.exe C:\work\INTERVIEW_PREPARATION\FitBeat\src\orchestrator.py 


####################################################################################################
### Step 1: Loading existing memory (if available) and constructing the combined prompt:

Existing memory loaded:
       "The human asks the AI to create a playlist for a romantic date with tracks that have deep meaning."

***** Do you want to clear previous memory and start a new unrelated task? (y/n): n

Continuing with existing memory.

Combined Prompt (with memory context): 
     "The human asks the AI to create a playlist for a romantic date with tracks that have deep meaning.
New request: I forgot to say that we would probably dance during our date"



####################################################################################################
### Step 2: LLM is analyzing user request and generating the textual plan of actions...:

Textual Plan of Actions:
 1. Analyze into numeric parameters for romantic and danceable tracks.
2. Filter numerically for romantic and upbeat tracks suitable for dancing.
3. Refine semantically to select tracks with deep meanings and emotional depth.
4. Create_Recommendation_Table.
5. Summarize the final playlist.


####################################################################################################
### Step 3: LLM is converting textual plan of actions to the structured one...

Structured Plan of Actions:
 {'actions': ['Analyze', 'Filter', 'Refine', 'Create_Recommendation_Table', 'Summarize']}


####################################################################################################
### Step 4: Executing actions...

--------------------------------------------------
Action # 1. Analyze

LLM is analyzing the user prompt: "The human asks the AI to create a playlist for a romantic date with tracks that have deep meaning.
New request: I forgot to say that we would probably dance during our date"
to derive numeric audio parameters.
Additionally, the LLM suggests a suitable folder name for the playlist.

Resulting ranges of numerical audio parameters:
  - Explicit: False
  - Danceability: [0.6, 0.8]
  - Energy: [0.4, 0.7]
  - Loudness: [-20, -8]
  - Mode: None
  - Speechiness: [0, 0.4]
  - Acousticness: [0.2, 0.6]
  - Instrumentalness: [0, 0.5]
  - Liveness: [0, 0.3]
  - Valence: [0.5, 0.8]
  - Tempo: [90, 120]
  - Time_signature: None
  - Track_genre: None

****   The tracks will be stored in the folder 'romantic_dance'   *****.


--------------------------------------------------
Action # 2. Filter

Searching Kaggle dataset for matching tracks...

 20 Selected Tracks :
    -56050 Sofia – Clairo
    -20701 Go Crazy – Chris Brown;Young Thug
    -64000 Just the Two of Us (feat. Bill Withers) – Grover Washington, Jr.;Bill Withers
    -37557 Lovely Day – Bill Withers
    -37252 I Just Called To Say I Love You – Stevie Wonder
    -11190 Sympathy For The Devil - 50th Anniversary Edition – The Rolling Stones
    -80045 Chola Chola – Sathyaprakash;VM Mahalingam;Nakul Abhyankar
    -107222 Relax – Frankie Goes To Hollywood
    -64500 Just the Two of Us – Grover Washington, Jr.
    -20250 Eyes Off You – PRETTYMUCH
    -31952 Showed Me (How I Fell In Love With You) – Madison Beer
    -80089 Chola Chola (From "Ponniyin Selvan Part -1") – A.R. Rahman;Sathyaprakash;VM Mahalingam;Nakul Abhyankar
    -80050 Ajab Si – KK
    -90260 You Got It – Roy Orbison
    -47412 Burning Heart - From "Rocky IV" Soundtrack – Survivor
    -107283 Dance Hall Days – Wang Chung
    -80131 Saiyaara – Sohail Sen;Mohit Chauhan;Taraannum Mallik;Kausar Munir
    -19909 New Kid in Town - 2013 Remaster – Eagles
    -103920 Human Nature – Michael Jackson
    -80157 O Sanam – Lucky Ali

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
2. Lovely Day by Bill Withers
3. Human Nature by Michael Jackson
4. Sofia by Clairo
5. Showed Me (How I Fell In Love With You) by Madison Beer
6. Dance Hall Days by Wang Chung
7. Go Crazy by Chris Brown;Young Thug
8. O Sanam by Lucky Ali

--------------------------------------------------
Action # 4. Create_Recommendation_Table


Recommended Playlist:

Artist                 Track Name                              Official YouTube Link                      
         Stevie Wonder         I Just Called To Say I Love You https://www.youtube.com/watch?v=1bGOgY1CmiU
          Bill Withers                              Lovely Day https://www.youtube.com/watch?v=bEeaS6fuUoA
       Michael Jackson                            Human Nature https://www.youtube.com/watch?v=ElN_4vUvTPs
                Clairo                                   Sofia https://www.youtube.com/watch?v=L9l8zCOwEII
          Madison Beer Showed Me (How I Fell In Love With You) https://www.youtube.com/watch?v=khCziHJQSwg
            Wang Chung                         Dance Hall Days https://www.youtube.com/watch?v=V-xpJRwIA-Q
Chris Brown;Young Thug                                Go Crazy https://www.youtube.com/watch?v=dPhwbZBvW2o
             Lucky Ali                                 O Sanam https://www.youtube.com/watch?v=dWqb-WqbGh8

JSON playlist saved to 'output\playlists\romantic_date_dance_playlist\playlist.json'
CSV playlist saved to 'output\playlists\romantic_date_dance_playlist\playlist.csv'

```


##  **Author**

This project (**FitBeat**) was created and developed by **Sergey Gendel**.

---

##  **Legal Disclaimer (YouTube Downloads)**

Downloading content directly from YouTube may violate YouTube's [Terms of Service](https://www.youtube.com/t/terms), specifically regarding unauthorized downloading and distribution.  
**FitBeat** is provided for demonstration, educational, and personal use only.  
Ensure you have permission or rights to any content downloaded using this tool. **The author is not responsible for misuse or violations of applicable laws or terms of service.**