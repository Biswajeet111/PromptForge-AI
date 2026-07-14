import json
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini Model
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_response(prompt: str) -> str:
    """
    Sends the prompt to Gemini and returns the response.
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error: {str(e)}"

def analyze_prompt_quality(prompt: str) -> dict:
    """
    Analyzes the prompt quality and returns a structured JSON payload.
    """
    analysis_prompt = f"""
    Analyze the following prompt and evaluate its quality based on Clarity, Structure, Context, and Specificity.
    Provide a JSON response with the following schema:
    {{
        "overall_score": <int 0-100>,
        "clarity": <int 0-100>,
        "structure": <int 0-100>,
        "context": <int 0-100>,
        "specificity": <int 0-100>,
        "improvement_suggestions": [<list of 2-3 strings>],
        "missing_information": [<list of 2-3 strings>],
        "better_formatting_tips": [<list of 2-3 strings>]
    }}
    
    Prompt to analyze:
    {prompt}
    """
    try:
        response = model.generate_content(
            analysis_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "overall_score": 0,
            "clarity": 0,
            "structure": 0,
            "context": 0,
            "specificity": 0,
            "improvement_suggestions": [f"Error analyzing prompt: {str(e)}"],
            "missing_information": [],
            "better_formatting_tips": []
        }