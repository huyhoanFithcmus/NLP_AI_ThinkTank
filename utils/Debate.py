from langchain.schema import ChatMessage
from typing import List, Dict, Optional, Any
from utils.Coordinator import Coordinator
from utils.Expert import Expert
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.schema.messages import HumanMessage
from langchain.schema import StrOutputParser
from langchain.prompts import ChatPromptTemplate
import re

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



class Debate():
    def __init__(self, api_key: str, model_name: str = "gemini-1.0-pro") -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.topic = None
        self.debate_history = []
        self.memory = []
        self.experts = []
        self.image_url = None

        if not firebase_admin._apps:
            # Khởi tạo ứng dụng Firebase
            service_account_key = {
                "type": env("TYPE"),
                "project_id": env("PROJECT_ID"),
                "private_key_id": env("PRIVATE_KEY_ID"),
                "private_key": env("PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": env("CLIENT_EMAIL"),
                "client_id": env("CLIENT_ID"),
                "auth_uri": env("AUTH_URI"),
                "token_uri": env("TOKEN_URI"),
                "auth_provider_x509_cert_url": env("AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": env("CLIENT_X509_CERT_URL"),
            }

            cred = credentials.Certificate(service_account_key)
            firebase_admin.initialize_app(cred)
            


    def add_message(self, role: str, content: str, avatar: Optional[str] = None) -> None:
        self.debate_history.append({"role": role, "avatar": avatar, "content": content})

        db = firestore.client() # connecting to firestore
        collection = db.collection('programmer_details')  # create collection
        collection.document('A01').set(self.debate_history)

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
        url_pattern = r'https?://\S+\.(jpg|jpeg|png|gif|bmp|svg)$'
        
        if re.match(url_pattern, input_string):
            return True
        return False


    def create_expert_instructions(self, num_experts: int, stance: str) -> List[Dict[str, str]]:
        # Determine if the topic is a URL or a text topic
        if self.is_image_url(self.topic):
            self.image_url = self.topic
            self.topic = self.generate_topic_from_image(self.topic)

        coordinator_model = ChatGoogleGenerativeAI(model=self.model_name, stream=True, convert_system_message_to_human=True)
        coordinator = Coordinator(model=coordinator_model, num_experts=num_experts, topic=self.topic, stance=stance)

        return coordinator.generate_expert_instructions()


    def generate_experts(self, experts_instructions: List[Dict[str, str]]) -> List[Expert]:
        experts = []
        for expert_instruction in experts_instructions:
            expert_model = ChatGoogleGenerativeAI(model="gemini-1.0-pro", stream=True, convert_system_message_to_human=True)
            experts.append(Expert(expert_model, expert_instruction))
        return experts
    
    def get_debate_params(self) -> Dict[str, Any]:
        return {"topic": self.topic, "debate_history": self.debate_history, "expert_instructions": [expert.expert_instruction for expert in self.experts]}
    

    def generate_topic_from_image(self, image_url: str) -> str:
        vision_model = ChatGoogleGenerativeAI(model="gemini-1.0-pro-vision", stream=True, convert_system_message_to_human=True)

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