import google.generativeai as genai
from models.gemini import GoogleModel
from models.gemini import GoogleModel

genai.configure(api_key="AIzaSyBrh5bOh7RaTWA805GbIj9nnz9j9R18Lgs")  # Make sure to set your API key in the environment variable
model = genai.GenerativeModel('gemini-pro')

class Vocabulary:
    def __init__(self, content):
        self.content = content

    def generate_vocabulary(self, message_data):
        english_words_prompt = f"""
            The purpose of this vocabulary development prompt is to guide the creation of a specialized vocabulary based on a specific content domain. The vocabulary will include words relevant to the chosen content, along with their respective parts of speech, meanings in both English and Vietnamese, usage, and examples. This exercise aims to enhance understanding and communication within the chosen domain by expanding the vocabulary repertoire.

                Components of the Vocabulary Entry:
                1. Word: The term being added to the vocabulary.
                2. Part of Speech: The grammatical category to which the word belongs (e.g., noun, verb, adjective, adverb).
                3. Meaning (English): A concise definition or explanation of the word's significance in English.
                4. Meaning (Vietnamese): The equivalent translation or interpretation of the word in Vietnamese.
                5. Usage: How the word is typically used or applied within the context of the content domain.
                6. Example: A sentence or phrase demonstrating the word's usage in context.

                Instructions for Creating Vocabulary Entries:
                1. For each word selected, provide the following components in a clear and organized manner.
                2. Ensure accuracy and clarity in defining the meanings of words.
                3. Include relevant information on part of speech and usage to facilitate understanding.
                4. Provide diverse and illustrative examples to demonstrate the word's usage effectively.
                5. Use language appropriate to the target audience's proficiency level within the domain.

                Example Vocabulary Entry:

                ---------------------------------------------------------------------
                - Word 1: Encryption
                - Part of Speech: Noun
                - Meaning (English): The process of encoding information or data in such a way that only authorized parties can access it, typically through the use of algorithms and keys.
                - Meaning (Vietnamese): Quá trình mã hóa thông tin hoặc dữ liệu một cách sao cho chỉ có các bên được ủy quyền mới có thể truy cập, thông thường thông qua việc sử dụng thuật toán và khóa.
                - Usage: Encryption is commonly employed in data security protocols to safeguard sensitive information from unauthorized access.
                - Example: The company utilizes strong encryption techniques to protect customer data during transmission over the internet.
                ---------------------------------------------------------------------

                This tis the content you will extract and make the vocabulary on this: {message_data} 
        """
        model = genai.GenerativeModel('gemini-pro')
        english_words_response = model.generate_content(english_words_prompt)
        extracted_words = english_words_response.text
        self.content = extracted_words.replace("*", "")
        return self.content
    
    def get_vocabulary(self):
        return self.content
    


    

