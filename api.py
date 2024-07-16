import google.generativeai as genai
from config_loader import get_api

class Chatbot:
    def __init__(self):
        genai.configure(api_key=get_api())
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

# print(response.text)

