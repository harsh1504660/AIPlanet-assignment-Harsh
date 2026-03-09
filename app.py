"""
Math Mentor - Multimodal JEE Math Problem Solver
Main Streamlit Application
"""

import streamlit as st
import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
# Load environment
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Page config must be first Streamlit call
st.set_page_config(
    page_title="Math Mentor",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root variables */
:root {
    --ink: #0f0e17;
    --paper: #fffcf2;
    --accent: #e53170;
    --accent2: #ff6b35;
    --gold: #f5a623;
    --muted: #6e6d7a;
    --surface: #f4f2eb;
    --border: #e0ddd4;
    --success: #22c55e;
    --warning: #f59e0b;
    --error: #ef4444;
    --code-bg: #1a1a2e;
}

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

.main { background: var(--paper); }
.block-container { padding: 2rem 2rem 4rem; max-width: 1400px; }

/* Header */
.mentor-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 2rem 0 1.5rem;
    border-bottom: 2px solid var(--ink);
    margin-bottom: 2rem;
}

.mentor-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -1px;
    line-height: 1;
}

.mentor-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    color: var(--muted);
    margin-top: 0.3rem;
    font-weight: 400;
}

.accent-dot {
    display: inline-block;
    width: 14px;
    height: 14px;
    background: var(--accent);
    border-radius: 50%;
    margin-left: 4px;
    vertical-align: middle;
}

/* Panels */
.panel {
    background: white;
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.panel-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Agent Trace */
.trace-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    font-size: 0.88rem;
    border: 1px solid transparent;
}

.trace-running { background: #fef3c7; border-color: #fbbf24; }
.trace-complete { background: #f0fdf4; border-color: #86efac; }
.trace-hitl_triggered { background: #fff7ed; border-color: #fed7aa; }
.trace-error { background: #fef2f2; border-color: #fca5a5; }
.trace-passed { background: #f0fdf4; border-color: #86efac; }
.trace-rejected { background: #fef2f2; border-color: #fca5a5; }
.trace-found { background: #eff6ff; border-color: #bfdbfe; }
.trace-none { background: #f9fafb; border-color: #e5e7eb; }
.trace-warning { background: #fff7ed; border-color: #fed7aa; }
.trace-stored { background: #f0fdf4; border-color: #86efac; }
.trace-searching { background: #eff6ff; border-color: #bfdbfe; }

.trace-agent { font-weight: 600; color: var(--ink); min-width: 160px; }
.trace-details { color: var(--muted); font-size: 0.82rem; flex: 1; }

/* Status icon */
.status-icon { font-size: 1rem; min-width: 20px; text-align: center; }

/* Source chips */
.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.82rem;
    margin: 0.2rem;
    color: var(--ink);
}

.source-score {
    background: var(--accent);
    color: white;
    border-radius: 10px;
    padding: 0.1rem 0.4rem;
    font-size: 0.72rem;
    font-weight: 600;
}

/* Confidence bar */
.conf-container {
    background: var(--surface);
    border-radius: 8px;
    height: 8px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.conf-bar {
    height: 100%;
    border-radius: 8px;
    transition: width 0.5s ease;
}

.conf-high { background: var(--success); }
.conf-mid { background: var(--warning); }
.conf-low { background: var(--error); }

/* Answer display */
.answer-box {
    background: var(--ink);
    color: white;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin: 1rem 0;
    font-family: 'Space Mono', monospace;
}

.answer-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 0.5rem;
}

.answer-text {
    font-size: 1.4rem;
    font-weight: 700;
    color: white;
}

/* HITL Banner */
.hitl-banner {
    background: linear-gradient(135deg, #fff7ed, #fef3c7);
    border: 2px solid var(--warning);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

.hitl-icon { font-size: 1.8rem; }
.hitl-title { font-weight: 700; color: #92400e; margin-bottom: 0.3rem; }
.hitl-reason { color: #78350f; font-size: 0.9rem; }

/* Memory card */
.memory-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    transition: all 0.15s;
}

.memory-card:hover { border-color: var(--accent); background: white; }

/* Feedback buttons */
.fb-correct {
    background: #22c55e !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
}

.fb-incorrect {
    background: #ef4444 !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
}

/* OCR Preview */
.ocr-preview {
    background: #1a1a2e;
    border-radius: 10px;
    padding: 1.2rem;
    margin: 0.75rem 0;
}

.ocr-text {
    color: #a6e3a1;
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    white-space: pre-wrap;
}

/* Confidence badge */
.conf-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
}

.conf-badge-high { background: #dcfce7; color: #166534; }
.conf-badge-mid { background: #fef3c7; color: #92400e; }
.conf-badge-low { background: #fee2e2; color: #991b1b; }

/* Topic badge */
.topic-badge {
    display: inline-block;
    background: var(--accent);
    color: white;
    border-radius: 6px;
    padding: 0.2rem 0.7rem;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
}

[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { 
    color: white !important; 
    font-family: 'Space Mono', monospace !important;
}

/* Input mode tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* Divider */
.section-divider {
    border: none;
    border-top: 1.5px solid var(--border);
    margin: 1.5rem 0;
}

/* Scrollable explanation */
.explanation-box {
    max-height: 60vh;
    overflow-y: auto;
    padding: 0.5rem;
}

/* Stats */
.stat-card {
    background: white;
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}

.stat-number {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--ink);
}

.stat-label {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.3rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Initialize Components ───────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def init_components():
    """Initialize RAG pipeline and memory store."""
    from rag.pipeline import MathRAGPipeline
    from memory.store import MathMemory
    
    base_dir = Path(__file__).parent
    
    rag = MathRAGPipeline(
        knowledge_base_path=str(base_dir / "knowledge_base"),
        vector_store_path=str(base_dir / "rag" / "vector_store"),
        top_k=5
    )
    rag.build_index()
    
    memory = MathMemory(
        db_path=str(base_dir / "memory" / "math_memory.json")
    )
    memory.increment_session()
    
    return rag, memory


@st.cache_resource(show_spinner=False)
def init_orchestrator(_rag, _memory,_api_key):
    """Initialize the orchestrator with agents."""
    from agents.orchestrator import MathMentorOrchestrator
    return MathMentorOrchestrator(_rag, _memory,_api_key)


# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_trace_icon(status: str) -> str:
    icons = {
        "running": "⚡",
        "complete": "✅",
        "hitl_triggered": "⚠️",
        "error": "❌",
        "passed": "✅",
        "rejected": "🚫",
        "found": "🔍",
        "none": "○",
        "warning": "⚠️",
        "stored": "💾",
        "searching": "🔍",
    }
    return icons.get(status, "•")


def render_confidence(conf: float) -> str:
    """Render confidence as HTML."""
    pct = int(conf * 100)
    cls = "conf-high" if conf >= 0.75 else ("conf-mid" if conf >= 0.5 else "conf-low")
    badge_cls = "conf-badge-high" if conf >= 0.75 else ("conf-badge-mid" if conf >= 0.5 else "conf-badge-low")
    label = "High" if conf >= 0.75 else ("Medium" if conf >= 0.5 else "Low")
    emoji = "🟢" if conf >= 0.75 else ("🟡" if conf >= 0.5 else "🔴")
    
    return f"""
<span class="conf-badge {badge_cls}">{emoji} {label} Confidence — {pct}%</span>
<div class="conf-container">
    <div class="conf-bar {cls}" style="width:{pct}%"></div>
</div>"""


def render_agent_trace(trace: list):
    """Render agent execution trace."""
    for item in trace:
        status = item.get("status", "")
        css_class = f"trace-{status}"
        icon = get_trace_icon(status)
        
        st.markdown(f"""
<div class="trace-item {css_class}">
    <span class="status-icon">{icon}</span>
    <span class="trace-agent">{item.get('agent', '')}</span>
    <span class="trace-details">{item.get('details', '')}</span>
</div>""", unsafe_allow_html=True)


def render_sources(sources: list):
    """Render RAG sources as chips."""
    if not sources:
        st.caption("No sources retrieved")
        return
    
    chips_html = ""
    for src in sources:
        score_pct = int(src.get("score", 0) * 100)
        chips_html += f'<span class="source-chip">📖 {src["source"]} <span class="source-score">{score_pct}%</span></span>'
    
    st.markdown(chips_html, unsafe_allow_html=True)
    
    with st.expander("View retrieved context"):
        for i, src in enumerate(sources, 1):
            st.markdown(f"**{i}. {src['source']}** (score: {src.get('score', 0):.3f})")
            st.text(src.get("preview", ""))
            st.markdown("---")


# ─── Main App ─────────────────────────────────────────────────────────────────

def main():
    # If API key not yet provided

    if "GEMINI_API_KEY" not in st.session_state:

        st.title("🔑 Enter Gemini API Key")

        api_key = st.text_input(
            "Paste your Gemini API key",
            type="password",
            placeholder="AIza..."
        )

        if st.button("Continue"):

            if api_key.strip() == "":
                st.error("Please enter a valid API key.")
                return

            try:
                # Configure Gemini with user key
                genai.configure(api_key=api_key)

                # Small test request
                model = genai.GenerativeModel("models/gemini-flash-latest")

                response = model.generate_content("Hello")

                # If success → store key
                st.session_state["GEMINI_API_KEY"] = api_key
                os.environ["GEMINI_API_KEY"] = api_key

                st.success("✅ API Key validated successfully!")
                st.rerun()

            except Exception as e:

                error_msg = str(e)

                if "quota" in error_msg.lower():
                    st.error("❌ API key is valid but quota is exceeded.")
                elif "permission" in error_msg.lower():
                    st.error("❌ API key does not have access to Gemini API.")
                elif "invalid" in error_msg.lower():
                    st.error("❌ Invalid API key.")
                else:
                    st.error(f"❌ API validation failed: {error_msg}")

        st.info("You can get your API key from: https://aistudio.google.com/app/apikey")

        return

    # Header
    st.markdown("""
<div class="mentor-header">
    <div>
        <div class="mentor-title">Math Mentor<span class="accent-dot"></span></div>
        <div class="mentor-subtitle">JEE Problem Solver · RAG + Multi-Agent · Multimodal</div>
    </div>
</div>""", unsafe_allow_html=True)

    # Initialize components
    with st.spinner("Initializing agents and knowledge base..."):
        try:
            rag, memory = init_components()
            api_key = st.session_state["GEMINI_API_KEY"]
            orchestrator = init_orchestrator(rag, memory, api_key)
        except Exception as e:
            st.error(f"Initialization error: {e}")
            st.info("Please check your API key and dependencies.")
            return

    # ─── SIDEBAR ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🧮 Math Mentor")
        st.markdown("---")
        
        # Stats
        stats = memory.get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Problems Solved", stats["total_problems"])
            st.metric("Accuracy", f"{stats['accuracy']:.0%}" if stats['with_feedback'] > 0 else "N/A")
        with col2:
            st.metric("Sessions", stats["sessions"])
            st.metric("Corrections", stats["correction_rules"])
        
        st.markdown("---")
        
        # Topic stats
        st.markdown("### 📊 Topics")
        topic_stats = memory.get_topic_stats()
        if topic_stats:
            for topic, ts in topic_stats.items():
                solved = ts.get("solved", 0)
                correct = ts.get("correct", 0)
                acc = f"{correct/max(solved,1):.0%}" if solved > 0 else "N/A"
                st.markdown(f"**{topic.title()}**: {solved} solved, {acc} accuracy")
        else:
            st.caption("No problems solved yet")
        
        st.markdown("---")
        
        # Memory browser
        st.markdown("### 💾 Memory")
        all_problems = memory.get_all_problems()
        if all_problems:
            st.caption(f"{len(all_problems)} problems in memory")
            selected_mem = st.selectbox(
                "View solved problem",
                options=range(min(10, len(all_problems))),
                format_func=lambda i: f"{all_problems[-(i+1)].get('topic', 'unknown').title()}: {all_problems[-(i+1)].get('parsed_problem', {}).get('problem_text', '')[:40]}...",
                key="mem_selector"
            )
            if st.button("View Problem", key="view_mem"):
                prob = all_problems[-(selected_mem+1)]
                st.session_state["memory_view"] = prob
        else:
            st.caption("Memory is empty")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        st.toggle("Show full solution steps", value=True, key="show_full_solution")
        st.toggle("Auto-show agent trace", value=True, key="auto_show_trace")

    # ─── MEMORY VIEW MODAL ────────────────────────────────────────────────────
    if st.session_state.get("memory_view"):
        prob = st.session_state["memory_view"]
        with st.expander("📖 Memory: Viewed Problem", expanded=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Problem:** {prob.get('parsed_problem', {}).get('problem_text', '')}")
                st.markdown(f"**Answer:** {prob.get('solution', '')[:300]}...")
            with col2:
                st.markdown(f"**Topic:** {prob.get('topic', 'N/A')}")
                st.markdown(f"**Feedback:** {prob.get('user_feedback', 'None')}")
                st.markdown(f"**Saved:** {prob.get('timestamp', '')[:10]}")
            if st.button("Close", key="close_mem_view"):
                del st.session_state["memory_view"]

    # ─── MAIN INPUT AREA ─────────────────────────────────────────────────────
    st.markdown("### 📥 Input Your Problem")
    
    tab_text, tab_image, tab_audio = st.tabs(["💬 Text", "🖼️ Image", "🎤 Audio"])
    
    # Initialize session state
    if "current_result" not in st.session_state:
        st.session_state.current_result = None
    if "ocr_text" not in st.session_state:
        st.session_state.ocr_text = ""
    if "ocr_confidence" not in st.session_state:
        st.session_state.ocr_confidence = 1.0
    if "asr_text" not in st.session_state:
        st.session_state.asr_text = ""
    if "input_ready" not in st.session_state:
        st.session_state.input_ready = False
    if "final_text" not in st.session_state:
        st.session_state.final_text = ""
    if "input_type" not in st.session_state:
        st.session_state.input_type = "text"

    # ─── TEXT TAB ─────────────────────────────────────────────────────────────
    with tab_text:
        st.markdown("""
<div style="padding: 0.5rem 0; color: #6e6d7a; font-size: 0.9rem;">
Type your JEE math problem below. You can use standard notation like x^2, sqrt(), etc.
</div>""", unsafe_allow_html=True)
        
        text_input = st.text_area(
            "Problem",
            placeholder="Example: Find the probability that when 3 dice are rolled, the sum is at least 15.\n\nOr: Solve: x² - 5x + 6 = 0 and find the sum of squares of roots.\n\nOr: If f(x) = x³ - 3x² + 4, find the local maxima and minima.",
            height=140,
            label_visibility="collapsed",
            key="text_problem"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🚀 Solve Problem", type="primary", key="solve_text", use_container_width=True):
                if text_input.strip():
                    st.session_state.final_text = text_input.strip()
                    st.session_state.input_type = "text"
                    st.session_state.ocr_confidence = 1.0
                    st.session_state.input_ready = True
                else:
                    st.warning("Please enter a problem first.")
        with col2:
            # Example problems
            examples = [
                "Solve: 2x² - 7x + 3 = 0",
                "Find P(sum=7) when two dice are rolled",
                "Find dy/dx if y = x²·sin(x)",
                "Find det of [[1,2],[3,4]]",
                "Find lim(x→0) sin(3x)/x",
                "Expand (2x + y)⁴ using binomial theorem",
            ]
            selected_ex = st.selectbox("Or try an example:", [""] + examples, key="example_sel")
            if selected_ex and st.button("Use Example", key="use_example"):
                st.session_state.final_text = selected_ex
                st.session_state.input_type = "text"
                st.session_state.ocr_confidence = 1.0
                st.session_state.input_ready = True
                st.rerun()

    # ─── IMAGE TAB ────────────────────────────────────────────────────────────
    with tab_image:
        st.markdown("""
<div style="padding: 0.5rem 0; color: #6e6d7a; font-size: 0.9rem;">
Upload a photo or screenshot of a math problem. The system will extract text using Claude Vision (OCR).
</div>""", unsafe_allow_html=True)
        
        uploaded_image = st.file_uploader(
            "Upload image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key="img_uploader"
        )
        
        if uploaded_image:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(uploaded_image, caption="Uploaded image", use_container_width=True)
            
            with col2:
                if st.button("🔍 Extract Text (OCR)", key="run_ocr"):
                    with st.spinner("Extracting math from image..."):
                        from utils.multimodal import process_image_ocr, preprocess_math_ocr
                        
                        img_bytes = uploaded_image.read()
                        mime = f"image/{uploaded_image.type.split('/')[-1]}" if '/' in (uploaded_image.type or '') else "image/png"
                        
                        ocr_result = process_image_ocr(img_bytes, mime)
                        cleaned = preprocess_math_ocr(ocr_result["text"])
                        
                        st.session_state.ocr_text = cleaned
                        st.session_state.ocr_confidence = ocr_result["confidence"]
                
                if st.session_state.ocr_text:
                    conf = st.session_state.ocr_confidence
                    badge_cls = "conf-badge-high" if conf >= 0.75 else ("conf-badge-mid" if conf >= 0.5 else "conf-badge-low")
                    label = "High" if conf >= 0.75 else ("Medium" if conf >= 0.5 else "Low")
                    
                    st.markdown(f'<span class="conf-badge {badge_cls}">OCR Confidence: {label} ({conf:.0%})</span>', 
                               unsafe_allow_html=True)
                    
                    if conf < 0.6:
                        st.warning("⚠️ Low OCR confidence — please review and correct the extracted text.")
                    
                    st.markdown("**Extracted Text (editable):**")
                    edited_ocr = st.text_area(
                        "Edit extracted text",
                        value=st.session_state.ocr_text,
                        height=100,
                        label_visibility="collapsed",
                        key="ocr_edit"
                    )
                    
                    if st.button("🚀 Solve This Problem", type="primary", key="solve_ocr"):
                        st.session_state.final_text = edited_ocr
                        st.session_state.input_type = "image"
                        st.session_state.input_ready = True

    # ─── AUDIO TAB ────────────────────────────────────────────────────────────
    with tab_audio:
        st.markdown("""
<div style="padding: 0.5rem 0; color: #6e6d7a; font-size: 0.9rem;">
Upload an audio recording of your math question. Supports MP3, WAV, M4A formats.
</div>""", unsafe_allow_html=True)
        
        uploaded_audio = st.file_uploader(
            "Upload audio",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            label_visibility="collapsed",
            key="audio_uploader"
        )
        
        if uploaded_audio:
            st.audio(uploaded_audio)
            
            if st.button("🎙️ Transcribe Audio", key="run_asr"):
                with st.spinner("Transcribing audio..."):
                    from utils.multimodal import process_audio_asr, preprocess_math_speech
                    
                    audio_bytes = uploaded_audio.getvalue()
                    fmt = uploaded_audio.name.split('.')[-1].lower()
                    
                    asr_result = process_audio_asr(audio_bytes, fmt)
                    
                    cleaned = preprocess_math_speech(asr_result["text"])
                    
                    st.session_state.asr_text = cleaned
                    st.session_state.ocr_confidence = asr_result["confidence"]
        
        if st.session_state.asr_text:
            conf = st.session_state.ocr_confidence
            badge_cls = "conf-badge-high" if conf >= 0.75 else ("conf-badge-mid" if conf >= 0.5 else "conf-badge-low")
            label = "High" if conf >= 0.75 else ("Medium" if conf >= 0.5 else "Low")
            
            st.markdown(f'<span class="conf-badge {badge_cls}">ASR Confidence: {label} ({conf:.0%})</span>', 
                       unsafe_allow_html=True)
            
            st.markdown("**Transcript (editable):**")
            edited_asr = st.text_area(
                "Edit transcript",
                value=st.session_state.asr_text,
                height=100,
                label_visibility="collapsed",
                key="asr_edit"
            )
            
            if st.button("🚀 Solve This Problem", type="primary", key="solve_asr"):
                st.session_state.final_text = edited_asr
                st.session_state.input_type = "audio"
                st.session_state.input_ready = True

    # ─── PROCESSING ──────────────────────────────────────────────────────────
    if st.session_state.get("input_ready") and st.session_state.get("final_text"):
        st.session_state.input_ready = False  # Reset flag
        
        final_text = st.session_state.final_text
        input_type = st.session_state.input_type
        ocr_conf = st.session_state.ocr_confidence
        
        st.markdown("---")
        st.markdown("### ⚙️ Processing")
        
        # Live agent trace during processing
        trace_container = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("Running multi-agent pipeline..."):
            # Show problem being processed
            with trace_container.container():
                st.markdown(f'<span class="topic-badge">{input_type}</span> Processing: *{final_text[:100]}...*' if len(final_text) > 100 else f'<span class="topic-badge">{input_type}</span> Processing: *{final_text}*', unsafe_allow_html=True)
            
            progress_bar.progress(10)
            status_text.text("🔍 Running agents...")
            
            result = orchestrator.process(final_text, input_type, ocr_conf)
            
            progress_bar.progress(100)
            status_text.empty()
        
        progress_bar.empty()
        trace_container.empty()
        
        st.session_state.current_result = result

    # ─── RESULTS ─────────────────────────────────────────────────────────────
    if st.session_state.current_result:
        result = st.session_state.current_result
        
        st.markdown("---")
        
        if result.get("error") and not result.get("success"):
            st.error(f"❌ Error: {result['error']}")
            return
        
        # Layout: main content + right panel
        main_col, side_col = st.columns([2, 1])
        
        with side_col:
            # Agent Trace
            st.markdown('<div class="panel-title">⚡ Agent Trace</div>', unsafe_allow_html=True)
            render_agent_trace(result.get("agent_trace", []))
            
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Parsed Problem
            parsed = result.get("parsed_problem", {})
            if parsed:
                st.markdown('<div class="panel-title">🔬 Parsed Problem</div>', unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    topic = parsed.get("topic", "N/A")
                    st.markdown(f'<span class="topic-badge">{topic}</span>', unsafe_allow_html=True)
                with col_b:
                    diff = parsed.get("difficulty", "medium")
                    diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(diff, "⚪")
                    st.markdown(f"{diff_emoji} {diff.title()}")
                
                st.markdown(f"**Problem:** {parsed.get('problem_text', 'N/A')}")
                
                if parsed.get("variables"):
                    st.markdown(f"**Variables:** `{', '.join(parsed['variables'])}`")
                if parsed.get("constraints"):
                    st.markdown(f"**Constraints:** {', '.join(parsed['constraints'])}")
                if parsed.get("what_to_find"):
                    st.markdown(f"**Find:** {parsed['what_to_find']}")
            
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Retrieved Sources
            st.markdown('<div class="panel-title">📚 Knowledge Base Context</div>', unsafe_allow_html=True)
            render_sources(result.get("retrieved_sources", []))
            
            # Similar problems from memory
            similar = result.get("similar_problems_found", [])
            if similar:
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown('<div class="panel-title">🔄 Memory Reuse</div>', unsafe_allow_html=True)
                st.markdown(f"*Found {len(similar)} similar solved problem(s)*")
                for sp in similar[:2]:
                    prob_text = sp.get("parsed_problem", {}).get("problem_text", "")
                    st.markdown(f"""
<div class="memory-card">
    <div style="font-size: 0.82rem; color: #6e6d7a;">{sp.get('topic', 'N/A').title()} · {sp.get('timestamp', '')[:10]}</div>
    <div style="font-size: 0.88rem; margin-top: 0.3rem;">{prob_text[:80]}...</div>
</div>""", unsafe_allow_html=True)

        with main_col:
            # HITL Banner
            if result.get("hitl_required"):
                st.markdown(f"""
<div class="hitl-banner">
    <div class="hitl-icon">⚠️</div>
    <div>
        <div class="hitl-title">Human Review Required</div>
        <div class="hitl-reason">{result.get('hitl_reason', 'Please review and verify this solution.')}</div>
    </div>
</div>""", unsafe_allow_html=True)
            
            # Confidence
            conf = result.get("confidence", 0.8)
            st.markdown(render_confidence(conf), unsafe_allow_html=True)
            
            # Verifier status
            verifier = result.get("verifier_result", {})
            if verifier:
                is_correct = verifier.get("is_correct", True)
                issues = verifier.get("issues_found", [])
                
                if is_correct and not issues:
                    st.success("✅ Solution verified — no issues found")
                elif issues:
                    with st.expander(f"⚠️ Verifier found {len(issues)} potential issue(s)", expanded=False):
                        for issue in issues:
                            st.markdown(f"- {issue}")
                        if verifier.get("corrections_needed"):
                            st.markdown("**Corrections applied:**")
                            for c in verifier["corrections_needed"]:
                                st.markdown(f"- {c}")
            
            # Answer Box
            answer = result.get("answer", "")
            if answer and answer != "See solution above":
                st.markdown(f"""
<div class="answer-box">
    <div class="answer-label">Final Answer</div>
    <div class="answer-text">{answer}</div>
</div>""", unsafe_allow_html=True)
            
            # Solution & Explanation Tabs
            sol_tab, exp_tab = st.tabs(["📐 Solution Steps", "📖 Explanation"])
            
            with sol_tab:
                solution = result.get("solution", "")
                if solution:
                    if st.session_state.get("show_full_solution", True):
                        st.markdown(solution)
                    else:
                        st.markdown(solution[:500] + "..." if len(solution) > 500 else solution)
                else:
                    st.info("Solution not available")
            
            with exp_tab:
                explanation = result.get("explanation", "")
                if explanation:
                    st.markdown('<div class="explanation-box">', unsafe_allow_html=True)
                    st.markdown(explanation)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Explanation not available")
            
            # ─── FEEDBACK ────────────────────────────────────────────────────
            st.markdown("---")
            st.markdown("### 💬 Was this solution correct?")
            
            problem_id = result.get("problem_id")
            
            fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 2])
            
            with fb_col1:
                if st.button("✅ Correct", type="primary", key="fb_correct", use_container_width=True):
                    if problem_id:
                        memory.update_feedback(problem_id, "correct")
                        st.success("🎉 Thanks for confirming! This will improve future solutions.")
                        st.balloons()
            
            with fb_col2:
                if st.button("❌ Incorrect", key="fb_incorrect", use_container_width=True):
                    st.session_state.show_correction_input = True
            
            with fb_col3:
                if st.button("🔄 Re-check (HITL)", key="fb_recheck", use_container_width=True):
                    if result.get("parsed_problem"):
                        st.session_state.show_hitl_review = True
            
            # Correction input
            if st.session_state.get("show_correction_input"):
                st.markdown("**What was wrong? Provide the correct answer or hint:**")
                correction_text = st.text_area("Your correction", key="correction_input", height=80)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Submit Correction", key="submit_correction"):
                        if problem_id and correction_text:
                            memory.update_feedback(problem_id, "incorrect", correction_text)
                            st.success("✅ Correction stored. Thank you! This will improve future solutions.")
                            st.session_state.show_correction_input = False
                with col_b:
                    if st.button("Cancel", key="cancel_correction"):
                        st.session_state.show_correction_input = False
            
            # HITL Review panel
            if st.session_state.get("show_hitl_review"):
                st.markdown("---")
                st.markdown("### 🔍 Human-in-the-Loop Review")
                
                parsed = result.get("parsed_problem", {})
                
                st.markdown("**Review the parsed problem:**")
                reviewed_problem = st.text_area(
                    "Problem text (edit if needed)",
                    value=parsed.get("problem_text", ""),
                    key="hitl_problem",
                    height=80
                )
                
                st.markdown("**Review the solution:**")
                reviewed_solution = st.text_area(
                    "Solution (edit if needed)",
                    value=result.get("solution", "")[:1000],
                    key="hitl_solution",
                    height=120
                )
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("✅ Approve", type="primary", key="hitl_approve"):
                        if problem_id:
                            memory.update_feedback(problem_id, "correct")
                        st.success("Solution approved and stored!")
                        st.session_state.show_hitl_review = False
                with col_b:
                    if st.button("✏️ Approve with Edit", key="hitl_edit"):
                        if problem_id:
                            memory.update_feedback(problem_id, "correct", reviewed_solution)
                        st.success("Edited solution approved!")
                        st.session_state.show_hitl_review = False
                with col_c:
                    if st.button("❌ Reject", key="hitl_reject"):
                        if problem_id:
                            memory.update_feedback(problem_id, "incorrect", "Rejected by human reviewer")
                        st.warning("Solution rejected and flagged.")
                        st.session_state.show_hitl_review = False

    # ─── FOOTER ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
<div style="text-align: center; color: #6e6d7a; font-size: 0.8rem; padding: 1rem 0; font-family: 'Space Mono', monospace;">
    Math Mentor · RAG + Multi-Agent + HITL + Memory · Built for JEE preparation
</div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
