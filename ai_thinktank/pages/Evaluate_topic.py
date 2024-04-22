import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
from models.gemini import GoogleModel
from langchain.schema.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

# Version read document:
from langchain.chains import StuffDocumentsChain
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

# Version read transcript youtube:
from youtube_transcript_api import YouTubeTranscriptApi


load_dotenv()
st.set_page_config(
    page_title="Evaluate Topic",
    page_icon=":robot_face:",  # Set your desired favicon
    layout="wide",  # Choose layout style ('wide' or 'centered')
)

# Initialize Gemini-Pro 
genai.configure(api_key="AIzaSyBrh5bOh7RaTWA805GbIj9nnz9j9R18Lgs")  # Make sure to set your API key in the environment variable
model = genai.GenerativeModel('gemini-pro')

# Gemini uses 'model' for assistant; Streamlit uses 'assistant'
def role_to_streamlit(role):
  if role == "model":
    return "assistant"
  else:
    return role

# Add a Gemini Chat history object to Streamlit session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history = [])

# Display Form Title
st.title("Evaluate Topic Relevance")

# Display chat messages from history above current input box
for message in st.session_state.chat.history:
    with st.chat_message(role_to_streamlit(message.role)):
        st.markdown(message.parts[0].text)


def is_image_url(input_string: str) -> bool:
        # Regular expression to match URLs ending with image file extensions
        url_pattern = r'https?://\S+\.(jpg|jpeg|png|gif|bmp|svg|JPG)$'
        if re.match(url_pattern, input_string):
            return True
        return False

def is_youtube_url(input_string: str) -> bool:
        # Regular expression to match YouTube URLs
        url_pattern = r'https?://(www\.)?youtube\.com/watch\?v=\S+'
        if re.match(url_pattern, input_string):
            return True
        return False

def generate_topic_from_image(image_url: str) -> str:
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

def generate_topic_from_youtube(youtube_url: str) -> str:
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

if prompt := st.chat_input("Enter your argument here:"):
    # Display user's last message
    st.chat_message("user").markdown(prompt)
    topic = ""

    # Check if the user input is an image URL
    if is_image_url(prompt):
        # Generate a topic from the image
        topic = generate_topic_from_image(prompt)
    elif is_youtube_url(prompt):
        topic = generate_topic_from_youtube(prompt)
    else:
        topic = prompt

    # Send user entry to Gemini and read the response

    st.session_state.chat.send_message(topic)
    
    
    template_debate = f"Debate with topic: {topic}."
    response_debate = genai.GenerativeModel('gemini-pro').generate_content(template_debate)
    
    # Send user entry to Gemini and read the response
    template_rating = f"Rate this argument: {topic} on a 10-point scale for each person and do not provide any feedback."
    response_rating = genai.GenerativeModel('gemini-pro').generate_content(template_rating)
    
    # Display last 
    with st.chat_message("assistant"):
        st.markdown(response_debate.text)
        st.markdown(response_rating.text + " in terms of relevance to the topic.")
