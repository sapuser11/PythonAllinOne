from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert developer in SAP BTP CAPM, please provide detailed technical information on the CAP programming for Node JS"),
    ("human","Question:{input}")
])

##Create object of chatgpt llm
llm = ChatOpenAI(model_name="gpt-4.1-mini", max_tokens=1024)
stringParser=StrOutputParser()

##Create langchain object
# chain = LLMChain(llm=llm, prompt=prompt, output_parser=stringParser)
chain = prompt | llm | stringParser

##Create a simple chatbot UI
st.title("CAPM Expert Chatbot")

user_input = st.text_input("Ask a question about CAPM:")
if st.button("Submit"):
    response = chain.invoke({"input": user_input})
    st.text_area("Response:", value=response, height=300)

