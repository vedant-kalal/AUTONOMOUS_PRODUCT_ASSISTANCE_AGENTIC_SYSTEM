import os 
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def load_llm():
    # User requested Groq for speed
    llm = ChatGroq(
        model="openai/gpt-oss-120b", 
        temperature=0,
    )
    return llm      