import json

from pathlib import Path
from langchain.schema.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

SECRET_PATH = Path(__file__).parent / "secrest.json" 

class GoogleModel:
    """
    GoogleModel is a class that creates a pipeline for the Google Generative AI model.

    Args:
        model_name (str): The name of the model to use.
        stream (bool): Whether to stream the output or not. Defaults to True.
        convert_system_message_to_human (bool): Whether to convert system messages to human messages. Defaults to True.

    Returns:
        ChatGoogleGenerativeAI: A pipeline for the Google Generative AI model.
    """
    def __init__(self, model_name: str, stream: bool = True, convert_system_message_to_human: bool = True):
        self.model_name = model_name
        self.stream = stream
        self.convert_system_message_to_human = convert_system_message_to_human
        with open(SECRET_PATH, "r") as f:
            self.env_vars = json.load(f)

    def make_pipeline(self):
        GOOGLE_API_KEY = self.env_vars["GOOGLE_API_KEY"].strip()
        return ChatGoogleGenerativeAI(google_api_key=GOOGLE_API_KEY, model=self.model_name, stream=self.stream, convert_system_message_to_human=self.convert_system_message_to_human)
