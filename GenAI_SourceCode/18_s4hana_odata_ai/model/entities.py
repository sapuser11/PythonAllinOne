from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SalesOrderItem(BaseModel):
    material_code: str = Field(..., description="Material/Product code")
    quantity: float = Field(..., gt=0, description="Quantity to order")
    unit: str = Field(default="PC", description="Unit of measure")
    price: Optional[float] = Field(None, description="Unit price")

class SalesOrderRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    sales_org: str = Field(default="1000", description="Sales organization")
    distribution_channel: str = Field(default="10", description="Distribution channel")
    division: str = Field(default="00", description="Division")
    order_type: str = Field(default="OR", description="Order type")
    requested_delivery_date: Optional[str] = Field(None, description="Requested delivery date")
    items: List[SalesOrderItem] = Field(..., description="Order items")
    reference: Optional[str] = Field(None, description="Reference document")

class NLPExtraction(BaseModel):
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    
class ChatbotResponse(BaseModel):
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    success: bool = Field(..., description="Success status")
    error: Optional[str] = Field(None, description="Error message if any")