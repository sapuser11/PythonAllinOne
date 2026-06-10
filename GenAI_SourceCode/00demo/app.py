# Import all the dependencies
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain_core.output_parsers import StrOutputParser
import os
# Import dependencies to make web api
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

# Initialize a web service
app = FastAPI(
    title="Anubhav Trainings ABAP assistant",
    description="First Chat bot with Gen AI",
    version="1.0.0"
)

# Serve a folder where we keep our fiori app
static_dir = Path(__file__).parent / "webapp"
if static_dir.exists():
    app.mount("/webapp", StaticFiles(directory=static_dir), name="webapp")


# Define the input and output data for the API
class ChatRequest(BaseModel):
    question:str
class ChatResponse(BaseModel):
    response:str


# to consume sap ai core service in BTP we need to load configuration (service key)
os.environ["AICORE_HOME"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/profiles"
os.environ["AICORE_PROFILE"] = "anubhav"

#A proxy client = a handler which communicates to AI core service
proxy_client = get_proxy_client('gen-ai-hub')

##initialize the llm which we want to use
llm = ChatOpenAI(proxy_model_name="gpt-35-turbo", proxy_client=proxy_client)

##set a prompt template to fix the context in which the AI should response
chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("You are a sap abap coding assistant, you will help the user with abap coding problems, respond sorry with a joke in case the question is related to non abap"),
    HumanMessagePromptTemplate.from_template("{spiderman}")
])

##Create the chain object using langchain
chain = chat_prompt | llm | StrOutputParser()

# local testing
# user_inp = input("please ask your question : ")

@app.post("/chat", response_model=ChatResponse, tags=["Cghat"])
async def chat(request: ChatRequest):

    if not request.question:
        raise HTTPException(status_code=400, detail="No question was provided")

    response = chain.invoke({'spiderman': request.question})

    print(response)
    return ChatResponse(response=response)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
