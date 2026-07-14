def analyze_prompt(prompt: str):

    words = len(prompt.split())

    characters = len(prompt)

    score = min(words * 2, 100)

    return {
        "overall": score,
        "words": words,
        "characters": characters
    }