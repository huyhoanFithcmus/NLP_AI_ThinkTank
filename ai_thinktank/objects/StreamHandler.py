from langchain.callbacks.base import BaseCallbackHandler

class StreamHandler(BaseCallbackHandler):
    """
    StreamHandler is a class that handles the streaming of text.

    Args:
        container (st.container): The Streamlit container.
        initial_text (str): The initial text. Defaults to "".

    Returns:
        None
    """
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

    def get_accumulated_response(self):
        return self.text
