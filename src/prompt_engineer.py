from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

import config
from src.dataset_genres import DATASET_GENRES


class PromptEngineer:
    def __init__(self):
        self.dataset_genres = DATASET_GENRES

        self.system_template = """
               You're a music recommendation expert.
               The user provides a general emotional or situational description.
               You must respond in JSON format containing ranges or values
               for these parameters:

               - explicit: Boolean (true = explicit lyrics;
                           false = no explicit lyrics; null if uncertain).
               - danceability (0.0–1.0): How suitable a track is for dancing
                                         based on tempo, rhythm stability,
                                         beat strength, and regularity.
               - energy (0.0–1.0): Intensity and activity. Energetic tracks feel fast,
                                   loud, noisy (e.g. death metal = high energy,
                                   Bach prelude = low energy).
               - loudness (-60 to 0 dB):
                                   Overall track loudness (closer to 0 is louder).
               - mode: Modality of the track (0 = minor, 1 = major, null if uncertain).
               - speechiness (0.0–1.0): Presence of spoken words
                                        (values >0.66 = mostly speech,
                                        0.33–0.66 = rap/music mix,
                                        <0.33 = mostly music).
               - acousticness (0.0–1.0): Likelihood track is acoustic
                                         (1.0 = fully acoustic).
               - instrumentalness (0.0–1.0): Likelihood track has no vocals
                                             (1.0 = instrumental only).
               - liveness (0.0–1.0): Presence of audience
                                    (values >0.8 = live performance).
               - valence (0.0–1.0): Musical positiveness
                                    (1.0 = happy/euphoric, 0.0 = sad/angry).
               - tempo (60–200 BPM):
                              Overall speed or pace of a track in beats per minute.
               - time_signature (3–7):
                              Number of beats per bar (typical values: 3 to 7).
               - track_genre: Select from provided genre list:
                 {genres}

        If any parameter can't be determined,  return "null".

        Additionally,  include a short summary (2-4 words) capturing the user's request
        for folder naming.

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
        system_message = SystemMessage(
            content=self.system_template.format(genres=self.dataset_genres)
        )
        user_message = HumanMessage(
            content=user_prompt, additional_kwargs={"message_type": "user_prompt"}
        )
        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_planning_prompt_old(self, user_prompt):
        system_message = SystemMessage(
            content="""
        You're a task-planning assistant for FitBeat, an LLM-powered
        music recommendation agent.

        FitBeat has these explicitly defined abilities and resources:
        1. Analyze: Convert emotional descriptions into numeric audio parameters
                    (tempo, valence, energy, etc.).
        2. Filter:
             Filter tracks based on numeric audio parameters using Kaggle dataset.
        3. Refine: Refine the track list semantically using lyrics, song meanings,
                   and semantic context (Retrieval-Augmented Generation, RAG).
        4. Create_Recommendation_Table: Explicitly generate a structured recommendation
            table clearly including Artist names, Track names, and Official YouTube
            links clearly and explicitly.
        5. Retrieve_and_Convert:
                        Retrieve audio tracks from YouTube and convert them to MP3.
        6. Summarize: Summarize and present the final playlist.

        Your explicit task:
        - Given user's request, outline a clear and executable sequence of actions.
        - If the user explicitly asks or implies about meaning, lyrics, or emotional
          depth beyond numeric parameters, include the "Refine" step.
        - Clearly distinguish between numeric filtering ("Filter") and
           semantic refinement using lyrics and context ("Refine").

        Example (user input: "Playlist of deep romantic songs with meaningful lyrics"):
        1. Analyze emotional description into numeric parameters.
        2. Filter dataset  based on numeric audio parameters.
        3. Refine using semantic analysis (lyrics, meaning, context).
        4. Create Recommendation Table
        4. Retrieve_and_Convert tracks from YouTube.
        5. Summarize and present final playlist.

        Return as numbered list of actions.
        """
        )

        user_message = HumanMessage(content=user_prompt)
        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_planning_prompt(self, user_prompt):
        """
        Constructs planning prompt  based on frontend_mode.
        """
        actions_available = """
        1. Analyze: Convert emotional descriptions into numeric audio parameters
                    (tempo, valence, energy, etc.).
        2. Filter:
                Filter tracks based on numeric audio parameters using Kaggle dataset.
        3. Refine: Refine the track list semantically using lyrics, song meanings,
                   and semantic context (Retrieval-Augmented Generation, RAG).
        4. Create_Recommendation_Table:
                Create structured recommendation table (Artist, Track, YouTube link).
        5. Summarize: Summarize and present the final playlist.
        """

        if not config.FRONTEND_MODE:
            actions_available += (
                "\n    6. Retrieve_and_Convert:"
                "Retrieve audio tracks from YouTube and convert them to MP3."
            )

        system_message = SystemMessage(
            content=f"""
        You're a task-planning assistant for FitBeat, an LLM-powered
        music recommendation agent.

        FitBeat has these defined abilities and resources:
        {actions_available}


        Your explicit task:
        - Given user's request, outline a clear and executable sequence of actions.
        - If the user asks or implies about meaning, lyrics, or emotional
          depth beyond numeric parameters, include the "Refine" step.
        - Clearly distinguish between numeric filtering ("Filter") and
           semantic refinement using lyrics and context ("Refine").
        - Include "Create_Recommendation_Table"  if user requests or implies wanting
          recommendations formatted as a table or playlist.
        - Include "Retrieve_and_Convert" only if if config.FRONTEND_MODE is False and
          requested or implied by the user's prompt.
        - Always include "Summarize" at the end if playlist was created by
          Create_Recommendation_Table or Retrieve_and_Convert actions.


        Examples:

        config.FRONTEND_MODE=True:
        1. Analyze into numeric parameters.
        2. Filter numerically.
        3. Refine semantically (if required).
        4. Create_Recommendation_Table.

        config.FRONTEND_MODE=False:
        1. Analyze into numeric parameters.
        2. Filter numerically.
        3. Refine semantically (if required explicitly).
        4. Create_Recommendation_Table.
        5. Retrieve_and_Convert (optional).

        Return numbered list of actions.
        """
        )

        user_message = HumanMessage(content=user_prompt)
        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_action_structuring_prompt(self, textual_plan):
        """
        Convert a textual action plan from the LLM into a structured JSON format
        defining actions for the FitBeat agent.

        :param textual_plan: String containing a numbered textual action plan.
        :return: ChatPromptTemplate ready to use for structuring action JSON.
        """

        system_message = SystemMessage(
            content="""
        You're an assistant converting a textual action plan into structured
        JSON actions for the FitBeat agent.

        Available actions defined:
        - "Analyze": interpret emotional descriptions into numeric audio parameters.
        - "Filter": filter tracks based on numeric audio parameters.
        - "Refine": perform semantic refinement using RAG
                    (lyrics, emotions, semantic context).
        - "Create_Recommendation_Table" - create a table with selected tracks.
        - "Retrieve_and_Convert": retrieve tracks from YouTube and convert
                                  them to MP3 format.
        - "Summarize": summarize the final playlist.

        Instructions given:
        - Include each action AT MOST ONCE.
        - List actions ONLY IF explicitly mentioned in provided plan.
        - Do NOT insert, reorder, or assume actions not stated.
        - Collapse multiple occurrences of same action into single instance.

        Return ONLY valid JSON, no additional text:
        {
          "actions": ["Action1", "Action2", "..."]
        }
        """
        )
        user_message = HumanMessage(
            content=f"Convert this plan into structured JSON:\n\n{textual_plan}"
        )
        return ChatPromptTemplate.from_messages([system_message, user_message])

    def construct_refined_prompt(self, user_prompt, refined_tracks_context):
        """
        Constructs a refined prompt for semantic track ranking using RAG.

        This method creates a detailed prompt combining:
            1. The user's original emotional or situational request.
            2. Semantic context retrieved for each candidate track
               (lyrics, descriptions, etc.).

        The constructed prompt instructs the LLM to:
            - Rank all candidate tracks from most suitable to least suitable.
            - Ensure no track is omitted and no duplicates appear.
            - Respond in a structured JSON format suitable for parsing.

        Parameters:
            user_prompt (str):
                The original emotional or situational description provided by the user.

            refined_tracks_context (list of dict):
                List of dictionaries containing semantic contexts for each track.
                Each dictionary  includes:
                    {
                        'artist': Artist name,
                        'track_name': Track track_name,
                        'context': Semantic context(lyrics/descriptions),
                                    or None if unavailable.
                    }

        Returns:
            ChatPromptTemplate:
                A formatted prompt ready to be sent to an LLM, containing:
                    - User's original request.
                    - Semantic context for each candidate track.
                    - Clear, explicit instructions for generating a structured,
                      ranked response.
        """

        context_text = "\n".join(
            [
                (
                    f"{i + 1}. {track['artist']} - {track['track_name']}:"
                    f"\n{track['context'][:500]}..."
                    if track["context"]
                    else f"{i + 1}. {track['artist']} - {track['track_name']}:"
                    f" No additional context."
                )
                for i, track in enumerate(refined_tracks_context)
            ]
        )

        augmented_prompt = f"""
        Given the user's request: '{user_prompt}',
        and given the candidate tracks with their lyrics/descriptions provided below:

        {context_text}

        Perform the following instructions precisely:

        1. Rank ALL tracks listed above from MOST suitable to LEAST suitable
           according to how closely each matches the user's request.
        2. Do NOT omit any track explicitly—include every track listed exactly once.
        3. Ensure there are NO DUPLICATES in your final ranked list.
        4. Return ONLY this valid JSON format with no additional explanations or text:

        {{
            "ranked_playlist": [
                {{"artist": "Artist1", "track_name": "track_name1"}},
                {{"artist": "Artist2", "track_name": "track_name2"}},
                ...
            ],
            "summary": "short_summary_for_folder_name"
        }}
        """

        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="You're an expert music recommender "
                    "ranking candidate track."
                    " Follow instructions exactly."
                ),
                HumanMessage(content=augmented_prompt),
            ]
        )


if __name__ == "__main__":
    import json

    from llm_executor import LLMExecutor

    prompt_engineer = PromptEngineer()
    llm_executor = LLMExecutor()

    # Scenario 1. Analyze → Filter → Retrieve_and_Convert → Summarize
    # user_prompt = "music for romantic date"

    # Scenario 2. Analyze → Filter → RAG → Retrieve_and_Convert → Summarize
    # user_prompt = ("playlist for romantic date, tracks with deeply"
    #                " meaningful and romantic lyrics")

    # Scenario 3: Retrieve_and_Convert → Summarize
    user_prompt = (
        "I already have a list of specific songs:\n"
        "- The Weeknd - Blinding Lights\n"
        "- Eminem - Lose Yourself\n"
        "- Coldplay - Adventure of a Lifetime\n\n"
        "Just download these exact songs from YouTube, convert them to mp3, "
        "and summarize the resulting playlist. "
        "No additional analysis or recommendations are needed."
    )

    planning_prompt = prompt_engineer.construct_planning_prompt(user_prompt)
    messages = planning_prompt.format_messages(user_prompt=user_prompt)

    textual_plan = llm_executor.execute(messages)

    print("\nStep 1 - Explicit Plan (Text):\n", textual_plan)

    # Step 2: Convert explicit plan into structured actions JSON
    structuring_prompt = prompt_engineer.construct_action_structuring_prompt(
        textual_plan
    )
    messages_json = structuring_prompt.format_messages(textual_plan=textual_plan)
    structured_actions = llm_executor.execute(messages_json)

    print(
        "\nStep 2 - Structured Actions (JSON):\n",
        json.dumps(structured_actions, indent=2),
    )
