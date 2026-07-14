import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="PromptForge AI",
    page_icon="🚀",
    layout="wide"
)

# Title
st.title("🚀 PromptForge AI")
st.caption("Transform simple prompts into powerful AI prompts.")

st.divider()

# Sidebar
st.sidebar.header("⚙️ Prompt Settings")

model = st.sidebar.selectbox(
    "Select AI Model",
    ["Gemini"]
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

length = st.sidebar.slider(
    "Prompt Detail Level",
    1,
    5,
    3
)

# Main Input
prompt = st.text_area(
    "Enter your prompt",
    height=220,
    placeholder="Example: Write a blog on Artificial Intelligence..."
)

optimize = st.button(
    "✨ Optimize Prompt",
    use_container_width=True
)

st.divider()

st.subheader("Optimized Prompt")

output_box = st.empty()