import streamlit as st
import pandas as pd

from src.core.optimizer import build_optimization_prompt
from src.ai.gemini_client import generate_response, analyze_prompt_quality
from src.core.history import save_prompt, load_history, clear_history, toggle_favorite
from src.utils import load_css

# ======================================================
# PAGE CONFIGURATION
# ======================================================

st.set_page_config(
    page_title="PromptForge AI",
    page_icon="🚀",
    layout="wide"
)

# ======================================================
# STATE MANAGEMENT
# ======================================================
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = ""
if "optimized_result" not in st.session_state:
    st.session_state.optimized_result = ""
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

# ======================================================
# LOAD CSS
# ======================================================

st.markdown(
    load_css("assets/style.css"),
    unsafe_allow_html=True
)

# ======================================================
# HEADER
# ======================================================

st.markdown("""
# 🚀 PromptForge AI

### AI Powered Prompt Optimization Studio

Optimize your prompts using intelligent prompt engineering powered by Google Gemini.
""")

st.divider()

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.header("⚙️ Prompt Settings")

model = st.sidebar.selectbox(
    "AI Model",
    ["Gemini 2.5 Flash"]
)

task_type = st.sidebar.selectbox(
    "Task Type",
    ["General", "Writing", "Coding", "Research", "Education", "Marketing", "Business"]
)

tone = st.sidebar.selectbox(
    "Tone",
    ["Professional", "Friendly", "Technical", "Creative", "Formal", "Casual"]
)

detail_level = st.sidebar.selectbox(
    "Detail Level",
    ["Short", "Medium", "Detailed"]
)

template = st.sidebar.selectbox(
    "📚 Prompt Template",
    ["None", "Blog Writing", "Email Writing", "Python Code", "SQL Query", "Resume", "Research Paper", "Marketing", "LinkedIn Post", "YouTube Script"]
)

# ======================================================
# HISTORY
# ======================================================

st.sidebar.divider()
st.sidebar.subheader("📜 Recent History")

search_query = st.sidebar.text_input("🔍 Search History", placeholder="Search by keyword...")
show_favorites = st.sidebar.toggle("⭐ Show Favorites Only")

history = load_history()

if not history.empty:
    if search_query:
        history = history[history['original_prompt'].str.contains(search_query, case=False, na=False) | 
                          history['task_type'].str.contains(search_query, case=False, na=False)]
    
    if show_favorites and "favorite" in history.columns:
        history = history[history['favorite'] == True]

if history.empty:
    st.sidebar.info("No prompt history found.")
else:
    latest_history = history.tail(10).iloc[::-1]

    for _, row in latest_history.iterrows():
        is_fav = row.get("favorite", False)
        fav_icon = "⭐" if is_fav else "☆"
        
        st.sidebar.caption(row["timestamp"])
        
        col1, col2 = st.sidebar.columns([0.85, 0.15])
        
        with col1:
            snippet = f"{row['original_prompt'][:35]}..." if len(row["original_prompt"]) > 35 else row['original_prompt']
            if st.button(snippet, key=f"hist_{row['timestamp']}", use_container_width=True):
                st.session_state.current_prompt = row['original_prompt']
                st.session_state.optimized_result = row.get('optimized_prompt', '')
                st.session_state.analysis_data = None
                st.rerun()
                
        with col2:
            if st.button(fav_icon, key=f"fav_{row['timestamp']}", help="Toggle Favorite"):
                toggle_favorite(row["timestamp"])
                st.rerun()

        st.sidebar.caption(f"{row['task_type']} • {row['tone']}")
        st.sidebar.divider()

if st.sidebar.button("🗑 Clear History"):
    clear_history()
    st.session_state.current_prompt = ""
    st.session_state.optimized_result = ""
    st.session_state.analysis_data = None
    st.success("History Cleared Successfully!")
    st.rerun()

# ======================================================
# MAIN LAYOUT
# ======================================================

left_col, right_col = st.columns(2)

# ======================================================
# LEFT PANEL
# ======================================================

with left_col:
    with st.container(border=True):
        st.subheader("📝 Original Prompt")

        prompt = st.text_area(
            "Enter your prompt",
            key="current_prompt",
            placeholder="Example: Write a professional LinkedIn post about Artificial Intelligence...",
            height=300
        )

        optimize = st.button("✨ Optimize Prompt", use_container_width=True)

# ======================================================
# OPTIMIZATION LOGIC
# ======================================================

if optimize:
    if not st.session_state.current_prompt.strip():
        st.warning("⚠️ Please enter a prompt.")
    else:
        with st.spinner("🤖 Optimizing and analyzing your prompt..."):
            optimized_instruction = build_optimization_prompt(
                user_prompt=st.session_state.current_prompt,
                task_type=task_type,
                tone=tone,
                detail_level=detail_level,
                template=template
            )

            response = generate_response(optimized_instruction)
            st.session_state.optimized_result = response
            
            analysis = analyze_prompt_quality(st.session_state.current_prompt)
            st.session_state.analysis_data = analysis

            save_prompt(
                original=st.session_state.current_prompt,
                optimized=response,
                task=task_type,
                tone=tone,
                detail=detail_level
            )
            
            st.rerun()

# ======================================================
# RIGHT PANEL
# ======================================================

with right_col:
    if st.session_state.optimized_result:
        tabs = st.tabs(["🚀 Optimized Prompt", "📊 Quality Analysis"])
        
        with tabs[0]:
            with st.container(border=True):
                st.subheader("Optimized Result")
                
                # Using st.code provides an automatic "Copy to clipboard" button
                st.code(st.session_state.optimized_result, language="markdown")

                st.download_button(
                    label="📥 Download Prompt",
                    data=st.session_state.optimized_result,
                    file_name="optimized_prompt.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                st.divider()
                st.subheader("📊 Prompt Statistics")
                metric1, metric2, metric3 = st.columns(3)
                metric1.metric("Words", len(st.session_state.optimized_result.split()))
                metric2.metric("Characters", len(st.session_state.optimized_result))
                metric3.metric("Lines", len(st.session_state.optimized_result.splitlines()))

        with tabs[1]:
            if st.session_state.analysis_data:
                data = st.session_state.analysis_data
                with st.container(border=True):
                    st.subheader("Overall Score")
                    
                    score = data.get("overall_score", 0)
                    if isinstance(score, (int, float)):
                        st.progress(score / 100, text=f"{score}/100")
                    
                    st.subheader("Metrics")
                    m1, m2 = st.columns(2)
                    
                    def safe_progress(val):
                        if isinstance(val, (int, float)):
                            return val / 100.0
                        return 0.0
                        
                    with m1:
                        st.caption("Clarity")
                        st.progress(safe_progress(data.get("clarity")), text=f"{data.get('clarity', 0)}/100")
                        st.caption("Structure")
                        st.progress(safe_progress(data.get("structure")), text=f"{data.get('structure', 0)}/100")
                    with m2:
                        st.caption("Context")
                        st.progress(safe_progress(data.get("context")), text=f"{data.get('context', 0)}/100")
                        st.caption("Specificity")
                        st.progress(safe_progress(data.get("specificity")), text=f"{data.get('specificity', 0)}/100")
                    
                    st.divider()
                    
                    st.subheader("💡 AI Suggestions")
                    
                    with st.expander("Improvement Suggestions", expanded=True):
                        for tip in data.get("improvement_suggestions", []):
                            st.markdown(f"- {tip}")
                            
                    with st.expander("Missing Information"):
                        for info in data.get("missing_information", []):
                            st.markdown(f"- {info}")
                            
                    with st.expander("Better Formatting Tips"):
                        for fmt in data.get("better_formatting_tips", []):
                            st.markdown(f"- {fmt}")
            else:
                st.info("Optimize the prompt to see its quality analysis.")
    else:
        with st.container(border=True):
            st.info("Enter a prompt on the left and click **✨ Optimize Prompt** to see the magic!")

# ======================================================
# FOOTER
# ======================================================

st.divider()

st.caption(
    "🚀 PromptForge AI • Powered by Google Gemini • Built with Streamlit"
)