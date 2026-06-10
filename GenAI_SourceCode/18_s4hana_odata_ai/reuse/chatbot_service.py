from typing import Dict, Any
from reuse.nlp_processor import extract_sales_order_details
from reuse.odata_processor import SAPService
from model.entities import ChatbotResponse
from utils.openai_utils import OpenAIExtractor
from utils.logger_utils import setup_logger

logger = setup_logger(__name__)

class ChatbotService:
    def __init__(self):
        self.sap_service = SAPService()
        self.openai_utils = OpenAIExtractor()
        
    def process_message(self, user_message: str) -> ChatbotResponse:
        """Main method to process user messages and return responses"""
        try:
            # Step 1: Extract sales order details using OpenAI
            sales_order_details = extract_sales_order_details(user_message)
            
            intent = sales_order_details.get("intent")
            entities = sales_order_details.get("entities", {})
            
            logger.info(f"Processing intent: {intent}")
            
            # Step 2: Route to appropriate handler based on intent
            if intent == "create_sales_order":
                return self.handle_create_sales_order(entities, user_message)
            elif intent == "check_order_status":
                return self.handle_check_order_status(entities, user_message)
            elif intent == "get_price":
                return self.handle_get_price(entities, user_message)
            else:
                return ChatbotResponse(
                    message="I can help you with:\n- Creating sales orders\n- Checking order status\n- Getting material prices",
                    success=True
                )
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return ChatbotResponse(
                message="Sorry, I encountered an error. Please try again.",
                success=False,
                error=str(e)
            )
    
    def handle_create_sales_order(self, entities: Dict[str, Any], original_message: str) -> ChatbotResponse:
        """Handle sales order creation requests"""
        
        # Check required fields
        required_fields = ['customer_id', 'material_code', 'quantity']
        missing_fields = [field for field in required_fields if not entities.get(field)]
        
        if missing_fields:
            return ChatbotResponse(
                message=f"Missing information: {', '.join(missing_fields)}\n"
                       f"Example: 'Create order for customer CUST001, material MAT123, quantity 10'",
                success=False,
                error="Missing required fields"
            )
        
        # Prepare order data with defaults
        order_data = {
            "customer_id": entities.get("customer_id"),
            "material_code": entities.get("material_code"),
            "quantity": entities.get("quantity"),
            "unit": entities.get("unit", "PC"),
            "delivery_date": entities.get("delivery_date"),
            "order_type": "OR"
        }
        
        # Call SAP service
        result = self.sap_service.create_sales_order(order_data)
        
        if result["success"]:
            return ChatbotResponse(
                message=f"✅ Sales order created!\n"
                       f"Order ID: {result['sales_order_id']}\n"
                       f"Customer: {order_data['customer_id']}\n"
                       f"Material: {order_data['material_code']}\n"
                       f"Quantity: {order_data['quantity']}",
                success=True,
                data=result
            )
        else:
            return ChatbotResponse(
                message=f"❌ Failed to create order: {result.get('error')}",
                success=False,
                error=result.get('error')
            )
    
    def handle_check_order_status(self, entities: Dict[str, Any], original_message: str) -> ChatbotResponse:
        """Handle order status check requests"""
        
        order_id = entities.get("order_id")
        if not order_id:
            return ChatbotResponse(
                message="Please provide order ID. Example: 'Check status of order SO12345'",
                success=False,
                error="Order ID not provided"
            )
        
        result = self.sap_service.get_sales_order(order_id)

        if result["success"]:
            order_data = result["data"].get("d", {})
            response = self.openai_utils.order_status_human_readable(order_data)
            
            return ChatbotResponse(
                message=response,
                success=True,
                data=result
            )
        else:
            return ChatbotResponse(
                message=f"❌ Order {order_id} not found",
                success=False,
                error=result.get('error')
            )
    
    def handle_get_price(self, entities: Dict[str, Any], original_message: str) -> ChatbotResponse:
        """Handle material price requests"""
        print("Getting price for entities:", entities)
        material_code = entities.get("material_code")
        if not material_code:
            return ChatbotResponse(
                message="Please provide material code. Example: 'What is price of material MAT123?'",
                success=False,
                error="Material code not provided"
            )
        
        customer_id = entities.get("customer_id")
        result = self.sap_service.get_material_price(material_code, customer_id)
        
        if result["success"]:
            return ChatbotResponse(
                message=f"Price for {material_code}: {result['unit_price']} {result['currency']}",
                success=True,
                data=result
            )
        else:
            return ChatbotResponse(
                message=f"❌ Could not get price for {material_code}",
                success=False,
                error=result.get('error')
            )