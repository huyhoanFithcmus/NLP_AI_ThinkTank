import streamlit as st
import random
from datetime import datetime
import time
from diary.database import DBManager


class ChatBot:
    def __init__(self, page_name:str, url:str|None=None):
        self.bot_url = url 
        self.page_name = page_name
        self.db_manager = DBManager()

        
        
    def main(self):
        # Initialize chat history
        try:
            messages = self.db_manager.get_messages(page_name=self.page_name)
            messages = messages["messages"].values[0]
            messages = eval(messages)
            original_messages = messages
        except:
            messages = []
                        

        # Display chat messages from history on app rerun
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("I am listening"):
            # Add user message to chat history
            messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                assistant_response = random.choice(
                    [
                        "Hello there! How can I assist you today?",
                        "Hi, human! Is there anything I can help you with?",
                        "Do you need help?",
                    ]
                )
                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            # Add assistant response to chat history
            messages.append({"role": "assistant", "content": full_response})
            try:
                if messages:
                    appending_messages = original_messages + messages
                    self.db_manager.update_table(table="pages",
                                                col_name="messages",
                                                value= str(appending_messages).replace("'",'"'),
                                                page_name=self.page_name)
            except Exception as e:
                print(e)
                
                