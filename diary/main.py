from objects.page_object import Page
from database.manager import DBManager
import os
import streamlit as st
 
os.environ["DATABASE_URI"] ="sqlite:///E:\dear-diary\database.db"

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
        return f"<img class='tile_image' src='{url}'  width='{width}' height='{height}'>"
    
    def add_new_page(self):
        if self.new_page_name:
            Page(title=self.new_page_name)
        
        
    def main(self):
        title_tag = self._heading_tag("1 class='title' ", "Dear Diary", "text-align:center")
        self._write_markdown(title_tag)
        
        #Get all available pages 
        pages = self.db_manager.get_all_page_names()
        pages = pages["page_name"].values
        self.pages = list(pages)
        self.pages.insert(0, None)
        selected_page = st.sidebar.selectbox("Choose a Page", self.pages)
        if selected_page:
            Page(title=selected_page).main()
        else:
            new_tag = self._heading_tag("3 class='title' ", "New Page", "text-align:center")
            self._write_markdown(new_tag)
            col1, col2, col3 = st.columns([0.2,0.6,0.2])
            with col2:
                page_name_input = st.text_input(label="Add a name here",value="")
                if page_name_input:
                    self.new_page_name = page_name_input.strip().replace(" ", "")
                st.button("New Page", on_click=self.add_new_page)

app = App()

app.main()