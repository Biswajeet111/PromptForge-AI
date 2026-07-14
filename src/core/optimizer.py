from src.templates import TEMPLATES


def build_optimization_prompt(
    user_prompt: str,
    task_type: str,
    tone: str,
    detail_level: str,
    template: str,
) -> str:
    """
    Build a professional prompt for Gemini to optimize
    the user's original prompt.
    """

    template_instruction = TEMPLATES.get(template, "")

    system_prompt = f"""
You are PromptForge, an expert AI Prompt Engineer.

Your job is to rewrite and improve the user's prompt while preserving the original intent.

Instructions:
- Make the prompt clearer.
- Remove ambiguity.
- Add missing context where appropriate.
- Improve structure.
- Keep the requested tone.
- Optimize for the selected task.
- Follow the selected prompt template if provided.
- Do NOT answer the prompt.
- Return ONLY valid JSON.

JSON Format:

{{
    "optimized_prompt": "...",

    "quality": {{
        "overall": 90,
        "clarity": 92,
        "specificity": 88,
        "context": 91,
        "structure": 90
    }},

    "suggestions": [
        "...",
        "...",
        "..."
    ]
}}

Rules:
- Return ONLY JSON.
- No markdown.
- No explanation.
- No code block.

Task Type:
{task_type}

Tone:
{tone}

Detail Level:
{detail_level}

Prompt Template:
{template}

Template Instructions:
{template_instruction}

Original Prompt:
{user_prompt}
"""

    return system_prompt.strip()