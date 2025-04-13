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

    def analyze_user_request(self, user_prompt):
        print(f'\nAnalyzing user request: "{user_prompt}"  via LLM...\n')
        prompt_template = self.prompt_engineer.construct_prompt(user_prompt)
        messages = prompt_template.format_messages(user_prompt=user_prompt)
        llm_response = self.llm_executor.execute(messages)
        params, folder_name = self.parser.parse_response(llm_response)
        return params, folder_name

    def search_for_tracks(self, params, folder_name, num_tracks=10):

        filtered_tracks = explicit_filtering_logic(params, self.dataset, num_tracks)

        if filtered_tracks.empty:
            print("⚠No tracks match criteria.")
            return filtered_tracks

        print("\nParameters provided by LLM for tracks  filtering:")
        for key, value in params.items():
            print(f"  - {key.capitalize()}: {value}")

        print("\nSearching for relevant tracks in the dataset...")
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

# Example Usage
if __name__ == "__main__":
    orchestrator = Orchestrator()
    user_prompt = "music tracks for dancing party for 50+ years old "
    orchestrator.run_agent(user_prompt, num_tracks=10)
