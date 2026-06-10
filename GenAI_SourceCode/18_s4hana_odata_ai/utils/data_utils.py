import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.logger_utils import setup_logger

logger = setup_logger(__name__)

class DataProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize input text"""
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters except necessary ones
        text = re.sub(r'[^\w\s\-.,@]', '', text)
        return text
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract numbers from text"""
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(num) for num in numbers]
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """Extract date patterns from text"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}'   # MM-DD-YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates
    
    @staticmethod
    def format_sap_date(date_str: str) -> str:
        """Format date for SAP API"""
        try:
            # Try different date formats
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
            # If no format matches, return current date
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.error(f"Error formatting date {date_str}: {str(e)}")
            return datetime.now().strftime('%Y-%m-%d')
    
    @staticmethod
    def validate_sales_order_data(data: Dict[str, Any]) -> bool:
        """Validate sales order data before API call"""
        required_fields = ['customer_id', 'material_code', 'quantity']
        
        for field in required_fields:
            if field not in data or not data[field]:
                logger.error(f"Missing required field: {field}")
                return False
                
        # Validate quantity is positive number
        try:
            quantity = float(data['quantity'])
            if quantity <= 0:
                logger.error("Quantity must be positive")
                return False
        except (ValueError, TypeError):
            logger.error("Invalid quantity format")
            return False
            
        return True