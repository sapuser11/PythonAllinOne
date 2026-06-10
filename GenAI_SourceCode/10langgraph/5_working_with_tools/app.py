from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langgraph.prebuilt import chat_agent_executor
from tools.local_tools import my_custom_tool, update_vendor_data
import streamlit as st
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")


store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

##Create object of chatgpt llm
llm = ChatOpenAI(model_name="gpt-4.1-mini", max_tokens=1024)
stringParser=StrOutputParser()

##Create object of a tool
tavily = TavilySearch(max_results=1)
tools = [tavily, my_custom_tool, update_vendor_data]
llm.bind_tools(tools)

#with_message_history = RunnableWithMessageHistory(llm, get_session_history)
llm_with_tools = chat_agent_executor.create_tool_calling_executor(llm, tools)

config = {"configurable": {"session_id": "anubhav_chat"}}

##Pass my Question
print("Bot: Hello! Ask me anything. Type 'exit' to end the conversation.")

while True:
    user_input = input("Enter your question (You): ")
    if user_input.lower() == 'exit':
        print("Bot: Goodbye!")
        break

    response = llm_with_tools.invoke({
        "messages": [HumanMessage(content=user_input)]
    }, config=config)
    
    print("Bot:", response["messages"][-1].content)
    print("is tool used? :", response["messages"][-2].name)