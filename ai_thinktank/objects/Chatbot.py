import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import re

from datetime import datetime
from streamlit_player import st_player
from functools import wraps
from PIL import Image
from io import BytesIO

from database.Manager import DBManager
from objects.Debate import Debate
from objects.StreamHandler import StreamHandler
from models.gemini import GoogleModel

# Version read pdf:
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
import google.generativeai as genai

genai.configure(api_key="AIzaSyBrh5bOh7RaTWA805GbIj9nnz9j9R18Lgs")  # Make sure to set your API key in the environment variable
model = genai.GenerativeModel('gemini-pro')

@st.cache_resource
class ChatBot:
    def __init__(self, page_name:str, url:str|None=None):
        self.url = url 
        self.page_name = page_name
        self.db_manager = DBManager()
        self.submitted = False
        self.start_debate = False
        self.url_image = None
        self.url_document = None
        self.debate = None
        self.initialized = None
        self.experts = []
        self.topic = None
        self.get_pdf = False
        self.url_youtube = None
    
    def show_spinner(func):
        @wraps(func)
        def wrapper_function(*args, **kwargs):
            with st.spinner('Generating Experts...'):
                return func(*args, **kwargs)
        return wrapper_function

    @show_spinner
    def initialize_debate(self, start_new=True, debate_history=None, expert_instructions=None):
        self.debate = Debate(model_name="gemini-1.0-pro")
        self.initialized = True

        if start_new:
            self.debate.initialize_new_debate(topic=topic, num_experts=number_experts, stance=stance)
        else:
            self.debate.initialize_existing_debate(topic=topic, debate_history=debate_history, expert_instructions=expert_instructions)

        self.topic = self.debate.topic 
        self.experts = self.debate.get_experts()
        self.url_image = self.debate.image_url
        self.url_document = self.debate.document_url
        self.url_youtube = self.debate.youtube_url
        self.initialized = True
    
    def conduct_debate_round(self):
        default_avatar = "👤"
        for expert in self.experts:
            try:
                with chat.chat_message(name=expert.expert_instruction["role"], avatar=expert.expert_instruction["avatar"]):
                    stream_handler = StreamHandler(st.empty())
                    expert.generate_argument(self.debate, stream_handler)
                    final_response = stream_handler.get_accumulated_response()

                    # from final_response, extract new words with meaning for learn English

                    english_words_prompt = f"""
                    Extract new words with meaning from the following response:
                    {final_response}
                    """
                    model = genai.GenerativeModel('gemini-pro')
                    english_words_response = model.generate_content(english_words_prompt)
                    extracted_words = english_words_response.text

                    self.debate.add_message(role=expert.expert_instruction["role"], avatar=expert.expert_instruction["avatar"], content=final_response + "\n\n" + "New words" + "\n" + extracted_words)
                    self.db_manager.update_table(table="pages", col_name="messages", value=json.dumps(self.debate.debate_history, ensure_ascii=False), page_name=self.page_name)
            except Exception:
                with chat.chat_message(name=expert.expert_instruction["role"], avatar=default_avatar):
                    response = expert.generate_argument(self.debate, StreamHandler(st.empty()))
                    self.debate.add_message(role=expert.expert_instruction["role"], avatar=default_avatar, content=response)
                    self.db_manager.update_table(table="pages", col_name="messages", value=json.dumps(self.debate.debate_history), ensure_ascii=False, page_name=self.page_name)

    def has_existing_debate(self):
        """
        Checks if there's existing debate data for the current page in the database.

        Returns:'s
            bool: True if data exists, False otherwise.
        """
        message_data = self.db_manager.get_debates(self.page_name)
        return bool(message_data and message_data.get('output'))

    def get_topic_from_pdf_text(self, pdf_docs):
        raw_text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                raw_text += page.extract_text()
        return raw_text
    
    def generate_topic_from_pdf(self, pdf_docs, model_name="gemini-1.0-pro"):
        model_summarize = GoogleModel(model_name=model_name, stream=True, convert_system_message_to_human=True)
        summarize_model = model_summarize.make_pipeline()

        prompt_template = """
        Generate a debate topic based on the following content, ensuring the topic presents a clear issue with distinct pro and con sides. The topic should be a concise statement that encourages discussion from opposing viewpoints. Just one single short sentence:
        {pdf_docs}
        CONCISE TOPIC DEBATE:
        """

        prompt_pdf = PromptTemplate.from_template(prompt_template)
        llm_chain = LLMChain(llm=summarize_model, prompt=prompt_pdf)
        generated_topic = llm_chain.run(pdf_docs)

        return generated_topic

    def main(self):
        
        st.markdown(
            """
            <style>
            .stButton > button {
                width: 100%;
                height: auto;
            }
            
            /* Apply margin-top only for non-mobile views */
            @media (min-width: 768px) {
                [data-testid="stFormSubmitButton"] > button {
                    margin-top: 28px;
                }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        if self.url_image is not None and self.url_image != "":
            try: 
                response = requests.get(self.url_image)
                image = Image.open(BytesIO(response.content))
                st.image(image, caption="Debate Image", use_column_width=True)
            except Exception as e:
                st.error(f"Failed to load image from URL. Error: {e}")
        elif self.url_document is not None and self.url_document != "":
            try:
                iframe_src = self.url_document
                components.iframe(iframe_src)
            except Exception as e:
                st.error(f"Failed to load document from URL. Error: {e}")
        elif self.url_youtube is not None and self.url_youtube != "":
            try:
                st_player(self.url_youtube)
            except Exception as e:
                st.error(f"Failed to load video from URL. Error: {e}")
        
        global topic 
        if self.topic is not None:
            st.header(self.topic)

        # Check database for existing debate data:
        if self.has_existing_debate() and self.submitted is False:
            # Extract debate data from the database:
            debate_data_record = self.db_manager.get_debates(self.page_name)
            debate_data = json.loads(debate_data_record["output"])

            # Extract expert instructions from the database:
            expert_instructions_record = self.db_manager.get_expert_instructions(self.page_name)
            expert_instructions = json.loads(expert_instructions_record["output"])

            # Extract topic from the database:
            topic_record = self.db_manager.get_topic_page_value(self.page_name)
            topic = topic_record["page_topic"].values[0]

            # Initialize the debate with the existing data:
            self.initialize_debate(start_new=False, debate_history=debate_data, expert_instructions=expert_instructions)

            # Set flag to start the debate:
            self.start_debate = True

        with st.sidebar:
            st.markdown("---")
            st.title("Upload PDF:")
            pdf_docs = st.file_uploader(
                "Upload your PDF File and Click on the Submit & Process Button", accept_multiple_files=True)
            
            if st.button("Submit & Process"):
                with st.spinner("Processing..."):
                    self.get_pdf = True
                    raw_text = self.get_topic_from_pdf_text(pdf_docs)
                    self.topic = self.generate_topic_from_pdf(raw_text)
        
        form = st.form(key="form_settings")
        topicCol, buttonCol = form.columns([4,1])
        
        if self.get_pdf is False:
            topic = topicCol.text_input(
                "Enter your topic of debate",
                placeholder="Accepts image, youtube or document URL",
                key="topic"
            )
        else:
            topic = topicCol.text_area(
                "The topic that was generated from the PDF",
                value=self.topic,
                key="topic"
            )
        
        expander = form.expander("Customize debate")
        global number_experts 
        number_experts = expander.slider(
            'Number of experts:',
            min_value=2,      
            max_value=6, 
            value=3,
            step=1
        )

        options = ["Strongly For", "For", "Neutral", "Against", "Strongly Against"]
        global stance
        stance = "Neutral"
        stance = expander.select_slider("Stance of the experts", options=options, value="Neutral")

        # Update stance, topic, experts in the database:
        submitted = buttonCol.form_submit_button(label="Submit")
        if submitted and topic.strip(): 
            self.submitted = True
            self.initialize_debate()
            # Update topic, experts in the database:
            self.db_manager.update_table(table="pages", col_name="page_topic", value=self.topic, page_name=self.page_name)
            self.db_manager.update_table(table="pages", col_name="expert_instructions", value=json.dumps([expert.expert_instruction for expert in self.experts], ensure_ascii=False).replace("'", "''"), page_name=self.page_name)
            self.start_debate = False
            
        global chat
        chat = st.container()

        if self.debate is not None:
            for msg in self.debate.debate_history:
                chat.chat_message(name=msg["role"], avatar=msg["avatar"]).write(msg["content"])

        if submitted and topic.strip():
            self.submitted = True
            self.initialize_debate()

            # Update topic, experts in the database:
            self.db_manager.update_table(table="pages", col_name="page_topic", value=self.topic, page_name=self.page_name)
            self.db_manager.update_table(table="pages", col_name="expert_instructions", value=json.dumps([expert.expert_instruction for expert in self.experts], ensure_ascii=False).replace("'", "''"), page_name=self.page_name)

            self.start_debate = False

        if self.initialized is True and self.initialized is not None:
            expert_expander = form.expander("Generated Experts")
            for expert in self.experts:
                expert_expander.write(f"{expert.expert_instruction['avatar']} {expert.expert_instruction['role']}, {expert.expert_instruction['stance']}")

            if not self.start_debate:
                if st.button("Start Debate"):
                    self.start_debate = True
                    self.experts = self.debate.get_experts()
                    self.conduct_debate_round()

            if self.start_debate:
                if input := st.chat_input(placeholder="Participate in the debate"):
                    user_prompt = input.replace("Human: ", "")
                    self.debate.add_message(role="user", content=user_prompt)
                    chat.chat_message("user").write(user_prompt)
                    self.conduct_debate_round()

                st.button("Continue debate", on_click=self.conduct_debate_round)
            