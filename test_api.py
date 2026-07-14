from src.gemini_client import generate_response

prompt = "Explain Artificial Intelligence in one paragraph."

response = generate_response(prompt)

print(response)