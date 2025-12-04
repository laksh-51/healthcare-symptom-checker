from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import List, Union, Dict, Any
import json

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
# ----------------------------

from app.llm_client import query_llm
from app.db import create_query_table, log_query_result, get_query_history

app = FastAPI(title="Healthcare Symptom Checker")

templates = Jinja2Templates(directory="app/templates")


app.mount("/static", StaticFiles(directory="app/static"), name="static")


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
        # Step 2a: Clean the LLM output string to remove ```json markdown
        clean_output = llm_output.strip()
        if clean_output.startswith("```"):
            clean_output = clean_output.strip("`").lstrip("json").strip()

        # Step 2b: NEW ROBUSTNESS FIX - Slice the string to ensure it ONLY contains the JSON object
        start_index = clean_output.find('{')
        end_index = clean_output.rfind('}')
        
        if start_index != -1 and end_index != -1 and end_index > start_index:
            # Slice the string to include only the JSON object (from first { to last })
            json_string = clean_output[start_index : end_index + 1]
        else:
            # Fallback to the original cleaned output if braces aren't found
            json_string = clean_output
        
        llm_data_dict = json.loads(json_string)
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
        # get_query_history will now raise a RuntimeError if it fails
        history_logs = get_query_history(limit=10)
        return {"history": history_logs}
    except Exception as e:
        # MANUAL RAISE EXCEPTION for history endpoint failures
        print(f"History endpoint error: {e}")
        # The detail will now contain the full error message from app/db.py
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Error in History Fetch: {e}"
        )