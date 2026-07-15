import streamlit as st
import pandas as pd

from src.core.optimizer import build_optimization_prompt, build_strategy_prompts
from src.ai.gemini_client import generate_response, analyze_prompt_quality, score_ai_output
from src.core.history import save_prompt, load_history, clear_history, toggle_favorite
from src.core.exporter import generate_pdf, generate_docx
from src.utils import load_css
import difflib
import json

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

def extract_prompt(raw_text: str) -> str:
    """Helper to extract optimized prompt from JSON string."""
    try:
        # Check if it looks like JSON
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        if start != -1 and end != 0:
            clean_json = raw_text[start:end]
            parsed = json.loads(clean_json)
            return parsed.get("optimized_prompt", raw_text)
    except Exception:
        pass
    return raw_text


if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = ""
if "optimized_result" not in st.session_state:
    st.session_state.optimized_result = ""
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "strategies_data" not in st.session_state:
    st.session_state.strategies_data = None

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

col1, col2 = st.columns([1, 6])
with col1:
    try:
        st.image("assets/logo.png", use_container_width=True)
    except:
        st.write("🚀")
        
with col2:
    st.markdown("""
    # PromptForge AI
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
                raw_opt = row.get('optimized_prompt', '')
                st.session_state.optimized_result = extract_prompt(raw_opt)
                st.session_state.analysis_data = None
                st.session_state.strategies_data = None
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
    st.session_state.strategies_data = None
    st.success("History Cleared Successfully!")
    st.rerun()

# ======================================================
# MAIN LAYOUT
# ======================================================

with st.container(border=True):
    st.subheader("📝 Original Prompt")

    prompt = st.text_area(
        "Enter your rough instruction",
        key="current_prompt",
        placeholder="Example: Write a short summary of how photosynthesis works...",
        height=150
    )

    col1, col2 = st.columns(2)
    with col1:
        compare_strategies = st.button("⚖️ Compare Strategies (Zero-Shot, Few-Shot, CoT)", use_container_width=True, type="primary")
    with col2:
        optimize = st.button("✨ Optimize Only (Single)", use_container_width=True)

# ======================================================
# STRATEGY COMPARISON LOGIC
# ======================================================

if compare_strategies:
    if not st.session_state.current_prompt.strip():
        st.warning("⚠️ Please enter a prompt.")
    else:
        with st.spinner("🤖 Generating strategies and evaluating outputs... This may take a moment."):
            # 1. Generate Strategy Prompts
            strategy_instruction = build_strategy_prompts(
                user_prompt=st.session_state.current_prompt,
                task_type=task_type,
                tone=tone
            )
            strategies_json_str = generate_response(strategy_instruction)
            
            try:
                start = strategies_json_str.find('{')
                end = strategies_json_str.rfind('}') + 1
                strategies_dict = json.loads(strategies_json_str[start:end])
                
                prompts = {
                    "Zero-Shot": strategies_dict.get("zero_shot", ""),
                    "Few-Shot": strategies_dict.get("few_shot", ""),
                    "Chain-of-Thought": strategies_dict.get("chain_of_thought", "")
                }
                
                results = {}
                
                # 2. Run outputs and score
                for strategy_name, strategy_prompt in prompts.items():
                    if strategy_prompt:
                        output = generate_response(strategy_prompt)
                        score = score_ai_output(strategy_prompt, output)
                        
                        results[strategy_name] = {
                            "prompt": strategy_prompt,
                            "output": output,
                            "score": score
                        }
                        
                st.session_state.strategies_data = results
                st.session_state.optimized_result = "" # Clear single run
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating strategies: {str(e)}")

# ======================================================
# OPTIMIZATION LOGIC (Single)
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
            
            final_optimized_prompt = extract_prompt(response)

            st.session_state.optimized_result = final_optimized_prompt
            st.session_state.strategies_data = None # Clear strategies
            
            analysis = analyze_prompt_quality(st.session_state.current_prompt)
            st.session_state.analysis_data = analysis

            save_prompt(
                original=st.session_state.current_prompt,
                optimized=final_optimized_prompt,
                task=task_type,
                tone=tone,
                detail=detail_level
            )
            
            st.rerun()

# ======================================================
# RESULTS UI
# ======================================================

if st.session_state.strategies_data:
    st.divider()
    st.subheader("⚖️ Strategy Comparison Results")
    
    s_col1, s_col2, s_col3 = st.columns(3)
    
    strategies = list(st.session_state.strategies_data.items())
    columns = [s_col1, s_col2, s_col3]
    
    for i, (name, data) in enumerate(strategies):
        if i < 3:
            with columns[i]:
                with st.container(border=True):
                    st.markdown(f"### {name}")
                    
                    # Scores
                    score = data["score"]
                    c_val = score.get('clarity', 0)
                    r_val = score.get('relevance', 0)
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Clarity", f"{c_val}/100")
                    m2.metric("Relevance", f"{r_val}/100")
                    
                    st.progress(c_val / 100, text="Clarity")
                    st.progress(r_val / 100, text="Relevance")
                    
                    with st.expander("📝 View Generated Prompt"):
                        st.info(data["prompt"])
                        
                    st.markdown("#### AI Output")
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); white-space: pre-wrap; font-size: 15px; line-height: 1.5; height: 400px; overflow-y: auto;">
{data['output']}
                    </div>
                    """, unsafe_allow_html=True)
                    
elif st.session_state.optimized_result:
    st.divider()
    tabs = st.tabs(["🚀 Optimized Prompt", "📊 Quality Analysis", "💡 Suggestions", "⚖️ Comparison"])
    
    with tabs[0]:
        with st.container(border=True):
            st.subheader("Optimized Result")
            
            escaped_text = st.session_state.optimized_result.replace('`', '\\`').replace('\\', '\\\\')
            
            custom_html = f"""
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); white-space: pre-wrap; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
{st.session_state.optimized_result}
            </div>
            <button onclick="navigator.clipboard.writeText(`{escaped_text}`); this.innerText='✅ Copied!';" style="background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%); border: none; color: white; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 14px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);">
                📋 Copy to Clipboard
            </button>
            """
            st.markdown(custom_html, unsafe_allow_html=True)

            dl_col1, dl_col2, dl_col3 = st.columns(3)
            with dl_col1:
                st.download_button(
                    label="📄 TXT",
                    data=st.session_state.optimized_result,
                    file_name="optimized_prompt.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with dl_col2:
                st.download_button(
                    label="📄 PDF",
                    data=generate_pdf(st.session_state.optimized_result),
                    file_name="optimized_prompt.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with dl_col3:
                st.download_button(
                    label="📄 DOCX",
                    data=generate_docx(st.session_state.optimized_result),
                    file_name="optimized_prompt.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
                
        else:
            st.info("Optimize the prompt to see its quality analysis.")
            
    with tabs[2]:
        if st.session_state.analysis_data:
            data = st.session_state.analysis_data
            with st.container(border=True):
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
            st.info("Optimize the prompt to see AI suggestions.")
            
    with tabs[3]:
        with st.container(border=True):
            st.subheader("Prompt Comparison")
            st.caption("Green highlights show what Gemini added. Red shows what was removed.")
            
            original_lines = st.session_state.current_prompt.splitlines()
            optimized_lines = st.session_state.optimized_result.splitlines()
            
            diff = difflib.HtmlDiff().make_table(original_lines, optimized_lines, "Original", "Optimized")
            
            # Make the diff table fit the dark theme better and wrap text properly
            diff = diff.replace('nowrap="nowrap"', '')
            
            diff_style = """
            <style>
                table.diff {
                    width: 100%;
                    border-collapse: collapse;
                    color: #e2e8f0;
                    font-family: 'Outfit', sans-serif;
                }
                table.diff th, table.diff td {
                    padding: 10px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    word-break: break-word;
                }
                table.diff td.diff_add {
                    background-color: rgba(34, 197, 94, 0.3);
                    color: #ffffff;
                }
                table.diff td.diff_sub {
                    background-color: rgba(239, 68, 68, 0.3);
                    color: #ffffff;
                }
                table.diff td.diff_chg {
                    background-color: rgba(234, 179, 8, 0.3);
                    color: #ffffff;
                }
                table.diff th {
                    background-color: rgba(255, 255, 255, 0.05);
                    text-align: center;
                }
                .diff_next { display: none; }
            </style>
            """
            
            html_str = f"<div style='background-color: transparent;'>{diff_style}{diff}</div>"
            st.components.v1.html(html_str, height=500, scrolling=True)
else:
    with st.container(border=True):
        st.info("Enter a prompt above and click **⚖️ Compare Strategies** or **✨ Optimize Only** to see the magic!")

# ======================================================
# FOOTER
# ======================================================

st.divider()

st.caption(
    "🚀 PromptForge AI • Powered by Google Gemini • Built with Streamlit"
)