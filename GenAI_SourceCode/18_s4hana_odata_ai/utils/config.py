import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SAP Configuration
    SAP_BASE_URL = os.getenv("SAP_BASE_URL", "https://your-sap-system.com")
    SAP_CLIENT = os.getenv("SAP_CLIENT", "800")
    SAP_USERNAME = os.getenv("SAP_USERNAME")
    SAP_PASSWORD = os.getenv("SAP_PASSWORD")
    SAP_API_PATH = "/sap/opu/odata/sap/API_SALES_ORDER_SRV"
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Application Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"