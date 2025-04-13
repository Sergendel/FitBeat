import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from langchain.schema import SystemMessage, HumanMessage, AIMessage

class LLMExecutor:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.2):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY is not set in your .env file")

        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature

    def execute(self, messages):
        """
        Sends formatted LangChain messages directly to the LLM.

        Parameters:
        - messages (list): List of structured messages (SystemMessage, HumanMessage).

        Returns:
        - dict: Parsed JSON response from LLM.
        """
        try:
            # Conversion from LangChain message objects to OpenAI-compatible dicts
            openai_messages = [
                {
                    "role": "user" if msg.type == "human" else msg.type,
                    "content": msg.content
                } for msg in messages
            ]

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=self.temperature
            )

            content = response.choices[0].message.content.strip()

            # Debugging step
            #print("\n Raw LLM response:\n", content)

            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw response:\n{content}")
            return None

        except Exception as e:
            print(f"Error during LLM API call: {e}")
            return None
