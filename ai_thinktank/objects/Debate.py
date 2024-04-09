import json
import re

from typing import List, Dict, Optional, Any
from objects.Coordinator import Coordinator
from objects.Expert import Expert
from pathlib import Path
from bs4 import BeautifulSoup

from langchain.schema.messages import HumanMessage
from langchain.schema import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema import ChatMessage

# Version read document:
from langchain.chains import StuffDocumentsChain
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

# Version read transcript youtube:
from youtube_transcript_api import YouTubeTranscriptApi

from models.gemini import GoogleModel

class Debate():
    def __init__(self, model_name: str = "gemini-1.0-pro") -> None:
        self.model_name = model_name
        self.topic = None
        self.debate_history = []
        self.memory = []
        self.experts = []
        self.image_url = None     
        self.document_url = None    
        self.youtube_url = None

    def add_message(self, role: str, content: str, avatar: Optional[str] = None) -> None:
        self.debate_history.append({"role": role, "avatar": avatar, "content": content})
        role = "user" if role == "user" else "assistant"
        self.memory.append(ChatMessage(role=role, content=content))

    def get_experts(self) -> List[Expert]:
        return self.experts

    def initialize_new_debate(self, topic: str, num_experts: int, stance: str) -> None:
        self.topic = topic
        expert_instructions = self.create_expert_instructions(num_experts, stance)
        self.experts = self.generate_experts(expert_instructions)

    def initialize_existing_debate(self, topic: str, debate_history: List[Dict[str, str]], expert_instructions: List[Dict[str, str]]) -> None:
        self.topic = topic
        self.debate_history = debate_history

        for message in debate_history:
            role = "user" if message["role"] == "user" else "assistant"
            self.memory.append(ChatMessage(role=role, content=message["content"]))
        self.experts = self.generate_experts(expert_instructions)


    def is_image_url(self, input_string: str) -> bool:
        # Regular expression to match URLs ending with image file extensions
        url_pattern = r'https?://\S+\.(jpg|jpeg|png|gif|bmp|svg|JPG)$'
        if re.match(url_pattern, input_string):
            return True
        return False

    def is_youtube_url(self, input_string: str) -> bool:
        # Regular expression to match YouTube URLs
        url_pattern = r'https?://(www\.)?youtube\.com/watch\?v=\S+'
        if re.match(url_pattern, input_string):
            return True
        return False
    
    def is_web_page_doc(self, input_string: str) -> bool:
        # Regular expression to match URLs and not youtube URLs, image URLs: 
        if self.is_youtube_url(input_string) or self.is_image_url(input_string):
            return False

        # Regular expression to match URLs
        url_pattern = r'https?://\S+'
        if re.match(url_pattern, input_string):
            return True
        
        return False

    def create_expert_instructions(self, num_experts: int, stance: str) -> List[Dict[str, str]]:
        # Determine if the topic is a URL or a text topic
        if self.is_image_url(self.topic):
            self.image_url = self.topic
            self.topic = self.generate_topic_from_image(self.topic)
        elif self.is_youtube_url(self.topic):
            self.youtube_url = self.topic
            self.topic = self.generate_topic_from_youtube(self.topic)
        elif self.is_web_page_doc(self.topic):
            self.document_url = self.topic
            self.topic = self.generate_topic_from_page(self.topic)

        model_coordinator = GoogleModel(model_name="gemini-1.0-pro", stream=True, convert_system_message_to_human=True)
        coordinator_model = model_coordinator.make_pipeline()
        coordinator = Coordinator(model=coordinator_model, num_experts=num_experts, topic=self.topic, stance=stance)

        return coordinator.generate_expert_instructions()

    def generate_experts(self, experts_instructions: List[Dict[str, str]]) -> List[Expert]:
        experts = []
        for expert_instruction in experts_instructions:
            model_expert = GoogleModel(model_name="gemini-1.0-pro", stream=True, convert_system_message_to_human=True)
            expert_model = model_expert.make_pipeline()
            experts.append(Expert(expert_model, expert_instruction))
        return experts
    
    def get_debate_params(self) -> Dict[str, Any]:
        return {"topic": self.topic, "debate_history": self.debate_history, "expert_instructions": [expert.expert_instruction for expert in self.experts]}
    

    def generate_topic_from_image(self, image_url: str) -> str:
        model_vision = GoogleModel(model_name="gemini-pro-vision", stream=True, convert_system_message_to_human=True)
        vision_model = model_vision.make_pipeline()

        multimodal_prompt = HumanMessage(
            content=[
                {"type": "text", "text": "Generate a debate topic based on the image, ensuring the topic presents a clear issue with distinct pro and con sides. The topic should be a concise statement that encourages discussion from opposing viewpoints. Just one single short sentence."},
                {"type": "image_url", "image_url": image_url}
            ]
        )

        image_prompt_template = ChatPromptTemplate.from_messages([multimodal_prompt])

        chain = (
            image_prompt_template
            | vision_model
            | StrOutputParser()
        )

        generated_topic = chain.invoke({})
        return generated_topic
    
    def generate_topic_from_page(self, page_url: str) -> str:
        model_web = GoogleModel(model_name="gemini-1.0-pro", stream=True, convert_system_message_to_human=True)
        web_model = model_web.make_pipeline()
        docs = WebBaseLoader(page_url).load()

        prompt_template = """
        Generate a debate topic based on the following content, ensuring the topic presents a clear issue with distinct pro and con sides. The topic should be a concise statement that encourages discussion from opposing viewpoints. Just one single short sentence:
        {docs}
        CONCISE TOPIC DEBATE:
        """

        prompt_website = PromptTemplate.from_template(prompt_template)
        llm_chain = LLMChain(llm=web_model, prompt=prompt_website)
        stuff_docs_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="docs")

        generated_topic = stuff_docs_chain.run(docs)

        return generated_topic

    def generate_topic_from_youtube(self, youtube_url: str) -> str:
        model_youtube = GoogleModel(model_name="gemini-1.0-pro", stream=True, convert_system_message_to_human=True)
        youtube_model = model_youtube.make_pipeline()
        video_id = youtube_url.split('=')[1]

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as e:
            print(e)

        result = ""
        for i in transcript:
            result += ' ' + i['text']

        prompt_template = """
        Generate a debate topic based on the provided YouTube transcript. Craft a topic that clearly delineates both sides of the argument, encouraging discussion from contrasting viewpoints. The topic should be succinct, presenting a clear issue in a single sentence:
        {transcript}  
        CONCISE TOPIC DEBATE:
        """

        prompt_youtube = PromptTemplate.from_template(prompt_template)
        llm_chain = LLMChain(llm=youtube_model, prompt=prompt_youtube)
        generated_topic = llm_chain.run(transcript)

        return generated_topic