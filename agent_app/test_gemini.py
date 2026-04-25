import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    print("Testing Gemini connectivity...")
    response = llm.invoke("Hello, are you there?")
    print(f"Response: {response.content}")
    print("Success!")
except Exception as e:
    print(f"Gemini Test Failed: {e}")
