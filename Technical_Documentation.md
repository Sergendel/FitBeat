# Technical Documentation 

## Semantic Refinement (RAG) 
### Intro: 
After the initial list of tracks was created, employing the numercal filtering of the audio parameters, the tracks are ranked based on their semantic relevance to the user's prompt.

The generl description of tracks list creation and ranking: 
1. Create initial list of tracks by numerical filtering
2. Create basic corpus of ~200  songs' descriptions (lyrics + description), based on parameters thresholds,
3. Create embedding for each track in the corpus, save emebdding and description to CromodDb collection.
4. Rank the tracks in the list based on semantic relevence to users promt by: 
    5.1. By creation of user's request embedding and claculating istance between it and tracks embeddings (No LLM involved).  
    5.2. By direct LLM request where user request and context (tracks lyrics and descriptions) are suppled in prompt. 
         src/prompt_engineer.construct_refined_prompt - prmpt creation
    5.3. Hybrid if 1 and 2: first rank by method 2 (fast but rough) and then erfine by method 1 (slower but accurate)

Below we describe steps 2 - 4

1. Creation of basic corpus of tracks description (create_basic_corpus.py) : 
    The idea is to create initial corpus of descriptions for tracks that most likely be in demand by most users. 
    This is done to reduce time of corus creation in future. 
    The most "Energetic" tracks (e.g high dancebility, high energy, high tempo) are choosed for the corpus by default.
    Function corpus/create_basic_corpus.py creates this "basic"corpus with ~200 tracks:
        1.1. Reads the dataset.csv file,
        1.2. Filters out the tracks that corresponds to parameters tresholds (hardcoded in the function)
        1.3. For every track in the resulting list: 
            1.3.1. Finds the song on genius.com  
            1.3.2. If song found downloads the description (lyrics + Description) by calling to function get_song_description
            1.3.3. Saves description to  f"{artist} - {title}.txt"  file in config.CORPUS_DIR folder. 
            1.3.4. Updates config.CORPUS_METADATA_PATH csv file with the track details 
    Notice that if track of interst is not present in the "basic" corpus, its description will be created "on-the-fly", see details below.

2.  Create embeddings for the basic corpus (corpus/embeddings/generate_embeddings.py)        
    This script creates embeddings for the tracks in the "basic" corpus. Again, the idea is to save time and not create the embedding for eah song "on-the-fly". 
    2.1 Tools used 
        2.1.1 Embedding model - SentenceTransformer('all-MiniLM-L6-v2') 
        2.1.2 Embeding DB     - ChromaDB     
    2.2 Flow:     
        2.2.1 Initialize ChromaDB collection - saved to config.EMBEDDINGS_DB_PATH
        2.2.2 Generate embedding for each track (read corresponding *.txt file from basic corpus) and create embedding by embeding model call.
        2.2.3 Add embedding and description to the collection.
    Notice that each embedding has unique id f"{artist} - {title}.txt, where the filename is taken from config.CORPUS_METADATA_PATH csv file. Actually this is the ony time we use this file. 

3. Ranking:
    3.1 Using embedding.
        3.1.1 
