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
            "Filter": self.search_for_tracks,
            "Retrieve": self.fetch_recommended_tracks,
            "Convert": self.fetch_recommended_tracks,  # downloading implicitly includes converting
            "Summarize": self.summarize_results
        }

    def analyze_user_request(self, user_prompt):
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

    def search_for_tracks(self, params, folder_name, num_tracks=10):

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


    def fetch_recommended_tracks(self, tracks, folder_name):
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
        Execute structured actions explicitly from LLM-generated JSON.

        Parameters:
        - actions_list: List of actions explicitly from LLM.
        - user_prompt: User's original prompt.
        - num_tracks: Number of tracks to retrieve (default 10).
        """
        # Variables explicitly shared between actions
        params = folder_name = tracks = None

        for i_a, action in enumerate(actions_list):
            print(f"{i_a+1}. {action}")

            if action == "Analyze":
                params, folder_name = self.analyze_user_request(user_prompt)

            elif action == "Filter":
                if params is None:
                    print("Error: Analyze step missing before Filter.")
                    return
                tracks = self.search_for_tracks(params, folder_name, num_tracks)

                if tracks.empty:
                    print("No tracks found during filtering.")
                    return

                # Semantic refinement
                print("Refining using RAG explicitly ...")
                refined_tracks_context = self.refine_tracks_with_semantic_retrieval(tracks)

                refined_prompt = self.prompt_engineer.construct_refined_prompt(user_prompt, refined_tracks_context)
                messages = refined_prompt.format_messages(user_prompt=user_prompt)

                refined_llm_response = self.llm_executor.execute(messages)
                ranked_playlist, refined_folder_name = self.parser.parse_ranked_playlist(refined_llm_response)

                if ranked_playlist:
                    print("Ranked Playlist:", ranked_playlist)
                    tracks = self.filter_tracks_by_ranking(tracks, ranked_playlist)
                else:
                    print("No refined ranking received, continuing with original tracks.")

                folder_name = refined_folder_name if refined_folder_name else folder_name


            elif action == "Retrieve":
                if tracks is None:
                    print("Error: Filter step missing before Retrieve.")
                    return

                if refined_folder_name is None:
                    print("Refined folder name is None, falling back to original folder_name.")
                    refined_folder_name = folder_name
                self.fetch_recommended_tracks(tracks, refined_folder_name)

            elif action == "Convert":
                print("Conversion already performed during 'Retrieve' step. Skipping redundant execution.")

            elif action == "Summarize":
                if tracks is None:
                    print("Error: No tracks explicitly available to summarize.")
                    return
                self.summarize_results(tracks)

            else:
                print(f"Error: Unknown action '{action}' encountered.")
                return

        print("\nAll actions executed successfully!")

    def filter_tracks_by_ranking(self, original_tracks, ranked_playlist):

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


    def refine_tracks_with_semantic_retrieval(self, tracks, top_k=3):
        refined_tracks = []
        for idx, track in tracks.iterrows():
            artist = track['artists'].split(';')[0].strip()
            title = track['track_name']

            print(f"Retrieving semantic context for: {artist} - {title}")

            song_text = retrieve_or_add_song(artist, title)

            if song_text:
                print(f"Semantic context retrieved for {title}, refining recommendations...")
                refined_tracks.append({
                    'artist': artist,
                    'title': title,
                    'context': song_text
                })
            else:
                print(f"No semantic context for '{title}'. Proceeding with only numeric filtering.")
                refined_tracks.append({
                    'artist': artist,
                    'title': title,
                    'context': None
                })

        return refined_tracks


# Example Usage
if __name__ == "__main__":
    orchestrator = Orchestrator()

    # planning, single call
    user_prompt = "playlist for birthday party of my 10 years old son"
    user_prompt = "music for intense gym training"
    orchestrator.run_planning_agent( user_prompt, num_tracks = 20)

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
