import os
from langchain_groq import ChatGroq

def get_llm(temperature: float = 0.2) -> ChatGroq:
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY"),
    )
