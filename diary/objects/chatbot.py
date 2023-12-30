import streamlit as st
import random
import json
import ast
from datetime import datetime
import time
from diary.database import DBManager
from diary.objects.utils import get_response


class ChatBot:
    def __init__(self, page_name:str, url:str|None=None):
        self.url = url 
        self.page_name = page_name
        self.db_manager = DBManager()

        
        
    def main(self):
        # Initialize chat history
        try:
            messages = self.db_manager.get_messages(page_name=self.page_name)
            if messages:
                print("Messages are: ", messages)
                messages = messages["output"]
                if messages:
                    original_messages = messages
                else:
                    original_messages = []
            else:
                original_messages = []
        except Exception as e:
            print("Can't fetch messages because ", e)
        new_messages = []                        

        # Display chat messages from history on app rerun
        for message in original_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("I am listening"):
            # Add user message to chat history
            new_messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            print(original_messages)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                resp = get_response(url=self.url, body=original_messages+new_messages)
                assistant_response = resp if resp else "I am down, but there :)"
                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            # Add assistant response to chat history
            new_messages.append({"role": "assistant", "content": full_response.replace("'", "")})
            try:
                if new_messages:
                    appending_messages = original_messages + new_messages
                    self.db_manager.update_table(table="pages",
                                                col_name="messages",
                                                value= json.dumps(appending_messages),
                                                page_name=self.page_name)
            except Exception as e:
                print(e)
                
                