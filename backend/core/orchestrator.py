import warnings

from dotenv import load_dotenv
from langchain_core._api.deprecation import LangChainDeprecationWarning

from backend import config
from backend.core.filtering_utils import filter_tracks_by_audio_params
from backend.core.llm_executor import LLMExecutor
from backend.core.memory_manager import MemoryManager
from backend.core.output_parser import OutputParser
from backend.core.playlist_utils import YouTubeSearcher
from backend.core.prompt_engineer import PromptEngineer
from backend.core.rag_semantic_refiner import RAGSemanticRefiner
from backend.core.track_downloader import TrackDownloader
from backend.core.user_prompt_utils import (
    parse_user_prompt_to_dataframe,
    prompt_to_audio_params,
)
from backend.data_management.extract.extract_file import ExtractFile

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

load_dotenv()


class Orchestrator:
    def __init__(
        self,
        open_ai_key=None,
        genius_api_key=None,
        youtube_api_key=None,
        clear_memory=None,
    ):
        self.clear_memory = clear_memory
        self.llm_executor = LLMExecutor(open_ai_key=open_ai_key)
        self.prompt_engineer = PromptEngineer()
        self.parser = OutputParser()
        self.downloader = TrackDownloader()
        self.dataset = ExtractFile().load_data()
        self.filter_tracks_by_audio_params = filter_tracks_by_audio_params
        self.prompt_to_audio_params = prompt_to_audio_params
        self.semantic_refiner = RAGSemanticRefiner(
            llm_executor=self.llm_executor,
            open_ai_key=open_ai_key,
            genius_api_key=genius_api_key,
        )
        self.memory = None
        self.existing_summary = None

        # memory
        self.memory_manager = MemoryManager()

        # YouTube searcher
        self.YouTubeSearcher = YouTubeSearcher(youtube_api_key=youtube_api_key)
        self.create_recommendation_table = (
            self.YouTubeSearcher.create_recommendation_table
        )
        self.summarize_results = self.YouTubeSearcher.summarize_results

        # Action mapping
        self.action_mapping = {
            "Analyze": self.prompt_to_audio_params,
            "Filter": self.filter_tracks_by_audio_params,
            "Refine": self.semantic_refiner.hybrid_refine_tracks,
            "Retrieve_and_Convert": self.downloader.retrieve_and_convert,
            "Create_Recommendation_Table": self.create_recommendation_table,
            "Summarize": self.summarize_results,
        }

    def run_planning_agent(self, user_prompt, num_tracks=20):

        print("\n\n" + "#" * 100)
        print(
            "### Step 1: Loading existing memory (if available) "
            "and constructing the combined prompt:"
        )
        # Initialize memory
        self.memory_manager.initialize_memory(clear_memory=self.clear_memory)

        # Create refined prompt using memory context
        prompt_with_memory = self.memory_manager.create_prompt_with_memory(user_prompt)

        # Planning
        print("\n\n" + "#" * 100)
        print(
            "### Step 2: LLM is analyzing user request and generating the "
            "textual plan of actions...:"
        )
        planning_prompt = self.prompt_engineer.construct_planning_prompt(
            prompt_with_memory
        )
        messages_plan = planning_prompt.format_messages(user_prompt=prompt_with_memory)
        textual_action_plan = self.llm_executor.execute(messages_plan)

        if textual_action_plan is None:
            raise ValueError(
                "LLM returned None or invalid response during planning step."
            )

        print("\nTextual Plan of Actions:\n", textual_action_plan)

        print("\n\n" + "#" * 100)
        print(
            "### Step 3: LLM is converting textual plan of actions "
            "to the structured one..."
        )
        structuring_prompt = self.prompt_engineer.construct_action_structuring_prompt(
            textual_action_plan
        )
        messages_structured = structuring_prompt.format_messages(
            explicit_plan=textual_action_plan
        )
        structured_actions_json = self.llm_executor.execute(messages_structured)

        if structured_actions_json is None or "actions" not in structured_actions_json:
            raise ValueError(
                "LLM returned None or invalid response during structuring "
                "actions step."
            )

        actions_list = structured_actions_json["actions"]
        print("\nStructured Plan of Actions:\n", structured_actions_json)

        print("\n\n" + "#" * 100)
        print("### Step 4: Executing actions...")

        playlist = self.execute_actions(actions_list, prompt_with_memory, num_tracks)

        # update memory
        self.memory_manager.update_memory(user_prompt)

        return playlist

    def execute_actions(self, actions_list, user_prompt, num_tracks=20):
        """
        Executes a structured list of actions generated by the
        LLM-based planning workflow.

        This method orchestrates the end-to-end execution of structured actions
         derived from a user's request.

        Supported Actions :
            - "Analyze": Converts user's prompt into numeric audio parameters.
            - "Filter": Filters tracks based on numeric audio parameters.
            - "Refine": Performs semantic refinement using lyrics and
                        semantic context (RAG).
            - "Create_Recommendation_Table": Create a table including
                                 Artist names, Track names, and Official YouTube links.
            - "Retrieve_and_Convert": Downloads tracks from YouTube and
                                      converts them to MP3.
            - "Summarize": Summarizes and displays the
                           final playlist results.

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
        playlist = None
        params = folder_name = tracks = None

        for i_a, action in enumerate(actions_list):
            print("\n" + "-" * 50)
            print(f"Action # {i_a + 1}. {action}")

            # Check  frontend_old mode
            if config.FRONTEND_MODE and action == "Retrieve_and_Convert":
                print("Skipping 'Retrieve_and_Convert' due to FRONTEND_MODE=True.")
                continue

            action_method = self.action_mapping.get(action)
            if not action_method:
                print(f"Error: Unknown action '{action}'.")
                return

            # Invoke the action method with appropriate parameters:
            if action == "Analyze":
                params, folder_name = action_method(user_prompt)

            elif action == "Filter":
                if params is None:
                    print("Error: 'Analyze' step missing.")
                    return
                tracks = action_method(self.dataset, params, folder_name, num_tracks)

            elif action == "Refine":
                if tracks is None or tracks.empty:
                    print("Error: No tracks to refine.")
                    return
                tracks, folder_name = action_method(user_prompt, tracks, folder_name)

            elif action == "Create_Recommendation_Table":
                if tracks is None or tracks.empty:
                    print("Error: No tracks available for recommendation table.")
                    return
                playlist = action_method(tracks, folder_name)

            elif action == "Retrieve_and_Convert":
                if tracks is None:
                    tracks = parse_user_prompt_to_dataframe(user_prompt)
                    folder_name = "user_provided_tracks"
                    if tracks.empty:
                        print("Error: No valid tracks  provided by user.")
                        return
                action_method(tracks, folder_name)

            elif action == "Summarize":
                if tracks is None or tracks.empty:
                    print("Error: No tracks to summarize.")
                    return
                action_method(tracks)

        print("\nAll actions executed successfully!")

        return playlist


# Example Usage
if __name__ == "__main__":
    orchestrator = Orchestrator(clear_memory=True)

    # ------------------  NO MEMORY SCENARIOS  ---------------------------

    # user_prompt = "please create a playlist of Canadian songs"

    # Scenario 1: Analyze → Filter → Retrieve_and_Convert → Summarize
    user_prompt = "music for nightmare movie"
    orchestrator.run_planning_agent(user_prompt, num_tracks=20)

    # Scenario 2: Analyze → Filter → Refine → Retrieve_and_Convert → Summarize
    # user_prompt = (
    #     "playlist for romantic date, tracks with deeply meaningful "
    #     "and romantic lyrics, I need playlist and mp3 files"
    # )

    # Scenario 3:
    # user_prompt = (
    #     "I already have a list of specific songs:\n"
    #     "- The Weeknd - Blinding Lights\n"
    #     "- Eminem - Lose Yourself\n"
    #     "- Coldplay - Adventure of a Lifetime\n\n"
    #     "Just download these exact songs from YouTube, convert them to mp3, "
    #     "and summarize the resulting playlist. No additional analysis or "
    #     "recommendations are needed."
    # )

    # ----------------------   MEMORY SCENARIOS   ------------------------------

    # # Scenario 4: memory
    # # first run with
    # user_prompt = "playlist for romantic date, tracks with deeply meaningful "
    # "and romantic lyrics"
    # # next run
    # user_prompt = "I forgot to say that we would probably dance during our date"

    # link:
    # https: // main.dxpisg36o3xzj.amplifyapp.com /

    # Prompt examples:
    # Romantic, soundhealing, mantra
    # Create a high-energy playlist perfect for an intense cardio workout.
    # Suggest calm, relaxing music for evening meditation.
    # Create the perfect playlist for a long summer road trip."
    # Playlist for romantic date, tracks with deeply meaningful and romantic lyrics
    # Suggest songs to match a cozy rainy - day vibe.
    # Generate an energetic playlist for a weekend dance party.
    # Suggest popular hits to get everyone dancing
