import streamlit as st 
import datetime
from chatbot import ChatBot 
import time
from database import DBManager
class Page:
    
    def __init__(self, title:str|None=None):
        self.title = title
        st.set_page_config(
            page_title=f"Topic: {self.title}",
            initial_sidebar_state="expanded",
            layout="centered",
            menu_items={"About":"""This is where you can see all 
                        your thoughts"""}
            
        ),
        self.db_manager = DBManager()
        self.db_manager.create_table(self.db_manager.CREATE_TABLE_PAGES)
        values={
                    "time": str(datetime.now()),
                    "page_id":hash(self.page_name),
                    "messages": str(st.session_state.messages)
                }
        self.db_manager.insert_into_pages(page_name=self.title,
                                            values=values)
        
    def headings(self):
        # Get the current date, day, and time
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
        day = now.strftime("%A")

        # Create a container to hold the elements
        container = st.container()

        # Display the date, day, and time in separate columns within the container
        with container:
            col1, col2, col3 = st.columns([0.25,0.5,0.25])
            with col1:
                st.write(date)
            with col2:
                st.header(self.title)
            with col3:
                st.write(day)
                
    def main(self):
        self.headings()
        chatbot = ChatBot(page_name=self.title)
        chatbot.main()
        
Page("My Thoughts").main()