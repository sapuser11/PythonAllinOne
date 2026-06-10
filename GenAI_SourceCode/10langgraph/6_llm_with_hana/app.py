from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv
from langgraph.prebuilt import chat_agent_executor
from langchain_community.utilities.sql_database import SQLDatabase
import streamlit as st
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
os.environ["db_user"] = os.getenv("db_user")
os.environ["db_password"] = os.getenv("db_password")
os.environ["db_host"] = os.getenv("db_host")
os.environ["db_port"] = os.getenv("db_port")

def connection_test(conn_str):
    from sqlalchemy import create_engine, text
    try:
        engine = create_engine(
            conn_str,
            connect_args={'timeout': 10}
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM DUMMY"))
            print("Connection successful!")
        
    except Exception as e:
        print(f"Connection failed: {e}")

connection_str = f"hana://{os.getenv('db_user')}:{os.getenv('db_password')}@{os.getenv('db_host')}/{os.getenv('db_name')}"
print(connection_str)
connection_test(conn_str=connection_str)

db = SQLDatabase.from_uri(connection_str)

from sqlalchemy import create_engine, text
import time

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)


while True:
    user_input = input("Enter your question (You): ")
    if user_input.lower() == 'exit':
        print("Bot: Goodbye!")
        break

    response = agent_executor.invoke(user_input)

    print("Bot:", response)
    