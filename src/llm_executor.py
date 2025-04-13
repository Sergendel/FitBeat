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
        try:
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

            # Automatically detect JSON or text
            try:
                result = json.loads(content)
                return result  # JSON parsed successfully
            except json.JSONDecodeError:
                # Not JSON, return raw text
                return content

        except Exception as e:
            print(f"Error during LLM API call: {e}")
            return None
