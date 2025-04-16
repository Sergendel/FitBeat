from dotenv import load_dotenv
from prompt_engineer import PromptEngineer
from llm_executor import LLMExecutor
from output_parser import OutputParser
from track_downloader import TrackDownloader
from extract.extract_file import ExtractFile
from src.filtering_logic import filtering_logic
from corpus.embeddings.semantic_retrieval import retrieve_or_add_song
import os
import config
import pandas as pd
import re

load_dotenv()

class Orchestrator:
    def __init__(self):
        self.prompt_engineer = PromptEngineer()
        self.llm_executor = LLMExecutor()
        self.parser = OutputParser()
        self.downloader = TrackDownloader()
        extractor = ExtractFile()
        self.dataset = extractor.load_data()

        # Action mapping
        self.action_mapping = {
            "Analyze": self.analyze_user_request,
            "Filter": self.filter_tracks_by_audio_params,
            "Refine": self.refine_tracks,
            "Retrieve_and_Convert": self.retrieve_and_convert,
            "Summarize": self.summarize_results
        }

    def analyze_user_request(self, user_prompt):
        """
            Analyze user's emotional or situational prompt to derive numeric audio parameters.

            :param user_prompt: user prompt (str).
            :return: (params: dict, folder_name: str)
        """

        print(f'\nAnalyzing user prompt "{user_prompt}" to derive numeric audio parameters...\n')
        prompt_template = self.prompt_engineer.construct_prompt(user_prompt)
        messages = prompt_template.format_messages(user_prompt=user_prompt)
        llm_response = self.llm_executor.execute(messages)

        if llm_response is None:
            raise ValueError("LLM returned None or invalid response during analyze step.")

        params, folder_name = self.parser.parse_response(llm_response)
        return params, folder_name

    def analyze_user_request_with_memory(self, user_prompt):

        # Retrieve previous user prompts from memory
        previous_messages = self.llm_executor.memory.chat_memory.messages
        if previous_messages:
            # Get last user prompt
            last_user_message = next(
                (m.content for m in reversed(previous_messages) if m.type == 'human'), None)
            combined_prompt = (
                f"Previously, the user requested: '{last_user_message}'. "
                f"Now, the user requests: '{user_prompt}'. "
                f"Generate numeric audio parameters suitable for this new, combined request."
            )
            print(f'\nAnalyzing combined user prompt (with memory context):\n"{combined_prompt}"\n')
        else:
            combined_prompt = user_prompt

        print(f'\nAnalyzing user prompt "{user_prompt}" to derive numeric audio parameters...\n')

        prompt_template = self.prompt_engineer.construct_prompt(combined_prompt)
        messages = prompt_template.format_messages(user_prompt=combined_prompt)
        llm_response = self.llm_executor.execute(messages)
        params, folder_name = self.parser.parse_response(llm_response)
        return params, folder_name

    def filter_tracks_by_audio_params(self, params, folder_name, num_tracks=10):
        """
            Filters tracks from the Kaggle dataset based on numeric audio parameters derived from user input.

            Parameters:
                params (dict):
                    Dictionary containing numeric audio parameter ranges or values.

                folder_name (str):
                    Name used for storing tracks and associated outputs resulting from this filtering step.

                num_tracks (int, optional, default=10):
                    Maximum number of tracks to retrieve from numeric filtering.

            Returns:
                pd.DataFrame:
                    DataFrame containing tracks that match numeric filtering criteria,
                    including columns such as:
                        - 'track_name': Title of the track.
                        - 'artists': Artist name(s).
                        - 'popularity', 'tempo', 'explicit', 'danceability', 'energy', etc.

                    If no tracks match criteria, returns an empty DataFrame.
        """
        filtered_tracks = filtering_logic(params, self.dataset, num_tracks)

        if filtered_tracks.empty:
            print("No tracks match criteria.")
            return filtered_tracks

        print("\nParameters provided by LLM for tracks filtering:")
        for key, value in params.items():
            print(f"  - {key.capitalize()}: {value}")

        print("\nSearching Kaggle dataset for matching tracks...")
        unique_tracks_count = filtered_tracks[['track_name', 'artists']].drop_duplicates().shape[0]

        print(f"\n {unique_tracks_count} Selected Tracks :")
        for idx, row in filtered_tracks.iterrows():
            print(f"    -{idx} {row['track_name']} – {row['artists']}")
            # print(f"   • Tempo: {row['tempo']}")
            # print(f"   • Energy: {row['energy']}")
            # print(f"   • Danceability: {row['danceability']}")
            # print(f"   • Valence: {row['valence']}")
            # print(f"   • Loudness: {row['loudness']} dB")
            # print(f"   • Speechiness: {row['speechiness']}")
            # print(f"   • Instrumentalness: {row['instrumentalness']}")
            # print(f"   • Acousticness: {row['acousticness']}")
            # print(f"   • Liveness: {row['liveness']}")
            # print(f"   • Genre: {row['track_genre']}")
            # print(f"   • Popularity: {row['popularity']}")

        print(
            f"\nThe tracks will be stored in the folder '{folder_name}'.\n")

        return filtered_tracks

    def refine_tracks(self, user_prompt, tracks, folder_name):
        """
           Performs semantic refinement using RAG based on lyrics and song context.

           This method retrieves semantic context (lyrics, descriptions) for each track, then uses an LLM
           to rank the tracks according to their semantic relevance to the user's original emotional or situational description.
           It  matches and reorders the original tracks DataFrame based on this semantic ranking.

           Parameters:
               user_prompt (str):
                   The user's original request.

               tracks (pd.DataFrame):
                   DataFrame containing tracks initially selected via numeric filtering.
                   Must include columns:
                       - 'track_name': Title of the track.
                       - 'artists': Artist(s) associated with the track.
                       - Additional numeric metadata from the original dataset.

               folder_name (str):
                   Name of the folder used to store the tracks and related outputs.
                   Can be updated if the semantic refinement step provides a more suitable name.

           Returns:
               tuple: (tracks (pd.DataFrame), folder_name (str)):
                   - tracks: DataFrame filtered and reordered based on semantic relevance.
                   - folder_name: Updated folder name provided by the semantic refinement step.
                                  Defaults to the original folder name if no update is provided.

            Refinement Steps:
               1. Retrieves semantic context (lyrics, descriptions) for each track.
               2. Constructs and sends a prompt to an LLM to rank tracks semantically.
               3. Parses ranked tracks provided by the LLM.
               4. Explicitly filters and reorders original tracks according to semantic ranking.

           Error Handling :
               - Handles cases where semantic context is unavailable (proceeds without context).
               - Logs errors or issues encountered during semantic refinement.
               - Ensures robust handling of missing tracks or failed LLM responses.
           """
        refined_tracks_context = self.retrieve_semantic_context(tracks)
        refined_prompt = self.prompt_engineer.construct_refined_prompt(user_prompt, refined_tracks_context)
        messages = refined_prompt.format_messages(user_prompt=user_prompt)
        ranked_playlist, refined_folder_name = self.parser.parse_ranked_playlist(self.llm_executor.execute(messages))

        if ranked_playlist:
            tracks = self.reorder_tracks_by_semantic_ranking(tracks, ranked_playlist)
            folder_name = refined_folder_name or folder_name
            print("✅ Refinement (RAG) explicitly completed successfully!")
        else:
            print("⚠️ Refinement explicitly failed; proceeding with original tracks.")

        return tracks, folder_name


    def retrieve_and_convert(self, tracks, folder_name):
        """
            Retrieves audio tracks from YouTube and converts them to MP3 format.

            Parameters:
                tracks (pd.DataFrame): Tracks to retrieve and convert.
                folder_name (str): Folder name for storing MP3 files.

            Returns:
                None

            Notes:
                - Skips downloading if a track file already exists.
                - Logs each successful download and conversion.
        """
        folder_path = os.path.join(config.TRACKS_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        print(f"Downloading recommended tracks explicitly and converting to MP3 explicitly.\n"
              f"Saving explicitly playlist to folder explicitly: '{folder_path}'\n")

        for idx, track in enumerate(tracks.itertuples()):
            track_number = idx + 1
            self.downloader.download_and_convert(
                track.track_name,
                track.artists,
                folder_path,
                track_index=track_number
            )

    def summarize_results(self, tracks):
        """
            Generates and displays a summary of the final playlist recommendations.

            This method prints each recommended track, including metadata (popularity, tempo,energy,...).

            Parameters:
                tracks (pd.DataFrame):
                    DataFrame containing tracks recommended by previous numeric filtering and/or semantic refinement actions.
                    Must include columns such as:
                        - 'track_name': Track title.
                        - 'artists': Artist name(s).
                        - 'popularity': Numeric popularity rating.
                        - 'tempo': Track tempo in BPM.
                        - 'explicit': Boolean indicating presence of explicit lyrics.
                        - 'danceability', 'energy', 'loudness', 'mode', 'speechiness', 'acousticness',
                          'instrumentalness', 'liveness', 'valence', 'time_signature', 'track_genre':
                          Additional audio and metadata fields explicitly from dataset.

            Returns:
                None:
        """
        print("\nFinal Recommendations:")
        for track_number, (_, row) in enumerate(tracks.iterrows()):
            print(f"{track_number}. {row['track_name']} by {row['artists']} | "
                  f"    \n   Popularity: {row['popularity']} | "
                  f"Tempo: {row['tempo']} BPM | "
                  f"Explicit: {row['explicit']} | "
                  f"Danceability: {row['danceability']} | "
                  f"Energy: {row['energy']} | "
                  f"Loudness: {row['loudness']} dB | "
                  f"Mode: {'Major' if row['mode'] == 1 else 'Minor'} | "
                  f"Speechiness: {row['speechiness']} | "
                  f"Acousticness: {row['acousticness']} | "
                  f"Instrumentalness: {row['instrumentalness']} | "
                  f"Liveness: {row['liveness']} | "
                  f"Valence: {row['valence']} | "
                  f"Time Signature: {row['time_signature']} | "
                  f"Genre: {row['track_genre']}\n")

    def execute_actions(self, actions_list, user_prompt, num_tracks=10):
        """
            Executes a structured list of actions generated by the LLM-based planning workflow.

            This method orchestrates the end-to-end execution of structured actions derived from a user's request.

            Supported Actions Explicitly:
                - "Analyze": Converts user's prompt into numeric audio parameters.
                - "Filter": Filters tracks based on numeric audio parameters.
                - "Refine": Performs semantic refinement using lyrics and semantic context (RAG).
                - "Retrieve_and_Convert": Downloads tracks from YouTube and converts them to MP3.
                - "Summarize": Summarizes and displays the final playlist results.

            Parameters:
                actions_list (list of str):
                    A structured,ordered list of actions to perform.

                user_prompt (str):
                    The user's original prompt.

                num_tracks (int, optional, default=10):
                    Maximum number of tracks.

            Returns:
                None:
        """

        params = folder_name = tracks = None

        for i_a, action in enumerate(actions_list):
            print(f"{i_a+1}. {action}")

            action_method = self.action_mapping.get(action)
            if not action_method:
                print(f"❌ Error: Unknown action '{action}'.")
                return

            # Explicitly invoke the action method with appropriate parameters:
            if action == "Analyze":
                params, folder_name = action_method(user_prompt)

            elif action == "Filter":
                if params is None:
                    print("❌ Error: 'Analyze' step missing.")
                    return
                tracks = action_method(params, folder_name, num_tracks)

            elif action == "Refine":
                if tracks is None or tracks.empty:
                    print("❌ Error: No tracks to refine.")
                    return
                tracks, folder_name = action_method(user_prompt, tracks, folder_name)

            elif action == "Retrieve_and_Convert":
                if tracks is None:
                    tracks = self.get_user_provided_tracks(user_prompt)
                    folder_name = "user_provided_tracks"
                    if tracks.empty:
                        print("❌ Error: No valid tracks explicitly provided by user.")
                        return
                action_method(tracks, folder_name)

            elif action == "Summarize":
                if tracks is None or tracks.empty:
                    print("❌ Error: No tracks to summarize.")
                    return
                action_method(tracks)

        print("\n✅ All actions executed explicitly and successfully!")


    def get_user_provided_tracks(self, user_prompt):
        """
           Extracts track and artist names provided directly by the user in the prompt text.

           User prompt must list tracks in the following format:
               - Artist - Track Name

           Parameters:
               user_prompt (str):
                   The user's text input containing a list of tracks and artists.

           Returns:
               pd.DataFrame:
                   DataFrame containing the extracted tracks with columns such as:
                       - 'artists': Artist name provided by the user.
                       - 'track_name': Track title provided by the user.
                       - Other metadata fields  set to None (placeholders).

           Notes:
               - Handles cases where no valid tracks are provided.
               - Logs a message indicating the number of tracks identified.
        """
        lines = user_prompt.strip().split("\n")
        tracks = []

        for line in lines:
            line = line.strip()
            if line.startswith("-"):
                line_content = line[1:].strip()
                if " - " in line_content:
                    artist, title = line_content.split(" - ", 1)
                    tracks.append({
                        'artists': artist.strip(),
                        'track_name': title.strip(),
                        'popularity': None,  # explicitly placeholder
                        'tempo': None,
                        'explicit': None,
                        'danceability': None,
                        'energy': None,
                        'loudness': None,
                        'mode': None,
                        'speechiness': None,
                        'acousticness': None,
                        'instrumentalness': None,
                        'liveness': None,
                        'valence': None,
                        'time_signature': None,
                        'track_genre': None
                    })

        if not tracks:
            print("⚠️ No explicitly provided tracks found in user prompt.")
        else:
            print(f"✅ Found {len(tracks)} explicitly user-provided tracks.")

        return pd.DataFrame(tracks)

    def reorder_tracks_by_semantic_ranking(self, original_tracks, ranked_playlist):
        """
            Reorders the original set of tracks based on a ranked playlist provided by the LLM.

            This method matches tracks obtained from numeric filtering with the semantic rankings
            provided by RAG. Matching is performed using normalized track titles and artist names
            to ensure robustness against case differences and extra spaces.

            Parameters:
                original_tracks (pd.DataFrame):
                    DataFrame containing tracks selected from numeric filtering.
                    Expected columns include at least:
                        - 'track_name': Original track title.
                        - 'artists': Artist(s) associated with the track.
                        - Additional numeric and metadata columns (e.g., tempo, energy).

                ranked_playlist (list of dict):
                    Provided list of tracks from the semantic refinement step.
                    Each dictionary must include:
                        {
                            'artist': 'artist_name',
                            'title': 'track_title'
                        }

            Returns:
                pd.DataFrame:
                    A DataFrame containing tracks filtered and reordered according
                    to the ranked playlist. Includes all metadata columns originally present in
                    the 'original_tracks' DataFrame.

                    - Matches tracks using normalized 'artist' and 'title' fields.
                    - Removes duplicates to maintain uniqueness.
                    - Logs any tracks from 'ranked_playlist' that couldn't be matched.

        """

        # Normalize titles and artist names for robust matching
        ranked_df = pd.DataFrame(ranked_playlist)
        ranked_df['title'] = ranked_df['title'].str.lower().str.strip()
        ranked_df['artist'] = ranked_df['artist'].str.lower().str.strip()

        original_tracks['normalized_title'] = original_tracks['track_name'].str.lower().str.strip()
        original_tracks['normalized_artist'] = original_tracks['artists'].str.lower().str.split(';').str[0].str.strip()

        filtered_df = pd.merge(ranked_df, original_tracks,
                               left_on=['title', 'artist'],
                               right_on=['normalized_title', 'normalized_artist'],
                               how='inner')

        filtered_df = filtered_df.drop_duplicates(subset=['track_name', 'artists'])

        # Check for tracks missing after merge:
        missing_tracks = set(ranked_df['title']) - set(filtered_df['normalized_title'])
        if missing_tracks:
            print(f"Missing tracks after merge: {missing_tracks}")

        return filtered_df

    def run_planning_agent(self, user_prompt, num_tracks=10):
        """
            Runs the complete FitBeat action-planning workflow based on a user-provided prompt.

            This method orchestrates three main steps:

                1. **Planning (Textual)**: Uses an LLM to generate a clear, human-readable textual plan of actions.

                2. **Structuring Actions**: Converts the textual plan into structured JSON actions (e.g., Analyze, Filter, Refine, Retrieve_and_Convert, Summarize).

                3. **Executing Actions**: Executes each structured action sequentially, ensuring robust handling of each step's dependencies.

            Parameters:
                user_prompt (str):
                    The user's description requesting music recommendations, or a direct instruction for track retrieval.

                num_tracks (int, optional, default=10):
                    Specifies the maximum number of tracks.

            Returns:
                None:
            """

        print(f'\n# Step 1: Analyzing user prompt "{user_prompt}". Generating explicit plan of actions...')
        planning_prompt = self.prompt_engineer.construct_planning_prompt(user_prompt)
        messages_plan = planning_prompt.format_messages(user_prompt=user_prompt)
        explicit_plan_text = self.llm_executor.execute(messages_plan)

        if explicit_plan_text is None:
            raise ValueError("LLM returned None or invalid response during planning step.")

        print("Plan of actions:\n", explicit_plan_text)

        print("\n# Step 2: Converting plan to structured actions...")
        structuring_prompt = self.prompt_engineer.construct_action_structuring_prompt(explicit_plan_text)
        messages_structured = structuring_prompt.format_messages(explicit_plan=explicit_plan_text)
        structured_actions_json = self.llm_executor.execute(messages_structured)

        if structured_actions_json is None or "actions" not in structured_actions_json:
            raise ValueError("LLM returned None or invalid response during structuring actions step.")

        actions_list = structured_actions_json["actions"]
        print("Structured Actions:\n", structured_actions_json)

        print("\n\n# Step 3: Executing actions explicitly...")
        self.execute_actions(actions_list, user_prompt, num_tracks)

    def retrieve_semantic_context(self, tracks):

        """
            Retrieves semantic context (lyrics and descriptions) for a provided list of tracks.

            This method interacts with a semantic corpus (via Genius API) to fetch lyrics and detailed descriptions
            of each track, enriching numeric-filtered tracks with meaningful textual context required for semantic refinement.

            Parameters:
                tracks (pd.DataFrame):
                    DataFrame containing tracks for which semantic context will be retrieved.
                    Must include columns:
                        - 'track_name': Title of the track.
                        - 'artists': Artist(s) associated with the track.

            Returns:
                list of dict:
                    Returns a list of dictionaries, each containing:
                        {
                            'artist': Artist name explicitly from the original track,
                            'title': Track title explicitly from the original track,
                            'context': Explicit textual semantic context (lyrics, description).
                                       None explicitly if no context was found.
                        }

            """

        semantic_contexts = []
        for idx, track in tracks.iterrows():
            artist = track['artists'].split(';')[0].strip()
            title = track['track_name']

            print(f"Retrieving semantic context explicitly for: {artist} - {title}")

            song_text = retrieve_or_add_song(artist, title)

            if song_text:
                print(f"✅ Semantic context explicitly retrieved for '{title}'.")
                semantic_contexts.append({
                    'artist': artist,
                    'title': title,
                    'context': song_text
                })
            else:
                print(f"⚠️ No semantic context explicitly found for '{title}'. Proceeding without semantic context.")
                semantic_contexts.append({
                    'artist': artist,
                    'title': title,
                    'context': None
                })

        return semantic_contexts


# Example Usage
if __name__ == "__main__":
    orchestrator = Orchestrator()

    # Scenario 1: Analyze → Filter → Retrieve_and_Convert → Summarize
    #user_prompt = "music for romantic date"

    # Scenario2: Analyze → Filter → Refine → Retrieve_and_Convert → Summarize
    user_prompt = "playlist for romantic date, tracks with deeply meaningful and romantic lyrics"


    # # Scenario 3:
    # user_prompt = (
    #     "I already have a list of specific songs:\n"
    #     "- The Weeknd - Blinding Lights\n"
    #     "- Eminem - Lose Yourself\n"
    #     "- Coldplay - Adventure of a Lifetime\n\n"
    #     "Just download these exact songs from YouTube, convert them to mp3, "
    #     "and summarize the resulting playlist. No additional analysis or recommendations are needed."
    # )

    orchestrator.run_planning_agent(user_prompt, num_tracks=10)









# # planning, test different scenarios
    # user_prompt = (
    #     "I already have a list of songs. I want playlist with similar, but other, songs "
    #     "Can you do it for me ? I just need track names, not the playable files"
    # )  # good!
    # orchestrator.run_planning_agent(user_prompt, num_tracks=20)



    # # test memory:
    # user_prompt_1 = "music tracks suitable for dancing"
    # orchestrator.run_planning_agent(user_prompt_1, num_tracks=10)
    #
    # # Second prompt explicitly tests memory explicitly
    # user_prompt_2 = "Now give me something slower and more relaxing."
    # orchestrator.run_planning_agent(user_prompt_2, num_tracks=10)



    # user_prompt = (
    #     "I already have a list of songs. "
    #     "Can you just find these exact tracks on YouTube, download and convert them to mp3, "
    #     "and then summarize the results for me?"
    # )

    # user_prompt = (
    #     "I already have a list of songs. "
    #     "Can you prepare a payable playlist with these songs for me  ?"
    # )  # tries to find common featires and creates new playlist

    # user_prompt = (
    #     "I already have a list of specific songs. "
    #     "Just download these exact songs from YouTube, convert them to mp3, and summarize the resulting playlist. "
    #     "No additional analysis or recommendations are needed."
    # )  # works but too simple

    # user_prompt = (
    #     "I already have a list of songs. "
    #     "Can you prepare a payable playlist with these songs for me  ?"
    #     "No additional analysis or recommendations are needed."
    # )  # GOOD

    # user_prompt = (
    #     "I already have a list of songs. I want playlist with similar, but other, songs "
    #     "Can you do it for me ?"
    # )  # good!

    # user_prompt = (
    #     "I already have a list of songs. I want playlist with similar, but other, songs "
    #     "Can you do it for me ? I just need track names, not the playable files"
    # )  # good!
    #
    # user_prompt = "music tracks suitable for studying for exams"
