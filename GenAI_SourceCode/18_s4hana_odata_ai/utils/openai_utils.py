import json
from langchain_openai import ChatOpenAI
from typing import Dict, Any
from utils.config import Config
from utils.logger_utils import setup_logger
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser
import os

logger = setup_logger(__name__)

class OpenAIExtractor:
    """Simple OpenAI-based entity extractor"""
    
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        self.llm = ChatOpenAI(model_name=Config.OPENAI_MODEL, max_tokens=1024)
        #self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
    def extract_sales_order_details(self, user_query: str) -> Dict[str, Any]:
        """Extract sales order details from user query using OpenAI"""
        
        try:
                parser = StructuredOutputParser.from_response_schemas([
                    {
                        "name": "intent",
                        "type": "string",
                        "enum": ["create_sales_order", "check_order_status", "get_price", "unknown"],
                        "description": "The intent of the user query."
                    },
                    {
                        "name": "entities",
                        "type": "object",
                        "properties": {
                            "customer_id": {"type": ["string", "null"], "description": "The ID of the customer or null."},
                            "material_code": {"type": ["string", "null"], "description": "The material code or null."},
                            "quantity": {"type": ["number", "null"], "description": "The quantity or null."},
                            "unit": {"type": ["string", "null"], "enum": ["PC", "KG", "L", None], "description": "The unit of measurement or null."},
                            "order_id": {"type": ["string", "null"], "description": "The order ID or null."},
                            "delivery_date": {"type": ["string", "null"], "format": "date", "description": "The delivery date in YYYY-MM-DD format or null."}
                        },
                        "description": "The extracted entities from the user query."
                    }
                ])
        
                
                prompt_template = ChatPromptTemplate.from_template("""
        Extract sales order information from this user message and return ONLY a JSON response.
        
        User message: "{user_query}"
        
        Return JSON in this exact format:
        {{{{
          "intent": "create_sales_order" | "check_order_status" | "get_price" | "unknown",
          "entities": {{{{
            "customer_id": "extracted customer ID or null",
            "material_code": "extracted material code or null", 
            "quantity": extracted_quantity_number_or_null,
            "unit": "PC" | "KG" | "L" | null,
            "order_id": "extracted order ID or null",
            "delivery_date": "YYYY-MM-DD or null"
          }}}}
        }}}}
        
        Examples:
        - "Create order for customer CUST001, material MAT123, quantity 10" → intent: "create_sales_order"
        - "if the material quantity is not passed, default to 1 and unit to PC"
        - "Check status of order SO12345" → intent: "check_order_status" 
        - "What is price of material MAT456?" → intent: "get_price"
        """)
        
                chain = prompt_template | self.llm | parser
        
                result = chain.invoke({"user_query": user_query})
                logger.info(f"OpenAI response: {result}")
                
                # Add confidence score
                result["confidence"] = 0.8 if result["intent"] != "unknown" else 0.1
                
                return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._fallback_response()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_response()

    def order_status_human_readable(self, order_data) -> str:
            """Generate human-readable order status response in email format"""
            prompt_template = ChatPromptTemplate.from_template("""
            Write an email to customer informing them about their order status, return complete string data.
        
            User message: "{{email_data}}"
        
            Return String in this exact format:
                                                               
            Dear {SoldToParty},

            Thanks for reaching out to us for getting the order status for your order {SalesOrder}.

            The current delivery status of the order is {OverallTotalDeliveryStatus} ({delivery_status_text}).

            The total order value is {TotalNetAmount}.

            Thanks,
            Anubhav Trainings
            https://www.anubhavtrainings.com
            """)

            # Map status codes to human-readable text
            delivery_status_map = {
                "A": "Not yet delivered",
                "B": "Partially delivered",
                "C": "Completely delivered"
            }

            # Get the human-readable status text
            delivery_status = order_data.get('OverallTotalDeliveryStatus', 'Unknown')
            delivery_status_text = delivery_status_map.get(delivery_status, "Status unknown")

            # Prepare the data for the template
            email_data = {
                "SoldToParty": order_data.get('SoldToParty', 'Valued Customer'),
                "SalesOrder": order_data.get('SalesOrder', 'N/A'),
                "OverallTotalDeliveryStatus": delivery_status,
                "delivery_status_text": delivery_status_text,
                "TotalNetAmount": order_data.get('TotalNetAmount', 'N/A')
            }

            # Generate the email using the LLM
            # Initialize the chain with the template
            chain = prompt_template | self.llm

            # Generate the email text
            response = chain.invoke(email_data)

            return response.content
            
            # return (f"📋 Order {order_data.get('order_id', 'N/A')} Status:\nonlocal"
            #         f"Customer: {order_data.get('SoldToParty', 'N/A')}\n"
            #         f"Status: {order_data.get('OverallSDProcessStatus', 'N/A')}\n"
            #         f"Total: {order_data.get('TotalNetAmount', 'N/A')}")

    def _fallback_response(self) -> Dict[str, Any]:
        """Fallback response when OpenAI fails"""
        return {
            "data": {
                "intent": "unknown",
                "confidence": 0.1,
                "entities": {
                    "customer_id": None,
                    "material_code": None,
                    "quantity": None,
                    "unit": None,
                    "order_id": None,
                    "delivery_date": None
                }
            },
            "error": None
        }