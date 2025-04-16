from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

class PromptEngineer:
    def __init__(self):
        self.dataset_genres = [
            "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal",
            "bluegrass", "blues", "brazil", "breakbeat", "british", "cantopop", "chicago-house",
            "children", "chill", "classical", "club", "comedy", "country", "dance", "dancehall",
            "death-metal", "deep-house", "detroit-techno", "disco", "disney", "drum-and-bass",
            "dub", "dubstep", "edm", "electro", "electronic", "emo", "folk", "forro", "french",
            "funk", "garage", "german", "gospel", "goth", "grindcore", "groove", "grunge", "guitar",
            "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal", "hip-hop", "honky-tonk",
            "house", "idm", "indian", "indie", "indie-pop", "industrial", "iranian", "j-dance",
            "j-idol", "j-pop", "j-rock", "jazz", "k-pop", "kids", "latin", "latino", "malay",
            "mandopop", "metal", "metalcore", "minimal-techno", "mpb", "new-age", "opera", "pagode",
            "party", "piano", "pop", "pop-film", "power-pop", "progressive-house", "psych-rock",
            "punk", "punk-rock", "r-n-b", "reggae", "reggaeton", "rock", "rock-n-roll", "rockabilly",
            "romance", "sad", "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska",
            "sleep", "songwriter", "soul", "spanish", "study", "swedish", "synth-pop", "tango",
            "techno", "trance", "trip-hop", "turkish", "world-music"
        ]

        self.system_template = """
               You're a music recommendation expert.
               The user provides a general emotional or situational description.
               You must explicitly respond in JSON format containing ranges or explicit values for these parameters:

               - explicit: Explicitly boolean (true = explicit lyrics; false = no explicit lyrics; null if uncertain).
               - danceability (0.0–1.0): How suitable a track is for dancing based on tempo, rhythm stability, beat strength, and regularity.
               - energy (0.0–1.0): Intensity and activity. Energetic tracks feel fast, loud, noisy (e.g. death metal = high energy, Bach prelude = low energy).
               - loudness (-60 to 0 dB): Overall track loudness (closer to 0 is louder).
               - mode: Modality of the track explicitly (0 = minor, 1 = major, null if uncertain).
               - speechiness (0.0–1.0): Presence of spoken words (values >0.66 = mostly speech, 0.33–0.66 = rap/music mix, <0.33 = mostly music).
               - acousticness (0.0–1.0): Likelihood track is acoustic (1.0 = fully acoustic).
               - instrumentalness (0.0–1.0): Likelihood track has no vocals (1.0 = instrumental only).
               - liveness (0.0–1.0): Presence of audience (values >0.8 = live performance).
               - valence (0.0–1.0): Musical positiveness (1.0 = happy/euphoric, 0.0 = sad/angry).
               - tempo (60–200 BPM): Overall speed or pace of a track in beats per minute.
               - time_signature (3–7): Number of beats per bar (typical values: 3 to 7).
               - track_genre: Select explicitly from provided genre list:
                 {genres}

        If any parameter can't be determined,  return "null".

        Additionally,  include a short summary (2-4 words) capturing the user's request for folder naming.

        JSON response format:
        {{
            "numeric_ranges": {{
                "explicit": true, 
                "tempo": [min, max],
                ...
            }},
            "summary": "short summary here"
        }}
        """

    def construct_prompt(self, user_prompt):
        system_message = SystemMessage(content=self.system_template.format(genres=self.dataset_genres))
        user_message = HumanMessage(content=user_prompt, additional_kwargs={"message_type": "user_prompt"})
        return ChatPromptTemplate.from_messages([system_message, user_message])


    def construct_planning_prompt_with_example(self, user_prompt):
        system_message = SystemMessage(content=f"""
        You're a task-planning assistant for a music recommendation agent named FitBeat.

        FitBeat has the following abilities and resources:

        AVAILABLE RESOURCES:
        - A Kaggle dataset containing tracks with numeric audio features (tempo, energy, danceability, valence, loudness, speechiness, instrumentalness, acousticness, liveness, genre, popularity).
        - Ability to interpret emotional descriptions using LLM and convert them to numeric audio parameters.
        - Ability to filter tracks based on numeric audio parameters.
        - Ability to retrieve audio tracks from YouTube.
        - Ability to convert downloaded tracks to mp3 format.
        - Ability to summarize and present results.

        YOUR TASK:
        Given a user's music request, outline a clear and executable sequence of actions. 
        Each action must  correspond to one of the listed abilities or resources.

        EXAMPLE (user input: "relaxing music for meditation"):
        1. Interpret user's emotional description into numeric audio parameters.
        2. Filter Kaggle dataset using numeric parameters.
        3. Retrieve recommended audio tracks from YouTube.
        4. Convert downloaded tracks to mp3 format.
        5. Summarize and  present recommended tracks.

        Return as a numbered list of actions. Do not include any steps beyond listed capabilities.
        """)

        user_message = HumanMessage(content=user_prompt)

        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_planning_prompt_old(self, user_prompt):
        system_message = SystemMessage(content=f"""
        You're a task-planning assistant for a music recommendation agent named FitBeat.
    
        FitBeat has these abilities and resources:
        - Kaggle dataset with audio features (tempo, energy, danceability, valence, etc.).
        - Convert emotional descriptions into numeric audio parameters.
        - Filter tracks by audio parameters.
        - Retrieve tracks from YouTube.
        - Convert tracks to mp3.
        - Summarize and present results.
    
        Outline a clear, executable sequence of actions corresponding only to these abilities.
    
        Return as a numbered list of actions.
        """)

        user_message = HumanMessage(content=user_prompt)

        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_planning_prompt(self, user_prompt):
        system_message = SystemMessage(content=f"""
        You're a task-planning assistant for FitBeat, an LLM-powered music recommendation agent.

        FitBeat explicitly has these clearly defined abilities and resources:
        1. Analyze: Explicitly convert emotional descriptions into numeric audio parameters (tempo, valence, energy, etc.).
        2. Filter: Explicitly filter tracks based on numeric audio parameters explicitly using Kaggle dataset.
        3. Refine: Explicitly refine the track list semantically using lyrics, song meanings, and semantic context explicitly (Retrieval-Augmented Generation, RAG).
        4. Retrieve_and_Convert: Explicitly retrieve audio tracks from YouTube and explicitly convert them to MP3.
        5. Summarize: Explicitly summarize and present the final playlist.

        Your explicit task:
        - Given user's request explicitly, outline a clear and executable sequence of actions.
        - If the user explicitly asks or implies about meaning, lyrics, or emotional depth explicitly beyond numeric parameters, explicitly include the "Refine" step.
        - Clearly distinguish between numeric filtering ("Filter") and semantic refinement explicitly using lyrics and context ("Refine").

        Example (user input: "Playlist of deep romantic songs with meaningful lyrics"):
        1. Analyze emotional description explicitly into numeric parameters.
        2. Filter dataset explicitly based on numeric audio parameters.
        3. Refine explicitly using semantic analysis (lyrics, meaning, context).
        4. Retrieve_and_Convert tracks explicitly from YouTube.
        5. Summarize explicitly and present final playlist.

        Return explicitly as numbered list of actions.
        """)

        user_message = HumanMessage(content=user_prompt)
        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_action_structuring_prompt_old(self, explicit_plan):
        system_message = SystemMessage(content="""
        You're an assistant tasked with converting a plain-text, numbered list of task actions into structured JSON.
    
        FitBeat (music recommendation agent) has ONLY these action keywords, strictly in the logical order they should always appear:
        1. "Analyze": includes analyzing user prompt, interpreting emotional descriptions, converting them into numeric audio parameters.
        2. "Filter": includes filtering the dataset using numeric audio parameters.
        3. "Retrieve": includes retrieving audio tracks from YouTube.
        4. "Convert": includes converting retrieved tracks into mp3 format.
        5. "Summarize": includes summarizing results clearly.
    
        You must analyze each provided numbered action carefully, mapping each action clearly to ONE keyword above, while strictly maintaining their logical order.
    
        Clarification:
        - Converting emotional descriptions maps ONLY to "Analyze".
        - Filtering tracks comes AFTER "Analyze".
        - Retrieval and Conversion clearly and follow filtering.
        - Summarizing comes last.
    
        Always ensure your structured actions strictly follow the logical order clearly listed above.
    
        JSON format you must return clearly:
        {
          "actions": ["Analyze", "Filter", "Retrieve", "Convert", "Summarize"]
        }
    
        No additional explanation. Respond ONLY with valid JSON.
        """)

        user_message = HumanMessage(content=f"Convert this text plan into structured JSON:\n\n{explicit_plan}")

        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_action_structuring_prompt_old_2(self, explicit_plan):
        system_message = SystemMessage(content="""
        You're an assistant converting a textual action plan into structured JSON actions for the FitBeat agent.

        Available actions:
        - "Analyze": interpret emotional descriptions into audio parameters.
        - "Filter": filter tracks based on audio parameters.
        - "Retrieve": retrieve tracks from YouTube.
        - "Convert": convert retrieved tracks into mp3 format.
        - "Summarize": summarize the final playlist.

        Instructions:
        - Include each action type AT MOST ONCE, regardless of how many times it appears in the textual plan.
        - List actions ONLY IF they are explicitly mentioned in the provided plan.
        - Do NOT insert, reorder, or assume any actions not explicitly stated.
        - If multiple specific examples of the same action are listed explicitly in sequence (e.g., multiple "Retrieve" steps), collapse them into a single instance of that action.

        Return ONLY a valid JSON response in the following format (no additional text or explanation):

        {
          "actions": ["Action1", "Action2", "..."]
        }
        """)
        user_message = HumanMessage(content=f"Convert this explicit plan into structured JSON:\n\n{explicit_plan}")

        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_action_structuring_prompt(self, explicit_plan):
        system_message = SystemMessage(content="""
        You're an assistant converting a textual action plan into structured JSON actions for the FitBeat agent.

        Available actions explicitly defined:
        - "Analyze": interpret emotional descriptions into numeric audio parameters.
        - "Filter": filter tracks explicitly based on numeric audio parameters.
        - "Refine": explicitly perform semantic refinement using RAG (lyrics, emotions, semantic context).
        - "Retrieve_and_Convert": explicitly retrieve tracks from YouTube and convert them explicitly to MP3 format.
        - "Summarize": explicitly summarize the final playlist.

        Instructions explicitly given:
        - Include each action AT MOST ONCE explicitly.
        - List actions ONLY IF explicitly mentioned in provided plan.
        - Do NOT insert, reorder, or assume actions not explicitly stated.
        - Collapse explicitly multiple occurrences of same action into single instance explicitly.

        Return ONLY valid JSON explicitly, no additional text:
        {
          "actions": ["Action1", "Action2", "..."]
        }
        """)
        user_message = HumanMessage(content=f"Convert this explicit plan into structured JSON:\n\n{explicit_plan}")
        return ChatPromptTemplate.from_messages([system_message, user_message])


    def construct_refined_prompt(self, user_prompt, refined_tracks_context):
        context_text = "\n".join([
            f"{i + 1}. {track['artist']} - {track['title']}:\n{track['context'][:500]}..." if track[
                'context'] else f"{i + 1}. {track['artist']} - {track['title']}: No additional context."
            for i, track in enumerate(refined_tracks_context)
        ])

        augmented_prompt = f"""
        Given the user's request: '{user_prompt}', 
        and given the candidate tracks with their lyrics/descriptions provided below:

        {context_text}

        Perform the following instructions precisely:

        1. Rank ALL tracks listed above from MOST suitable to LEAST suitable according to how closely each matches the user's request.
        2. Do NOT omit any track explicitly—include every track listed exactly once.
        3. Ensure there are NO DUPLICATES in your final ranked list.
        4. Return ONLY this valid JSON format with no additional explanations or text:

        {{
            "ranked_playlist": [
                {{"artist": "Artist1", "title": "Title1"}},
                {{"artist": "Artist2", "title": "Title2"}},
                ...
            ],
            "summary": "short_summary_for_folder_name"
        }}
        """

        return ChatPromptTemplate.from_messages([
            SystemMessage(
                content="You're an expert music recommender ranking candidate track. Follow instructions exactly."),
            HumanMessage(content=augmented_prompt)
        ])


if __name__ == "__main__":
    from llm_executor import LLMExecutor
    import json

    prompt_engineer = PromptEngineer()
    llm_executor = LLMExecutor()


    # Scenario 1. Analyze → Filter → Retrieve_and_Convert → Summarize
    # user_prompt = "music for romantic date"

    # Scenario 2. Analyze → Filter → RAG → Retrieve_and_Convert → Summarize
    # #user_prompt = "playlist for romantic date, tracks with deeply meaningful and romantic lyrics"

    # Scenario 3: Retrieve_and_Convert → Summarize
    user_prompt = (
        "I already have a list of specific songs:\n"
        "- The Weeknd - Blinding Lights\n"
        "- Eminem - Lose Yourself\n"
        "- Coldplay - Adventure of a Lifetime\n\n"
        "Just download these exact songs from YouTube, convert them to mp3, "
        "and summarize the resulting playlist. No additional analysis or recommendations are needed."
    )

    planning_prompt = prompt_engineer.construct_planning_prompt(user_prompt)
    messages = planning_prompt.format_messages(user_prompt=user_prompt)

    explicit_plan = llm_executor.execute(messages)

    print("\nStep 1 - Explicit Plan (Text):\n", explicit_plan)

    # Step 2: Convert explicit plan into structured actions JSON
    structuring_prompt = prompt_engineer.construct_action_structuring_prompt(explicit_plan)
    messages_json = structuring_prompt.format_messages(explicit_plan=explicit_plan)
    structured_actions = llm_executor.execute(messages_json)

    print("\nStep 2 - Structured Actions (JSON):\n", json.dumps(structured_actions, indent=2))

    # user_prompt = "music tracks suitable for studying for exams"
    # user_prompt = (
    #     "I already have a list of songs. "
    #     "Can you just find these exact tracks on YouTube, download and convert them to mp3, "
    #     "and then summarize the results for me?"
    # )
    #
    # user_prompt = (
    #     "I already have a list of songs. "
    #     "Can you prepare a payable playlist with these songs for me  ?"
    # )# tries to find common features and creates new playlist
    #
    # user_prompt = (
    #     "I already have a list of specific songs. "
    #     "Just download these exact songs from YouTube, convert them to mp3, and summarize the resulting playlist. "
    #     "No additional analysis or recommendations are needed."
    # )# works but too simple
    #
    # user_prompt = (
    #     "I already have a list of songs. "
    #     "Can you prepare a payable playlist with these songs for me  ?"
    #     "No additional analysis or recommendations are needed."
    # ) # GOOD
    #
    # user_prompt = (
    #     "I already have a list of songs. I want playlist with similar, but other, songs "
    #     "Can you do it for me ?"
    # )  # good!
    #
    # user_prompt = (
    #     "I already have a list of songs. I want playlist with similar, but other, songs "
    #     "Can you do it for me ? I just need track names, not the playable files"
    # )  # good!

