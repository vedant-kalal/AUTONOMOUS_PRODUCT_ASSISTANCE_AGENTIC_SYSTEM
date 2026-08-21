import os 
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def load_llm():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    
    # Default to openrouter models
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", 
        temperature=0,
        api_key=api_key or "your_openrouter_key",
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://localhost", 
            "X-Title": "Trust Cart AI"
        }
    )
    return llm      