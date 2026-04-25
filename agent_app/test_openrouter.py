import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

try:
    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )
    print("Testing OpenRouter (Gemini 2.0 Flash) connectivity...")
    response = llm.invoke("Hello, are you there?")
    print(f"Response: {response.content}")
    print("Success!")
except Exception as e:
    print(f"OpenRouter Test Failed: {e}")
