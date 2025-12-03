from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.llm_client import query_llm

app = FastAPI(title="Healthcare Symptom Checker")

class SymptomRequest(BaseModel):
    symptoms: str

@app.post("/check-symptoms")
async def check_symptoms(request: SymptomRequest):
    if not request.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptom input cannot be empty")
    
    # Call LLM client
    response = query_llm(request.symptoms)
    
    return response
