import google.generativeai as genai
import os 
import json

class GoogleModel:
    def __init__(self):
        self.model_name = "gemini-pro"
        with open("diary/models/secrests.json", "r") as f:
            self.env_vars = json.load(f)
    
    def make_pipeline(self):
        # Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
        GOOGLE_API_KEY=self.env_vars['GOOGLE_API_KEY'].strip()
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        return model.generate_content