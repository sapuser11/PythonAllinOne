from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI, OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain_core.output_parsers import StrOutputParser

##A module that communicate to vector store and pass data to LLM - Retriever
from langchain.chains import RetrievalQA
##Prepare chunks using specialized modules which create chunks
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
##a Loader library to load data from text
from langchain_community.document_loaders import TextLoader
##Communicate to SAP HANA vector store
from langchain_hana import HanaDB

from dotenv import load_dotenv
import os
from langchain.memory import ConversationBufferMemory
import logging
from cfenv import AppEnv
from hdbcli import dbapi
import streamlit as st

##1. Load Environment Variables
load_dotenv()
##2. Load Cloud Foundry Environment Variables
env = AppEnv()

##3. Prepare Logging
FORMAT = "%(asctime)s:%(name)s:%(levelname)s - %(message)s"
# Use filename="file.log" as a param to logging to log to a file
logging.basicConfig(format=FORMAT, level=logging.INFO)

# Check if running locally or in Cloud Foundry
if env.name is None:
    ##4. Set Environment variables - locally
    os.environ["AICORE_HOME"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/profiles"
    os.environ["AICORE_PROFILE"] = "anubhav"
    os.environ["HANA_HOST"] = os.getenv("db_host")
    os.environ["HANA_PORT"] = os.getenv("db_port")
    os.environ["HANA_USER"] = os.getenv("db_user")
    os.environ["HANA_PASSWORD"] = os.getenv("db_password")

    #5. Running locally - use environment variables
    print("Running locally - using environment variables")
    hana = {
        'credentials': {
            'host': os.getenv("db_host"),
            'port': os.getenv("db_port"),
            'user': os.getenv("db_user"),
            'password': os.getenv("db_password"),
            'certificate': os.getenv("HANA_CERTIFICATE", None)  # Optional for local
        }
    }
    
    # Validate required environment variables
    required_vars = ['HANA_HOST', 'HANA_USER', 'HANA_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {missing_vars}")
        hana = None
    else:
        logging.info(f"Local HANA connection configured for host: {hana['credentials']['host']}")
        
else:
    ##4. HANA Service Configuration
    hana_service = 'hana'

    # Running in Cloud Foundry - use bound service
    print("Running in Cloud Foundry - using bound service")
    hana = env.get_service(label=hana_service)
    
    if hana is None:
        logging.error(f"HANA service '{hana_service}' not found in Cloud Foundry")
    else:
        logging.info(f"Cloud Foundry HANA service found: {hana_service}")

class vector_store():
    
    def __init__(self) -> None:

        dep_id = os.getenv("LLM_DEPLOYMENT_ID")
        embedding_dep_id = os.getenv("LLM_EMBEDDING_MODEL_ID")
        
        if dep_id is None:
            dep_id = "dd43d1107ac0d426"
        
        if embedding_dep_id is None:
            embedding_dep_id = "d856a7666fd42d17"

        print("deployment id : ", dep_id)
        print("embedding deployment id : ", embedding_dep_id)

        proxy_client = get_proxy_client('gen-ai-hub')

        self.model = ChatOpenAI(proxy_model_name='gpt-35-turbo', proxy_client=proxy_client, deployment_id=dep_id)
        self.embedding_model = OpenAIEmbeddings(proxy_client=proxy_client, deployment_id=embedding_dep_id)
        
        self.conn = None
        self.db = None
        self.retriever = None
        self.chunks = None

 
    def set_db_connection(self) -> None:

        if hana is not None:

            # Handle different data structures for local vs Cloud Foundry
            if env.name is None:  # Local environment - hana is a dict
                dbHost = hana['credentials']['host']
                dbPort = hana['credentials']['port']
                dbUser = hana['credentials']['user']
                dbPwd = hana['credentials']['password']
                ssl_cert = ""
            else:  # Cloud Foundry environment - hana is a service object
                dbHost = hana.credentials['host']
                dbPort = hana.credentials['port']
                dbUser = hana.credentials['user']
                dbPwd = hana.credentials['password']
                ssl_cert = hana.credentials['certificate']

            self.conn = dbapi.connect(
                address = dbHost,
                port = dbPort,
                user = dbUser,
                password = dbPwd,
                encrypt = 'true',
                sslTrustStore = ssl_cert
                )


    def load_textfile(self, file_path: str) -> None:

        ##Load the text file based on input path
        loader = TextLoader(file_path)
        ##Get the contents of the file
        documents = loader.load()
        ##Split the content into chunks
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        # text_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=500,
        #     chunk_overlap=100,
        #     length_function=len,
        #     separator=["\n\n", "\n", " ", ""], ##Hierarchical seprator
        #     is_separator_regex=False
        # )
        self.chunks = text_splitter.split_documents(documents)

        ##Print chunk size and each chunk token
        print(f"Number of chunks created: {len(self.chunks)}")
        for i, chunk in enumerate(self.chunks):
            print(f"Chunk {i} (size: {len(chunk.page_content)}): ...")


    def save_embeddings_to_db(self, table_name) -> None:
        if self.conn is None:
            self.set_db_connection()
        
        if self.conn is not None and self.chunks is not None:
            self.db = HanaDB(connection=self.conn, embedding=self.embedding_model, table_name=table_name)
            ##Delete chunks which are already there
            self.db.delete(filter={})
            ##Save the embeddings in hana vector db
            self.db.add_documents(self.chunks)
            print(f"Embeddings saved to table {table_name}")

    def init_retriever(self) -> None:
        if self.conn is None:
            self.set_db_connection()

        if self.conn is not None:
            self.retriever = self.db.as_retriever()

    def get_retriever_qa(self) -> RetrievalQA:
        if self.retriever is None:
            self.init_retriever()

        if self.retriever is not None:
            qa_chain = RetrievalQA.from_llm(
                llm=self.model,
                retriever=self.retriever
            )
            return qa_chain
        else:
            print("Retriever is not initialized.")
            return None

##Run the design time for creating the vector store
app = vector_store()
app.set_db_connection()
app.load_textfile("./ats_profile.txt")
app.save_embeddings_to_db("ats_profile_embeddings")
app.init_retriever()
retriever=app.get_retriever_qa()

st.title("Simple Anubhav RAG application")
user_query = st.text_input("Enter your question related to Anubhav Trainings:")

if st.button("Get Answer"):
    response = retriever.invoke(user_query)
    st.write("Response:", response['result'])

# if __name__ == '__main__':
#     # Create a sample input message
