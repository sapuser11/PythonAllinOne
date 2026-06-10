from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import retreiver

app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_question(q: Question):
    answer = retreiver.process_workflow(q.question)
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

###You want to call API - python service.py
###Then call API - curl -X POST "http://localhost:8000/ask" 
# -H "Content-Type: application/json" -d '{"question": "What are Hdbkpic?"}'
###Then you will get response like {"answer": "Hdbkpic are high-density polyethylene (HDPE) pipes used for various applications."}