from langchain_openai import ChatOpenAI
import os
llm_with_temp = lambda temp: ChatOpenAI(
    model="gemini-2.0-flash",
    api_key=os.getenv("API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    temperature=temp)
