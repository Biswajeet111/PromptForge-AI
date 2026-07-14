import streamlit as st

from src.optimizer import build_optimization_prompt
from src.gemini_client import generate_response
from src.history import save_prompt, load_history, clear_history


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="PromptForge AI",
    page_icon="🚀",
    layout="wide"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🚀 PromptForge AI")
st.caption("Transform simple prompts into powerful AI prompts.")

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("⚙️ Prompt Settings")

model = st.sidebar.selectbox(
    "AI Model",
    [
        "Gemini 2.5 Flash"
    ]
)

task_type = st.sidebar.selectbox(
    "Task Type",
    [
        "General",
        "Writing",
        "Coding",
        "Research",
        "Education",
        "Marketing",
        "Business"
    ]
)

tone = st.sidebar.selectbox(
    "Tone",
    [
        "Professional",
        "Friendly",
        "Technical",
        "Creative",
        "Formal",
        "Casual"
    ]
)

detail_level = st.sidebar.selectbox(
    "Detail Level",
    [
        "Short",
        "Medium",
        "Detailed"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("📜 Prompt History")

history = load_history()

if history.empty:
    st.sidebar.info("No prompt history available.")
else:

    latest_history = history.tail(5).iloc[::-1]

    for _, row in latest_history.iterrows():

        st.sidebar.caption(row["timestamp"])

        st.sidebar.write(
            row["original_prompt"][:40] + "..."
            if len(row["original_prompt"]) > 40
            else row["original_prompt"]
        )

        st.sidebar.divider()

if st.sidebar.button("🗑 Clear History"):

    clear_history()

    st.sidebar.success("History Cleared!")

    st.rerun()

# --------------------------------------------------
# MAIN INPUT
# --------------------------------------------------

prompt = st.text_area(
    "Enter your prompt",
    placeholder="Example: Write a professional blog on Artificial Intelligence...",
    height=220
)

optimize = st.button(
    "✨ Optimize Prompt",
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------

st.subheader("Optimized Prompt")

output_placeholder = st.empty()

# --------------------------------------------------
# BUTTON ACTION
# --------------------------------------------------

if optimize:

    if not prompt.strip():

        st.warning("⚠ Please enter a prompt.")

    else:

        with st.spinner("Optimizing your prompt..."):

            optimized_instruction = build_optimization_prompt(
                user_prompt=prompt,
                task_type=task_type,
                tone=tone,
                detail_level=detail_level
            )

            response = generate_response(
                optimized_instruction
            )

            save_prompt(
                original=prompt,
                optimized=response,
                task=task_type,
                tone=tone,
                detail=detail_level
            )

        output_placeholder.text_area(
            "Optimized Prompt",
            value=response,
            height=300
        )

        st.success("✅ Prompt optimized successfully!")