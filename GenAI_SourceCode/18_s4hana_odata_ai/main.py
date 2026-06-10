from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from reuse.chatbot_service import ChatbotService
from model.entities import ChatbotResponse
from utils.logger_utils import setup_logger
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Allowed origins (frontend URLs)
origins = [
    "http://localhost:8080"   # UI5 local dev server
]

# Setup logging
logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Anubhav Trainings S/4HANA Sales Order Chatbot",
    description="NLP-powered chatbot for SAP Sales Order operations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],              # allow all HTTP methods
    allow_headers=["*"],              # allow all headers
)

# Initialize chatbot service
chatbot = ChatbotService()

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    response: str 
    success: bool 
    data: dict 
    error: str 

@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(request: MessageRequest):
    """Main chat endpoint"""
    try:
        logger.info(f"Received message: {request.message}")
        
        # Process the message
        result = chatbot.process_message(request.message)
        
        return MessageResponse(
                    response=result.message or "",
                    success=result.success,
                    data=result.data or {},
                    error=result.error or ""
                )

        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
   
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SAP Sales Order Chatbot"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "<h4>Welcome to <a href='https://coinmarketcap.com/currencies/anubhav-trainings/'>$ATS</a> SAP Sales Order Chatbot API<h4>",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
        },
        "usage": "Send POST request to /chat with {'message': 'your message here'}"
    }

if __name__ == "__main__":
    logger.info("Starting SAP Sales Order Chatbot...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

#http://localhost:8000/docs#    