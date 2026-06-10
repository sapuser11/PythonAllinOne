from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
from langserve import add_routes
from openai import BaseModel
import streamlit as st
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# system_prompt = "generate programming code in following {language} language"
system_prompt = "translate text in following {language} language"
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human","{input}")
])

##Create object of chatgpt llm
llm = ChatOpenAI(model_name="gpt-4.1-mini", max_tokens=1024)
stringParser=StrOutputParser()

##Create langchain object
chain = prompt | llm | stringParser

###Choose your protocol
app = FastAPI(title="Personal programmer assistent",
              description="A personal assistant for programming tasks",
              version="1.0.0"
              )

##Create input data model which user will pass
class MyInput(BaseModel):
    language: str
    input: str

##Using langserve to create web api and consume LLM
add_routes(app,chain,path= "/generate_code", input_type=MyInput)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

## http://localhost:8000/generate_code/playground