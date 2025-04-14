from dotenv import load_dotenv
from prompt_engineer import PromptEngineer
from llm_executor import LLMExecutor
from output_parser import OutputParser
from track_downloader import TrackDownloader
from extract.extract_file import ExtractFile
from src.explicit_filtering_logic import explicit_filtering_logic


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


    def search_for_tracks(self, params, folder_name, num_tracks=10):

        filtered_tracks = explicit_filtering_logic(params, self.dataset, num_tracks)

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
        print(f"Downloading recommended tracks and converting to MP3.\n"
              f"Saving playlist to folder: '{folder_name}'\n")
        for _, track in tracks.iterrows():
            self.downloader.download_and_convert(track['track_name'], track['artists'], folder_name)

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

    def run_agent(self, user_prompt, num_tracks=10):
        # Step-by-step  workflow:
        params, folder_name = self.analyze_user_request(user_prompt)

        tracks = self.search_for_tracks(params, folder_name, num_tracks)
        if tracks.empty:
            print("Failed to find matching tracks after relaxing parameters.")
            return

        self.fetch_recommended_tracks(tracks, folder_name)
        self.summarize_results(tracks)


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

            elif action == "Retrieve":
                if tracks is None:
                    print("Error: Filter step missing before Retrieve.")
                    return
                self.fetch_recommended_tracks(tracks, folder_name)

            elif action == "Convert":
                print("Conversion already performed during 'Retrieve' step. Skipping redundant execution.")

            elif action == "Summarize":
                if tracks is None:
                    print("Error: No tracks explicitly available to summarize.")
                    return
                self.summarize_results(tracks)

            else:
                print(f"Error: Unknown action '{action}' explicitly encountered.")
                return

        print("\nAll actions executed explicitly and successfully!")

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


# Example Usage
if __name__ == "__main__":
    orchestrator = Orchestrator()

    # simple
    # user_prompt = "music tracks for dancing party for 50+ years old "
    # orchestrator.run_agent(user_prompt, num_tracks=10)


    # planning
    user_prompt = "music tracks suitable for studying "
    orchestrator.run_planning_agent( user_prompt, num_tracks=10)


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
