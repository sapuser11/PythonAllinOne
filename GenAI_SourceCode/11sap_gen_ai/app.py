from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import streamlit as st
from langchain.memory import ConversationBufferMemory

load_dotenv()

os.environ["AICORE_HOME"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/profiles"
os.environ["AICORE_PROFILE"] = "anubhav"
dep_id = os.getenv("LLM_DEPLOYMENT_ID")

proxy_client = get_proxy_client('gen-ai-hub')

llm = ChatOpenAI(proxy_model_name='gpt-35-turbo', proxy_client=proxy_client, deployment_id=dep_id)

# Initialize memory
memory = ConversationBufferMemory(return_messages=True)

# Streamlit UI
st.title("🤖 Funny Chatbot")
st.write("Chat with me! I'll try to be entertaining!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("You are a witty and humorous assistant. Keep responses short and funny."),
            #SystemMessagePromptTemplate.from_template("You are a experienced abap developer."),
            HumanMessagePromptTemplate.from_template("{text}")
        ])
        chain = chat_prompt | llm | StrOutputParser()
        response = chain.invoke({'text': prompt})
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})