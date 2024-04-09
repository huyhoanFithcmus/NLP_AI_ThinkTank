from objects.PageObject import Page
from database.Manager import DBManager
from PIL import Image
from pathlib import Path
import os
import streamlit as st

#Comment this if you add an environment variable
DB_PATH = "sqlite:///database.db"
os.environ["DATABASE_URI"] = DB_PATH

class App:
    def __init__(self):
        self.db_manager = DBManager()
    
    def _heading_tag(self, h_level, string, style=""):
        return f"<h{h_level} style={style}>{string}</h{h_level}>"
    
    def _write_markdown(self, string):
        return st.markdown(string, unsafe_allow_html=True)
    
    def _text_tag(self,string, tag="p", style=""):
        return f"<{tag} style={style}>{string}</{tag}>"
    
    def _url_button_tag(self, url, name="View App",style=""):
        return f"<a class='btn' href='{url}'>{name}</a>"
    
    def local_css(self, file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    def _img_tag(self, url:str, height:int, width:int):
        return f"<img class='tile_image' src='{url}'  width='{width}' height='{height}'> "
    
    def add_new_page(self):
        if self.new_page_name:
            Page(title=self.new_page_name)
            
    def main(self):
        title_tag = self._heading_tag("1 class='title' ", "🤖 AI ThinkTank 🤖", "text-align:center")
        self._write_markdown(title_tag)

        st.image("https://www.notion.so/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F0c6b2a24-183c-4a8c-889c-6d8d4d66a1d6%2F253fc070-879f-4742-92e4-f4d38784e619%2FUntitled.png?table=block&id=62902ffb-885f-49dc-8cb5-f885ada0fada&spaceId=0c6b2a24-183c-4a8c-889c-6d8d4d66a1d6&width=2000&userId=d6573d3c-3d81-4d95-81bc-512898e8b7a4&cache=v2", caption='AI ThinkTank', use_column_width=True)
        string = ("""The explosion of Large Language Models (LLMs) has opened up breakthrough applications, contributing to enhancing work efficiency in various fields, including debate. Thanks to their ability to generate high-quality text, LLMs provide strong support for building tight arguments, analyzing strengths and weaknesses in opponents' arguments, thereby helping users practice debating skills and enhance their ability to perceive multidimensional views on a topic. Recognizing the immense potential of LLMs in the field of debate, the AI ThinkTank application emerges, promising to be a valuable assistant to users in idea development and fostering critical thinking.""")
        
        string_tag =self._text_tag(string=string, style="text-align:justify")
        self._write_markdown(string_tag)
        bar_line = "---"
        self._write_markdown(bar_line)
        #Get all available pages 
        pages = self.db_manager.get_all_page_names()
        if pages is not None:
            pages = pages["page_name"].values
            self.pages = list(pages)
        else:
            self.pages = []
        self.pages.insert(0, None)

        selected_page = st.sidebar.selectbox("Choose a Page", self.pages)
        if selected_page:
            Page(title=selected_page).main()
        else:
            new_tag = self._heading_tag("3 class='title' ", "New page to start your journey ", "text-align:center")
            self._write_markdown(new_tag)
            col1, col2, col3 = st.columns([0.2,0.6,0.2])
            with col2:
                page_name_input = st.text_input(label="Add a name here",value="")
                if page_name_input:
                    self.new_page_name = page_name_input.strip().replace(" ", "")
            
                st.button("New Page", on_click=self.add_new_page, use_container_width=True)

app = App()

app.main()