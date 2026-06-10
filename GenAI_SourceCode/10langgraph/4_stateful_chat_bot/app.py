from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from dotenv import load_dotenv
from langserve import add_routes
from openai import BaseModel
import streamlit as st
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

##Create object of chatgpt llm
llm = ChatOpenAI(model_name="gpt-4.1-mini", max_tokens=1024)
stringParser=StrOutputParser()

with_message_history = RunnableWithMessageHistory(llm, get_session_history)

config = {"configurable": {"session_id": "anubhav_chat"}}

##Pass my Question
print("Bot: Hello! Ask me anything. Type 'exit' to end the conversation.")

while True:
    user_input = input("Enter your question (You): ")
    if user_input.lower() == 'exit':
        print("Bot: Goodbye!")
        break

    response = with_message_history.invoke([HumanMessage(content=user_input)], config=config)
    print("Bot:", response.content)