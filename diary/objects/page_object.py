import streamlit as st 
import datetime
import json
from diary.objects.chatbot import ChatBot 
import time
from diary.database import DBManager
class Page:
    
    def __init__(self, title:str|None=None):
        self.title = title
        self.db_manager = DBManager()
        self.db_manager.create_table(self.db_manager.CREATE_TABLE_PAGES)
        if self.db_manager.get_page_name(page_name=self.title).values.__len__()<1:
            values={
                        "time": str(datetime.datetime.now()),
                        "page_id":hash(self.title),
                        "messages": json.dumps({})
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
        url = "http://127.0.0.1:8500/predict"
        chatbot = ChatBot(page_name=self.title, url=url)
        chatbot.main()
        
