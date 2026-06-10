import requests
import json
from typing import Dict, Any
from datetime import datetime
from utils.config import Config
from utils.auth_utils import SAPAuth
from utils.logger_utils import setup_logger
from utils.data_utils import DataProcessor

logger = setup_logger(__name__)

class SAPService:
    def __init__(self):
        self.auth = SAPAuth()
        self.base_url = Config.SAP_BASE_URL
        self.api_path = Config.SAP_API_PATH
        self.data_processor = DataProcessor()
        
    def create_sales_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create sales order with proper cookie session handling"""
        logger.info(f"=== SAP CREATE ORDER START ===")
        logger.info(f"Input order_data: {json.dumps(order_data, indent=2)}")
        
        try:
            # Step 1: Validate data
            if not self.data_processor.validate_sales_order_data(order_data):
                return {"success": False, "error": "Invalid order data"}
            
            # Step 2: Get CSRF token AND establish session cookies
            logger.info("Step 2: Getting CSRF token and establishing session cookies...")
            csrf_token = self.auth.get_csrf_token_and_cookies()
            if not csrf_token:
                return {"success": False, "error": "Failed to get CSRF token and establish session"}
            
            # Step 3: Create SAP payload
            logger.info("Step 3: Creating SAP payload...")
            sap_payload = {
                "SoldToParty": str(order_data["customer_id"]),
                "SalesOrganization": "CCPL",
                "DistributionChannel": "ZG", 
                "OrganizationDivision": "01",
                "SalesOrderType": "OR",
                "SalesOrderDate": f"/Date({int(datetime.now().timestamp() * 1000)})/",
                "to_Item": {
                    "results": [{
                        "SalesOrderItem": "10",
                        "Material": str(order_data["material_code"]),
                        "RequestedQuantity": str(order_data["quantity"]),
                        "RequestedQuantityUnit": order_data.get("unit") or "PC"
                    }]
                }
            }
            
            logger.info(f"SAP Payload: {json.dumps(sap_payload, indent=2)}")
            
            # Step 4: Make request using established session
            url = f"{self.base_url}{self.api_path}/A_SalesOrder"
            logger.info(f"Step 4: Making request to: {url}")
            
            response = self.auth.make_sap_request(url, sap_payload)
            
            # Step 5: Process response
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Body: {response.text}")
            
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    sales_order_id = result.get("d", {}).get("SalesOrder", "Unknown")
                    
                    return {
                        "success": True,
                        "sales_order_id": sales_order_id,
                        "message": f"Order {sales_order_id} created successfully",
                        "data": result
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "sales_order_id": "Created",
                        "message": "Order created successfully",
                        "raw_response": response.text
                    }
            else:
                return {
                    "success": False,
                    "error": f"SAP API error: {response.status_code}",
                    "details": {
                        "response_body": response.text,
                        "cookies_sent": dict(self.auth.session.cookies)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error creating sales order: {e}")
            return {"success": False, "error": str(e)}
        finally:
            logger.info("=== SAP CREATE ORDER END ===")

    def get_sales_order(self, sales_order_id: str) -> Dict[str, Any]:
        """Get sales order details"""
        try:
            headers = self.auth.get_basic_auth_header()
            url = f"{self.base_url}{self.api_path}/A_SalesOrder('{sales_order_id}')?$expand=to_Item"
            
            response = self.auth.session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False, 
                    "error": f"Order not found: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error getting sales order: {e}")
            return {"success": False, "error": str(e)}
    
    def get_material_price(self, material_code: str, customer_id: str = None) -> Dict[str, Any]:
        """Get material pricing"""
        return {
            "success": True,
            "material_code": material_code,
            "unit_price": "100.00",
            "currency": "USD",
            "note": "Mock pricing - works from chatbot"
        }