from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from memory_utils import confirm_clear_memory, save_memory_to_file, load_memory_from_file
from prompt_engineer import PromptEngineer
from llm_executor import LLMExecutor
from output_parser import OutputParser
from track_downloader import TrackDownloader
from extract.extract_file import ExtractFile
from filtering_utils import filter_tracks_by_audio_params
from user_prompt_utils import prompt_to_audio_params
from RAG_semantic_refiner import RAGSemanticRefiner
from playlist_summary import summarize_results
from user_prompt_utils import parse_user_prompt_to_dataframe
import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain.schema.messages import HumanMessage


warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

load_dotenv()

class Orchestrator:
    def __init__(self):
        self.llm_executor = LLMExecutor()
        self.prompt_engineer = PromptEngineer()
        self.parser = OutputParser()
        self.downloader = TrackDownloader()
        self.dataset = ExtractFile().load_data()
        self.filter_tracks_by_audio_params = filter_tracks_by_audio_params
        self.summarize_results = summarize_results
        self.prompt_to_audio_params = prompt_to_audio_params
        self.semantic_refiner = RAGSemanticRefiner()
        self.memory = None
        self.existing_summary = None

        # Initialize model
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)

        # Action mapping
        self.action_mapping = {
            "Analyze": self.prompt_to_audio_params,
            "Filter": self.filter_tracks_by_audio_params,
            "Refine": self.semantic_refiner.refine_tracks_with_rag,
            "Retrieve_and_Convert": self.downloader.retrieve_and_convert,
            "Summarize": self.summarize_results
        }


    def initialize_memory(self):
        # Initialize the LangChain ConversationSummaryMemory
        self.existing_summary = load_memory_from_file()

        if self.existing_summary:
            print(f'\nExisting memory loaded:\n       "{self.existing_summary}"')

            self.memory = ConversationSummaryMemory(llm=self.llm, buffer=self.existing_summary)

            # Check via LLM if current prompt is a new unrelated task
            if self.existing_summary and confirm_clear_memory():
                self.memory.clear()
                print("\nUnrelated task—memory cleared.")
            else:
                print("\nContinuing with existing memory.")

        else:
            self.memory = ConversationSummaryMemory(llm=self.llm)
            #print("\nNo existing memory found—starting fresh.")

    def update_memory(self, user_prompt):
        # Update memory with the latest interaction
        new_summary = self.memory.predict_new_summary(
            self.memory.buffer, [HumanMessage(content=user_prompt)]
        )
        save_memory_to_file(new_summary)
        print("\nMemory updated and saved for future sessions.")


    def create_prompt_with_memory(self, user_prompt):
        # Create prompt using memory context
        memory_context = self.memory.load_memory_variables({})["history"]
        prompt_with_memory = f"{memory_context}\nNew request: {user_prompt}" if memory_context else user_prompt
        if memory_context:
            print(f'\nCombined Prompt (with memory context): \n     "{prompt_with_memory}":\n')
        else:
            print(f'\nUser request: \n     "{prompt_with_memory}":\n')

        return prompt_with_memory


    def run_planning_agent(self, user_prompt, num_tracks=10):

        # Initialize memory
        self.initialize_memory()

        # Create refined prompt using memory context
        prompt_with_memory = self.create_prompt_with_memory(user_prompt)

        # Planning
        print(f'\n# Step 1: LLM is analyzing user request and generating the textual plan of actions...:')
        planning_prompt = self.prompt_engineer.construct_planning_prompt(prompt_with_memory)
        messages_plan = planning_prompt.format_messages(user_prompt=prompt_with_memory)
        textual_action_plan = self.llm_executor.execute(messages_plan)

        if textual_action_plan is None:
            raise ValueError("LLM returned None or invalid response during planning step.")

        print("Textual Plan of Actions:\n", textual_action_plan)

        print("\n\n# Step 2: LLM is converting textual plan of actions to the structured one...")
        structuring_prompt = self.prompt_engineer.construct_action_structuring_prompt(textual_action_plan)
        messages_structured = structuring_prompt.format_messages(explicit_plan=textual_action_plan)
        structured_actions_json = self.llm_executor.execute(messages_structured)

        if structured_actions_json is None or "actions" not in structured_actions_json:
            raise ValueError("LLM returned None or invalid response during structuring actions step.")

        actions_list = structured_actions_json["actions"]
        print("Structured Plan of Actions:\n", structured_actions_json)

        print("\n\n# Step 3: Executing actions...")
        self.execute_actions(actions_list, prompt_with_memory, num_tracks)


        # update memory
        self.update_memory(user_prompt)

    def execute_actions(self, actions_list, user_prompt, num_tracks=10):
        """
            Executes a structured list of actions generated by the LLM-based planning workflow.

            This method orchestrates the end-to-end execution of structured actions derived from a user's request.

            Supported Actions :
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
            print(f"\nAction # {i_a + 1}. {action}")

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






# Example Usage
if __name__ == "__main__":
    orchestrator = Orchestrator()


    # NO MEMORY SCENARIOS, ANSWER "NO" asked whether to use memory or not
    # Scenario 1: Analyze → Filter → Retrieve_and_Convert → Summarize
    #user_prompt = "music for romantic date"

    # Scenario 2: Analyze → Filter → Refine → Retrieve_and_Convert → Summarize
    #user_prompt = "playlist for romantic date, tracks with deeply meaningful and romantic lyrics"


    # Scenario 3:
    # user_prompt = (
    #     "I already have a list of specific songs:\n"
    #     "- The Weeknd - Blinding Lights\n"
    #     "- Eminem - Lose Yourself\n"
    #     "- Coldplay - Adventure of a Lifetime\n\n"
    #     "Just download these exact songs from YouTube, convert them to mp3, "
    #     "and summarize the resulting playlist. No additional analysis or recommendations are needed."
    # )

    # Scenario 4: memory
    # first run with
    user_prompt = "playlist for romantic date, tracks with deeply meaningful and romantic lyrics"
    # next run
    #user_prompt = "I forgot to say that we would probably dance during our date"


    orchestrator.run_planning_agent(user_prompt, num_tracks=10)



