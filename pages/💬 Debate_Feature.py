import streamlit as st
from pathlib import Path
import json
from PIL import Image
import requests
from io import BytesIO

from utils.StreamHandler import StreamHandler
from utils.Debate import Debate
from functools import wraps

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain
from utils.Debate import Debate


# Các thành phần không thay đổi về sau
def show_spinner(func):
    """
    A decorator to show a spinner in the Streamlit app while the decorated function is running.
    This can be used to indicate to the user that a process is ongoing in the background.

    Parameters:
    - func (Callable): The function to wrap with the spinner functionality.
    Returns:
    - Callable: The wrapped function with spinner functionality.
    """
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        with st.spinner('Generating Experts...'):
            return func(*args, **kwargs)
    return wrapper_function

def is_first_load():
    return False
    if "first_load_done" not in st.session_state:
        st.session_state["first_load_done"] = True
        return True
    return False

def get_api_key():
    """
    Retrieves the Google API key from the Streamlit session state or prompts the user to input it if not found.

    This function first checks if the 'GOOGLE_API_KEY' is present in the Streamlit session state. If not, it then checks
    if the key is available in the Streamlit secrets. If the key is still not found, it prompts the user to input the
    API key via a sidebar text input, which is then stored in the session state for future use.

    The function ensures that the application has access to the Google API key required for its operations.
    """
    if "GOOGLE_API_KEY" not in st.session_state:
        if "GOOGLE_API_KEY" in st.secrets:
            st.session_state["GOOGLE_API_KEY"] = st.secrets['GOOGLE_API_KEY']
        else:
            st.session_state["GOOGLE_API_KEY"] = st.sidebar.text_input("Google API Key", type="password")


    if not st.session_state["GOOGLE_API_KEY"]:
        st.info("Enter a Google API Key to continue")
        st.stop()

@show_spinner
def initialize_debate(start_new=True, debate_history=None, expert_instructions=None):
    get_api_key()
    st.session_state["debate"] = Debate(api_key=st.session_state["GOOGLE_API_KEY"], model_name="gemini-1.0-pro")
    st.session_state["initialized"] = True
    st.session_state["experts"] = []

    if start_new:
        st.session_state.debate.initialize_new_debate(topic=topic, num_experts=number_experts, stance=stance)
    else:
        st.session_state.debate.initialize_existing_debate(topic=topic, debate_history=debate_history, expert_instructions=expert_instructions)

    st.session_state["debate_topic"] = st.session_state.debate.topic
    st.session_state["debate_image_url"] = st.session_state.debate.image_url
    st.session_state["initialized"] = True

    st.session_state["experts"] = st.session_state.debate.get_experts()


def load_debate_configuration():
    config_path = Path(__file__).resolve().parent.parent / 'configs' / 'suggestions.json'
    with config_path.open('r', encoding='utf-8') as f:
        config = json.load(f)
    st.session_state["suggestions"] = config["suggestions"]

def display_suggestions():
    suggestions = st.container()
    columns = suggestions.columns(4)
    for i, suggestion in enumerate(st.session_state["suggestions"][:4]):
        button_key = f"suggestion_btn_{i}" 
        columns[i].button(suggestion["topic"], key=button_key, on_click=lambda suggestion=suggestion: initialize_debate(start_new=False, debate_history=suggestion["debate_history"], expert_instructions=suggestion["expert_instructions"]))


def conduct_debate_round():
    default_avatar = "👤"
    for expert in st.session_state["experts"]:
        try:
            with chat.chat_message(name=expert.expert_instruction["role"], avatar=expert.expert_instruction["avatar"]):
                stream_handler = StreamHandler(st.empty())
                expert.generate_argument(st.session_state.debate, stream_handler)
                final_response = stream_handler.get_accumulated_response()
                st.session_state.debate.add_message(role=expert.expert_instruction["role"], avatar=expert.expert_instruction["avatar"], content=final_response)
        except Exception:
            with chat.chat_message(name=expert.expert_instruction["role"], avatar=default_avatar):
                response = expert.generate_argument(st.session_state.debate, StreamHandler(st.empty()))
                st.session_state.debate.add_message(role=expert.expert_instruction["role"], avatar=default_avatar, content=response)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Function to split text into chunks
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000, chunk_overlap=1000)
    chunks = splitter.split_text(text)
    return chunks  # list of strings

# Function to get embeddings for each chunk
def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001")  # type: ignore
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def summarize_pdf(doc, custom_prompt="Summarize this text in a way that becomes a question used as a topic of debate"):
    genai.configure(api_key=get_api_key())
    model = genai.GenerativeModel(model_name="gemini-1.0-pro")
    
    summary = model.start_chat(history=[])
    summary.send_message(doc + "\n" + "\n" + custom_prompt)
    return summary.last.text

def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "upload some pdfs and ask me a question"}]

    
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

st.markdown("# AI ThinkTank")

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

if "start_debate" not in st.session_state:
    st.session_state["start_debate"] = False

if 'debate_image_url' in st.session_state and st.session_state['debate_image_url']:
    try:
        response = requests.get(st.session_state['debate_image_url'])
        image = Image.open(BytesIO(response.content))
        st.image(image, caption="Debate Image", use_column_width=True)
    except Exception as e:
        st.error(f"Failed to load image from URL. Error: {e}")

if 'debate_topic' in st.session_state and st.session_state['debate_topic']:
    st.header(st.session_state['debate_topic'])


# Khai báo một biến trạng thái để lưu trữ tóm tắt từ PDF
if "summary_gen" not in st.session_state:
    st.session_state["summary_gen"] = ""


# Sidebar for uploading PDF files
with st.sidebar:
    st.title("Menu:")
    pdf_docs = st.file_uploader(
        "Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
    if st.button("Submit & Process"):
        with st.spinner("Processing..."):
            raw_text = get_pdf_text(pdf_docs)
            text_chunks = get_text_chunks(raw_text)
            get_vector_store(text_chunks)
            summary = summarize_pdf(raw_text)
            st.session_state["summary_gen"] = summary


# Settings and form
form = st.form(key="form_settings")
topicCol, buttonCol = form.columns([4,1])

if st.session_state["summary_gen"] != "":
    topic = topicCol.text_area(
        "The topic that gemini generated",
        key="topic",
        value=st.session_state["summary_gen"],
        height=str(st.session_state["summary_gen"]).count("\n") * 25 # Sử dụng giá trị tóm tắt từ biến trạng thái
    )

expander = form.expander("Customize debate")
number_experts = expander.slider(
    'Number of experts:',
    min_value=2,      
    max_value=6, 
    value=3,
    step=1
)

options = ["Strongly For", "For", "Neutral", "Against", "Strongly Against"]
# stance = expander.select_slider("Stance of the experts", options=options, value="Neutral")
stance = "Neutral"

# Submit button
submitted = form.form_submit_button(label="Submit")

if submitted and topic != "":
    st.session_state["submitted"] = True
    initialize_debate()
    st.session_state["start_debate"] = False

# Conditionally display suggestions based on the 'submitted' state
if not st.session_state["submitted"]:
    load_debate_configuration()
    #display_suggestions()

# Load and display suggestions
load_debate_configuration()

if is_first_load():
    default_suggestion = st.session_state["suggestions"][1]
    initialize_debate(start_new=False, debate_history=default_suggestion["debate_history"], expert_instructions=default_suggestion["expert_instructions"])


## Chat interface
chat = st.container()

if "debate" in st.session_state:
    for msg in st.session_state.debate.debate_history:
        chat.chat_message(name=msg["role"], avatar=msg["avatar"]).write(msg["content"])

if submitted and topic.strip():
    st.session_state["submitted"] = True
    initialize_debate()
    st.session_state["start_debate"] = False


if "initialized" in st.session_state and st.session_state["initialized"]:
    expert_expander = form.expander("Generated Experts")
    for expert in st.session_state.experts:
        expert_expander.write(f"{expert.expert_instruction['avatar']} {expert.expert_instruction['role']}, {expert.expert_instruction['stance']}")

    if not st.session_state["start_debate"]:
        if st.button("Start Debate"):
            st.session_state["start_debate"] = True
            st.session_state["debate"].initialize_new_debate(topic=topic, num_experts=number_experts, stance=stance)
            st.session_state["experts"] = st.session_state["debate"].get_experts()
            conduct_debate_round()

    if st.session_state["start_debate"]:
        if input := st.chat_input(placeholder="Participate in the debate"):
            user_prompt = input.replace("Human: ", "")
            st.session_state.debate.add_message(role="user", content=user_prompt)
            chat.chat_message("user").write(user_prompt)

            conduct_debate_round()

        st.button("Continue debate", on_click=conduct_debate_round)
