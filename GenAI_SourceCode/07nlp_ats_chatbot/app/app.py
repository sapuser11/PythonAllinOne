import streamlit as st
import requests
import time
import json

st.set_page_config(
    page_title="Anubhav Training Bot",
    page_icon="🤖",
    layout="wide"
)

def get_bot_response(question):
    try:
        response = requests.post("https://ats-bot-api-silly-oribi-vg.cfapps.us10-001.hana.ondemand.com/ask", json={"input": {"question": question}})
        if response.status_code == 200:
            return response.json().get("answer", "Sorry, I didn't get that.")
        else:
            return "Error: Unable to get a response from the bot."
    except Exception as e:
        return f"Error: {e}"

st.title("Anubhav Training Bot")

##Create a center aligned content
with st.container():
    st.write("## Ask your question:")
    user_question = st.text_input("Question:")
    if st.button("Submit"):
        with st.spinner("Thinking..."):
            time.sleep(2)  # Simulate a delay
            bot_response = get_bot_response(user_question)
        st.write("### Bot Response:")
        st.write(bot_response)