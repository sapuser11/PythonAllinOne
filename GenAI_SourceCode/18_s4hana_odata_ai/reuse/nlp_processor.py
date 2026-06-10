from typing import Dict, Any
from utils.openai_utils import OpenAIExtractor
from utils.logger_utils import setup_logger

logger = setup_logger(__name__)

def extract_sales_order_details(user_query: str) -> Dict[str, Any]:
    """Extract sales order details using OpenAI - main function"""
    extractor = OpenAIExtractor()
    result = extractor.extract_sales_order_details(user_query)
    print("Extracted details:", result)
    return result