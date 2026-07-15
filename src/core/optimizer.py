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

def build_strategy_prompts(user_prompt: str, task_type: str, tone: str) -> str:
    """
    Build a prompt for Gemini to rewrite the user's prompt into three
    distinct strategies: Zero-Shot, Few-Shot, and Chain-of-Thought.
    """
    system_prompt = f"""
You are an expert AI Prompt Engineer.

Your task is to take the user's rough instruction and rewrite it into three different optimized prompt versions.
Do NOT answer the prompt. ONLY output the three rewritten prompts.

The three strategies are:
1. zero_shot: A highly optimized, clear, and direct version of the user's prompt. Provide role, context, and clear instructions.
2. few_shot: Similar to zero-shot, but MUST include 1 or 2 high-quality examples of the expected input and output.
3. chain_of_thought: Instructs the AI to think step-by-step, outlining its reasoning before providing the final answer. Use phrases like "Let's think step by step".

Task Type: {task_type}
Tone: {tone}

Original Prompt:
{user_prompt}

Return ONLY valid JSON in the following format:
{{
    "zero_shot": "...",
    "few_shot": "...",
    "chain_of_thought": "..."
}}

Rules:
- Return ONLY JSON.
- No markdown formatting like ```json
- Ensure the output is completely valid JSON that can be parsed by json.loads().
"""
    return system_prompt.strip()