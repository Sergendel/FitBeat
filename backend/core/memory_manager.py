import json
import os
import warnings
from pathlib import Path

from dotenv import load_dotenv
from langchain.memory import ConversationSummaryMemory
from langchain.schema.messages import HumanMessage
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_openai import ChatOpenAI

from backend import config

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
load_dotenv()


class MemoryManager:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.0):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.memory = None
        self.existing_summary = None

        if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            # Explicitly use Lambda's ephemeral storage path
            self.MEMORY_FILE_PATH = Path("/tmp/conversation_memory.json")
        else:
            # Explicitly use your local development path
            self.MEMORY_FILE_PATH = config.MEMORY_FILE_PATH

    def initialize_memory(self, clear_memory=None):
        self.existing_summary = self.load_memory_from_file()

        if self.existing_summary:
            print(f'\nExisting memory loaded:\n       "{self.existing_summary}"')

            self.memory = ConversationSummaryMemory(
                llm=self.llm, buffer=self.existing_summary
            )

            if self.confirm_clear_memory(clear_memory=clear_memory):
                self.memory.clear()
                print("\nUnrelated task—memory cleared.")
            else:
                print("\nContinuing with existing memory.")
        else:
            self.memory = ConversationSummaryMemory(llm=self.llm)
            print("\nNo existing memory found—starting fresh.")

    def update_memory(self, user_prompt):
        existing_summary = self.memory.load_memory_variables({})["history"]

        new_summary = self.memory.predict_new_summary(
            messages=[HumanMessage(content=user_prompt)],
            existing_summary=existing_summary,
        )

        self.save_memory_to_file(new_summary)
        print("\nMemory updated and saved for future sessions.")

    def create_prompt_with_memory(self, user_prompt):
        memory_context = self.memory.load_memory_variables({})["history"]
        prompt_with_memory = (
            f"{memory_context}\nNew request: {user_prompt}"
            if memory_context
            else user_prompt
        )
        if memory_context:
            print(
                f"\nCombined Prompt (with memory context): "
                f'\n     "{prompt_with_memory}"\n'
            )
        else:
            print(f'\nUser request: \n     "{prompt_with_memory}"\n')

        return prompt_with_memory

    def save_memory_to_file(self, memory_summary):
        with open(self.MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({"summary": memory_summary}, f)

    def load_memory_from_file(self):
        if self.MEMORY_FILE_PATH.exists():
            with open(self.MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("summary", "")
        else:
            return None

    @staticmethod
    def confirm_clear_memory(clear_memory=None):
        """
        Prompts user to confirm if they start a new unrelated task.
        Returns True if memory should be cleared.
        """
        if os.getenv("GITHUB_ACTIONS") == "true":
            print(
                "GitHub Actions detected. " "Automatically confirming clear memory (y)."
            )
            return True  # explicitly confirm "yes" in GitHub Actions
        else:
            if clear_memory is not None:
                return clear_memory
            else:
                response = (
                    input(
                        "\n***** Do you want to clear previous memory and start a "
                        "new unrelated task? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                return response in ("y", "yes")
