import streamlit as st
import json
import os
from datetime import datetime
from io import StringIO
import logging

# Import your existing vector store class and dependencies
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI, OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_hana import HanaDB
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
import pandas as pd
import hana_ml
from hana_ml import dataframe
from cfenv import AppEnv
from hdbcli import dbapi

# Initialize environment
load_dotenv()
env = AppEnv()

# Setup logging
FORMAT = "%(asctime)s:%(name)s:%(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

# Database configuration (same as your original code)
if env.name is None:
    os.environ["AICORE_HOME"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/profiles"
    os.environ["AICORE_PROFILE"] = "anubhav"
    os.environ["HANA_HOST"] = os.getenv("db_host")
    os.environ["HANA_PORT"] = os.getenv("db_port")
    os.environ["HANA_USER"] = os.getenv("db_user")
    os.environ["HANA_PASSWORD"] = os.getenv("db_password")

    hana = {
        'credentials': {
            'host': os.getenv("db_host"),
            'port': os.getenv("db_port"),
            'user': os.getenv("db_user"),
            'password': os.getenv("db_password"),
            'certificate': os.getenv("HANA_CERTIFICATE", None)
        }
    }
    
    required_vars = ['HANA_HOST', 'HANA_USER', 'HANA_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {missing_vars}")
        hana = None
    else:
        logging.info(f"Local HANA connection configured for host: {hana['credentials']['host']}")
else:
    hana_service = 'hana'
    hana = env.get_service(label=hana_service)
    
    if hana is None:
        logging.error(f"HANA service '{hana_service}' not found in Cloud Foundry")
    else:
        logging.info(f"Cloud Foundry HANA service found: {hana_service}")

class EnhancedVectorStore():
    def __init__(self, config=None) -> None:
        # Load configuration
        self.config = config if config else self.load_default_config()
        
        dep_id = os.getenv("LLM_DEPLOYMENT_ID")
        embedding_dep_id = os.getenv("LLM_EMBEDDING_MODEL_ID")
        proxy_client = get_proxy_client('gen-ai-hub')

        # Initialize model with configuration
        self.model = ChatOpenAI(
            proxy_model_name='gpt-35-turbo', 
            proxy_client=proxy_client, 
            deployment_id=dep_id,
            temperature=self.config['llm_settings']['temperature'],
            top_p=self.config['llm_settings']['top_p'],
            max_tokens=self.config['llm_settings']['max_tokens']
        )
        
        self.embeddingModel = OpenAIEmbeddings(proxy_client=proxy_client, deployment_id=embedding_dep_id)
        
        self.conn = None
        self.db = None
        self.retriever = None
        self.chunks = None
        self.documents = None

    def load_default_config(self):
        return {
            'text_splitter': {
                'type': 'CharacterTextSplitter',
                'chunk_size': 500,
                'chunk_overlap': 50
            },
            'llm_settings': {
                'temperature': 0.7,
                'top_p': 1.0,
                'top_k': 50,
                'max_tokens': 1000
            },
            'vector_store': {
                'table_name': 'CUSTOM_EMBEDDINGS'
            }
        }

    def set_db_connection(self) -> bool:
        if hana is not None:
            try:
                if env.name is None:
                    dbHost = hana['credentials']['host']
                    dbPort = hana['credentials']['port']
                    dbUser = hana['credentials']['user']
                    dbPwd = hana['credentials']['password']
                    ssl_cert = ""
                else:
                    dbHost = hana.credentials['host']
                    dbPort = hana.credentials['port']
                    dbUser = hana.credentials['user']
                    dbPwd = hana.credentials['password']
                    ssl_cert = hana.credentials['certificate']

                self.conn = dbapi.connect(
                    address=dbHost,
                    port=dbPort,
                    user=dbUser,
                    password=dbPwd,
                    encrypt='true',
                    autocommit=True,
                    sslTrustStore=ssl_cert
                )
                logging.info("Database connection established successfully")
                return True
            except Exception as e:
                logging.error(f"Failed to establish database connection: {e}")
                self.conn = None
                return False
        return False

    def load_text_content(self, content: str) -> bool:
        try:
            # Create a temporary file-like object from the content
            from langchain_community.document_loaders import TextLoader
            from langchain.docstore.document import Document
            
            # Create document from content
            self.documents = [Document(page_content=content)]
            
            # Split the text into chunks based on configuration
            splitter_type = self.config['text_splitter']['type']
            chunk_size = self.config['text_splitter']['chunk_size']
            chunk_overlap = self.config['text_splitter']['chunk_overlap']
            
            if splitter_type == 'CharacterTextSplitter':
                text_splitter = CharacterTextSplitter(
                    chunk_size=chunk_size, 
                    chunk_overlap=chunk_overlap
                )
            else:  # RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size, 
                    chunk_overlap=chunk_overlap
                )

            self.chunks = text_splitter.split_documents(self.documents)
            logging.info(f"Successfully split text into {len(self.chunks)} chunks")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load text content: {e}")
            self.chunks = None
            return False

    def check_existing_embeddings(self, table_name: str) -> bool:
        if self.conn is not None:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                cursor.close()
                return count > 0
            except Exception as e:
                return False
        return False

    def save_embeddings_to_db(self, table_name: str) -> bool:
        if self.conn is not None and self.chunks is not None:
            try:
                self.db = HanaDB(
                    embedding=self.embeddingModel,
                    connection=self.conn,
                    table_name=table_name
                )
                
                self.db.add_documents(self.chunks)
                logging.info(f"Successfully saved {len(self.chunks)} document chunks to database")
                return True
            except Exception as e:
                logging.error(f"Failed to save embeddings to database: {e}")
                self.db = None
                return False
        return False

    def load_existing_embeddings(self, table_name: str) -> bool:
        if self.conn is not None:
            try:
                self.db = HanaDB(
                    embedding_function=self.embeddingModel,
                    connection=self.conn,
                    table_name=table_name
                )
                logging.info(f"Successfully loaded existing embeddings from table {table_name}")
                return True
            except Exception as e:
                logging.error(f"Failed to load existing embeddings: {e}")
                return False
        return False

    def init_retriever(self) -> bool:
        if self.db is not None:
            try:
                self.retriever = self.db.as_retriever()
                logging.info("Retriever initialized successfully")
                return True
            except Exception as e:
                logging.error(f"Failed to initialize retriever: {e}")
                self.retriever = None
                return False
        return False

    def get_retriever_qa(self) -> RetrievalQA:
        if self.retriever is not None:
            try:
                retrieval_qa = RetrievalQA.from_llm(
                    llm=self.model,
                    retriever=self.retriever
                )
                return retrieval_qa
            except Exception as e:
                logging.error(f"Failed to create RetrievalQA: {e}")
                return None
        return None

def save_config_to_json(config, filename="rag_config.json"):
    """Save configuration to JSON file"""
    try:
        config['timestamp'] = datetime.now().isoformat()
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Failed to save configuration: {e}")
        return False

def load_config_from_json(filename="rag_config.json"):
    """Load configuration from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
    return None

# Initialize session state
if 'config' not in st.session_state:
    # Try to load existing config
    saved_config = load_config_from_json()
    if saved_config:
        st.session_state.config = saved_config
    else:
        st.session_state.config = {
            'text_splitter': {
                'type': 'CharacterTextSplitter',
                'chunk_size': 500,
                'chunk_overlap': 50
            },
            'llm_settings': {
                'temperature': 0.7,
                'top_p': 1.0,
                'top_k': 50,
                'max_tokens': 1000
            },
            'vector_store': {
                'table_name': 'CUSTOM_EMBEDDINGS'
            }
        }

if 'rag_initialized' not in st.session_state:
    st.session_state.rag_initialized = False
    st.session_state.vector_store_app = None
    st.session_state.retriever_qa = None

# Page Layout
st.set_page_config(page_title="RAG Admin Console", layout="wide")

# Create two columns
col1, col2 = st.columns([1, 2])

# LEFT PANEL - Configuration
with col1:
    st.header("⚙️ Configuration")
    
    with st.expander("📄 Text Splitter Settings", expanded=True):
        # Text Splitter Type
        splitter_type = st.selectbox(
            "Text Splitter Type",
            options=["CharacterTextSplitter", "RecursiveCharacterTextSplitter"],
            index=0 if st.session_state.config['text_splitter']['type'] == 'CharacterTextSplitter' else 1
        )
        
        # Chunk Size
        chunk_size = st.number_input(
            "Chunk Size",
            min_value=100,
            max_value=2000,
            value=st.session_state.config['text_splitter']['chunk_size'],
            step=50
        )
        
        # Chunk Overlap
        chunk_overlap = st.number_input(
            "Chunk Overlap",
            min_value=0,
            max_value=500,
            value=st.session_state.config['text_splitter']['chunk_overlap'],
            step=10
        )
    
    with st.expander("🤖 Language Model Settings", expanded=True):
        # Temperature
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.config['llm_settings']['temperature'],
            step=0.1
        )
        
        # Top P
        top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.config['llm_settings']['top_p'],
            step=0.05
        )
        
        # Top K
        top_k = st.slider(
            "Top K",
            min_value=1,
            max_value=100,
            value=st.session_state.config['llm_settings']['top_k'],
            step=1
        )
        
        # Max Tokens
        max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=st.session_state.config['llm_settings']['max_tokens'],
            step=100
        )
    
    with st.expander("🗄️ Vector Store Settings", expanded=True):
        # Table Name
        table_name = st.text_input(
            "HANA Table Name",
            value=st.session_state.config['vector_store']['table_name']
        )
    
    # Save Configuration Button
    if st.button("💾 Save Configuration", type="primary"):
        # Update session state with new values
        st.session_state.config = {
            'text_splitter': {
                'type': splitter_type,
                'chunk_size': chunk_size,
                'chunk_overlap': chunk_overlap
            },
            'llm_settings': {
                'temperature': temperature,
                'top_p': top_p,
                'top_k': top_k,
                'max_tokens': max_tokens
            },
            'vector_store': {
                'table_name': table_name
            }
        }
        
        # Save to JSON file
        if save_config_to_json(st.session_state.config):
            st.success("✅ Configuration saved successfully!")
            st.json(st.session_state.config)
        else:
            st.error("❌ Failed to save configuration")

# RIGHT PANEL - Main Console
with col2:
    st.header("🎓 Anubhav Training RAG System Admin Console")
    
    # File Upload Section
    st.subheader("📎 Document Upload")
    uploaded_file = st.file_uploader(
        "Choose a text file",
        type=['txt'],
        help="Upload a text file to create embeddings for the RAG system"
    )
    
    # Show file details if uploaded
    if uploaded_file is not None:
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size} bytes",
            "File type": uploaded_file.type
        }
        
        st.subheader("📋 File Details")
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")
        
        # Show file content preview
        if st.checkbox("Show file preview"):
            content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            st.text_area("File Content Preview", content[:1000] + "..." if len(content) > 1000 else content, height=200)
    
    # Configuration Status
    st.subheader("⚡ System Status")
    
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        config_status = "✅ Saved" if os.path.exists("rag_config.json") else "❌ Not Saved"
        st.metric("Configuration", config_status)
    
    with col_status2:
        db_status = "✅ Connected" if hana is not None else "❌ Not Connected" 
        st.metric("Database", db_status)
    
    with col_status3:
        rag_status = "✅ Ready" if st.session_state.rag_initialized else "❌ Not Initialized"
        st.metric("RAG System", rag_status)
    
    # Show current configuration
    if st.checkbox("Show Current Configuration"):
        st.json(st.session_state.config)
    
    # Initialize RAG System Button
    st.subheader("🚀 Initialize RAG System")
    
    if uploaded_file is not None:
        if st.button("🔄 Initialize RAG System", type="primary", disabled=st.session_state.rag_initialized):
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            step_container = st.container()
            
            try:
                with step_container:
                    # Step 1: Initialize Vector Store
                    status_text.text("Step 1/6: Initializing Vector Store...")
                    progress_bar.progress(10)
                    
                    app = EnhancedVectorStore(st.session_state.config)
                    st.write("✅ Vector Store object created")
                    
                    # Step 2: Set Database Connection
                    status_text.text("Step 2/6: Establishing Database Connection...")
                    progress_bar.progress(20)
                    
                    if app.set_db_connection():
                        st.write("✅ Database connection established")
                    else:
                        st.error("❌ Failed to establish database connection")
                        st.stop()
                    
                    # Step 3: Process Document
                    status_text.text("Step 3/6: Processing Document...")
                    progress_bar.progress(40)
                    
                    # Read uploaded file content
                    content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
                    
                    if app.load_text_content(content):
                        st.write(f"✅ Document processed into {len(app.chunks)} chunks")
                        
                        # Show chunk preview
                        with st.expander("Document Chunks Preview"):
                            for i, chunk in enumerate(app.chunks[:3]):  # Show first 3 chunks
                                st.write(f"**Chunk {i+1}:** {chunk.page_content[:150]}...")
                    else:
                        st.error("❌ Failed to process document")
                        st.stop()
                    
                    # Step 4: Check Existing Embeddings
                    status_text.text("Step 4/6: Checking Existing Embeddings...")
                    progress_bar.progress(50)
                    
                    table_name = st.session_state.config['vector_store']['table_name']
                    embeddings_exist = app.check_existing_embeddings(table_name)
                    
                    if embeddings_exist:
                        st.write(f"✅ Found existing embeddings in table {table_name}")
                        if app.load_existing_embeddings(table_name):
                            st.write("✅ Existing embeddings loaded")
                        else:
                            st.write("⚠️ Failed to load existing embeddings, creating new ones...")
                            embeddings_exist = False
                    else:
                        st.write(f"ℹ️ No existing embeddings found in table {table_name}")
                    
                    # Step 5: Create/Save Embeddings
                    if not embeddings_exist:
                        status_text.text("Step 5/6: Creating and Saving Embeddings...")
                        progress_bar.progress(70)
                        
                        if app.save_embeddings_to_db(table_name):
                            st.write("✅ Embeddings created and saved to database")
                        else:
                            st.error("❌ Failed to save embeddings to database")
                            st.stop()
                    else:
                        progress_bar.progress(70)
                    
                    # Step 6: Initialize Retriever
                    status_text.text("Step 6/6: Initializing Retriever...")
                    progress_bar.progress(90)
                    
                    if app.init_retriever():
                        st.write("✅ Retriever initialized")
                    else:
                        st.error("❌ Failed to initialize retriever")
                        st.stop()
                    
                    # Final step: Create RetrievalQA
                    retriever_qa = app.get_retriever_qa()
                    if retriever_qa is not None:
                        st.write("✅ RetrievalQA system created")
                        
                        # Store in session state
                        st.session_state.vector_store_app = app
                        st.session_state.retriever_qa = retriever_qa
                        st.session_state.rag_initialized = True
                        
                        progress_bar.progress(100)
                        status_text.text("🎉 RAG System Successfully Initialized!")
                        
                        st.success("🎉 **HANA Vector DB is Ready!**")
                        st.balloons()
                        
                        # Test the system
                        with st.expander("🧪 Test the System"):
                            test_query = st.text_input("Enter a test query:", value="What is this document about?")
                            if st.button("Test Query"):
                                if test_query:
                                    try:
                                        response = retriever_qa.invoke(test_query)
                                        st.write("**Test Response:**")
                                        st.write(response['result'])
                                    except Exception as e:
                                        st.error(f"Test query failed: {e}")
                    else:
                        st.error("❌ Failed to create RetrievalQA system")
                        
            except Exception as e:
                st.error(f"❌ Initialization failed: {e}")
                logging.error(f"RAG initialization failed: {e}")
        
        # Reset button
        if st.session_state.rag_initialized:
            if st.button("🔄 Reset RAG System"):
                st.session_state.rag_initialized = False
                st.session_state.vector_store_app = None
                st.session_state.retriever_qa = None
                st.rerun()
    
    else:
        st.info("📁 Please upload a text file to initialize the RAG system")
    
    # Show initialization status
    if st.session_state.rag_initialized:
        st.success("🎉 RAG System is Ready!")
        
        # Query Interface
        st.subheader("💬 Query Interface")
        user_query = st.text_input("Ask a question:")
        
        if st.button("Submit Query"):
            if user_query.strip():
                try:
                    with st.spinner("Processing query..."):
                        response = st.session_state.retriever_qa.invoke(user_query)
                        st.write("**Response:**")
                        st.write(response['result'])
                        
                        # Show retrieved documents
                        with st.expander("📚 Retrieved Documents"):
                            docs = st.session_state.vector_store_app.retriever.invoke(user_query)
                            for i, doc in enumerate(docs):
                                st.write(f"**Document {i+1}:**")
                                st.write(doc.page_content)
                                
                except Exception as e:
                    st.error(f"Query failed: {e}")
            else:
                st.warning("Please enter a query")

# Sidebar - Additional Controls
with st.sidebar:
    st.header("🔧 Admin Controls")
    
    if st.button("📄 Show Config File"):
        if os.path.exists("rag_config.json"):
            with open("rag_config.json", 'r') as f:
                config_content = f.read()
            st.code(config_content, language="json")
        else:
            st.info("No configuration file found")
    
    if st.button("🗑️ Clear All Data"):
        if st.session_state.rag_initialized:
            st.session_state.rag_initialized = False
            st.session_state.vector_store_app = None
            st.session_state.retriever_qa = None
        if os.path.exists("rag_config.json"):
            os.remove("rag_config.json")
        st.success("All data cleared!")
        st.rerun()
    
    st.subheader("📊 System Info")
    st.write(f"**Config Loaded:** {'Yes' if 'config' in st.session_state else 'No'}")
    st.write(f"**RAG Initialized:** {'Yes' if st.session_state.rag_initialized else 'No'}")
    st.write(f"**Database Available:** {'Yes' if hana is not None else 'No'}")