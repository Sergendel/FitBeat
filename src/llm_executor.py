import json
import os

from dotenv import load_dotenv
from langchain.chains import ConversationChain

# for memory
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from openai import OpenAI


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
                    "content": msg.content,
                }
                for msg in messages
            ]

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=self.temperature,
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


# not in use meanwhile
class LLMExecutor_with_memory:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.2):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY not set in .env file")

        self.llm = ChatOpenAI(
            api_key=api_key, model_name=model_name, temperature=temperature
        )
        self.memory = ConversationBufferMemory()

        # Integrate memory with ConversationChain
        self.chain = ConversationChain(llm=self.llm, memory=self.memory)

    def execute(self, messages):
        """
        Execute messages with explicit memory context.
        """
        # Convert LangChain message format to a single prompt explicitly
        prompt_text = "\n".join([msg.content for msg in messages])
        response = self.chain.run(prompt_text)

        # Attempt JSON parsing explicitly
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return response  # return raw text if JSON fails
