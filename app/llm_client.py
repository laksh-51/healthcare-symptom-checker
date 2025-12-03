import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def query_llm(symptoms: str):
    prompt = f"""
    You are an educational healthcare assistant.
    Input symptoms: {symptoms}
    Instructions:
    - Do NOT provide a diagnosis.
    - Do NOT give medical advice or medications.
    - Suggest possible condition categories only.
    - List any red-flag symptoms to watch.
    - Provide recommended next steps in general terms.
    - ALWAYS include this disclaimer: 'This information is for educational purposes only. Consult a qualified medical professional for any health concerns.'
    Output in JSON format:
    {{
        "possible_conditions": [],
        "reasoning": "",
        "red_flags": [],
        "recommended_next_steps": [],
        "disclaimer": ""
    }}
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}
