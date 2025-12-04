from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import List, Union, Dict, Any
import json

# --- NEW FRONTEND IMPORTS ---
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
# ----------------------------

from app.llm_client import query_llm
from app.db import create_query_table, log_query_result, get_query_history

app = FastAPI(title="Healthcare Symptom Checker")

# --- FRONTEND SETUP ---
# Initialize Jinja2Templates to find HTML files in app/templates
templates = Jinja2Templates(directory="app/templates")

# Mount StaticFiles to serve CSS, JS, etc., from app/static/
# Files will be accessible at http://127.0.0.1:8000/static/...
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# ----------------------


# Define Pydantic model for the expected LLM output
class LLMResponse(BaseModel):
    possible_conditions: List[str]
    reasoning: str
    red_flags: List[str]
    recommended_next_steps: List[str]
    disclaimer: str


class SymptomRequest(BaseModel):
    symptoms: str


@app.on_event("startup")
def startup_event():
    """Runs when the FastAPI application starts to ensure the DB table exists."""
    create_query_table()


# --- NEW: ROUTE TO SERVE THE MAIN HTML PAGE ---
@app.get("/", include_in_schema=False)
async def home(request: Request):
    """Serves the main HTML page (app/templates/index.html)."""
    return templates.TemplateResponse("index.html", {"request": request})


# ----------------------------------------------


@app.post("/check-symptoms", response_model=LLMResponse)
async def check_symptoms(request: SymptomRequest):
    symptoms_input = request.symptoms.strip()

    if not symptoms_input:
        raise HTTPException(status_code=400, detail="Symptom input cannot be empty")

    # 1. Call LLM client
    llm_output: Union[str, Dict[str, Any]] = query_llm(symptoms_input)

    # Handle LLM API error
    if isinstance(llm_output, dict) and "error" in llm_output:
        print(f"LLM API Error: {llm_output['error']}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while communicating with the AI service.",
        )

    # 2. Parse and Validate LLM JSON output
    try:
        # --- FIX: Clean the LLM output string to remove ```json markdown ---
        clean_output = llm_output.strip()
        if clean_output.startswith("```"):
            clean_output = clean_output.strip("`").lstrip("json").strip()
        # -----------------------------------------------------------------

        llm_data_dict = json.loads(clean_output)
        validated_response = LLMResponse(**llm_data_dict)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"LLM output parsing/validation error: {e}. Raw output: {llm_output}")
        raise HTTPException(
            status_code=500,
            detail="The AI service returned an unreadable or malformed safety-critical response.",
        )

    # 3. Log the query result to PostgreSQL
    log_query_result(symptoms_input, llm_data_dict)

    # 4. Return the validated Pydantic object
    return validated_response


@app.get("/history")
async def get_history():
    """API endpoint to fetch the last 10 query logs."""
    try:
        history_logs = get_query_history(limit=10)
        return {"history": history_logs}
    except Exception as e:
        print(f"History endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve query history.")
