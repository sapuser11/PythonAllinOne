from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import re
from recommender import get_movie_recommendation, data

app = FastAPI(title="ATS Movie Recommendation API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    query: str

class Movie(BaseModel):
    id: str
    name: str
    image: str

class RecommendationResponse(BaseModel):
    recommendations: List[Movie]

@app.get("/")
def root():
    return {"status": "Movie Recommendation API is running"}

@app.post("/recommend", response_model=RecommendationResponse)
def recommend_movies(request: RecommendationRequest):
    """Get 5 movie recommendations"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get recommendation from your engine
        response = get_movie_recommendation(request.query)
        
        return RecommendationResponse(recommendations=response['result'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)