import streamlit as st 
import datetime
import json
import time

from objects.Chatbot import ChatBot
from database.Manager import DBManager
        
class Page:
    """
    Page is a class that creates a page object.  

    Args:
        title (str): The title of the page.
    
    Returns:
        None
    """
    def __init__(self, title:str|None=None):
        self.title = title
        self.db_manager = DBManager()
        self.db_manager.create_table(self.db_manager.CREATE_TABLE_PAGES)

        # Check if the page exists in the database:
        if self.db_manager.get_page_name(page_name=self.title).values.__len__()<1:
            values={
                        "time": str(datetime.datetime.now()),
                        "page_id":hash(self.title),
                        "messages": json.dumps({}),
                        "page_topic": "",
                        "page_image": "",
                        "expert_instructions": json.dumps({})
                    }
            self.db_manager.insert_into_pages(page_name=self.title,values=values)
            
    def remove_button(self):
        """
        Remove the page from the database.

        Args:
            None
        """
        # Display button on the sidebar
        if st.sidebar.button("Remove Page", use_container_width=True):
            self.db_manager.delete_page(self.title)

            # Remove this sidebar navigation item:
            st.rerun()

        
    def headings(self):
        """
        Display the date and day on the page.

        Args:
            None
        """
        # Get the current date, day, and time
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
        day = now.strftime("%A")

        # Create a container to hold the elements
        container = st.container()

        # Display the date, day, and time in separate columns within the container
        with container:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(date)
            with col2:
                st.write(day)
        
    def main(self):
        self.headings()
        self.remove_button()
        url = "http://127.0.0.1:8500/predict"
        chatbot = ChatBot(page_name=self.title, url=url)
        chatbot.main()