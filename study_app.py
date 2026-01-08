import streamlit as st
import json
import os

# --- Configuration ---
FILE_NAME = "questions.json"

# --- Helper Functions ---
def load_questions():
    """
    Strictly loads from questions.json. 
    Returns an empty list if file is missing or broken.
    """
    if not os.path.exists(FILE_NAME):
        return []
    
    with open(FILE_NAME, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            st.error(f"Error reading {FILE_NAME}. Please check the JSON format.")
            return []

# --- App Layout ---
st.set_page_config(page_title="OR Exam Prep", layout="centered", page_icon="🎓")

# --- CSS STYLING (Dark Mode Native) ---
st.markdown("""
<style>
    /* Dark Card Design */
    .question-card {
        background-color: #262730;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #4a4a4a;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    }
    
    /* Text Contrast Enforcement */
    .question-card p, .question-card li, .question-card div, .question-card span, h1, h2, h3 {
        color: #FAFAFA !important;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.6;
    }

    /* Topic Badge */
    .topic-badge {
        background-color: #0e1117;
        color: #4db8ff !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 6px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 20px;
        border: 1px solid #4db8ff;
    }

    /* Success Box */
    .stSuccess {
        background-color: #1b2e21 !important;
        color: #d4edda !important;
        border: 1px solid #2e5c3b;
    }
    .stSuccess p, .stSuccess div {
        color: #d4edda !important;
    }

    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        height: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🎓 Operations Research Prep")
st.caption("Comprehensive Exam Review • Dark Mode Edition 🌙")

# --- Load Data ---
questions = load_questions()

# --- Handle Empty File ---
if not questions:
    st.warning("No questions found in `questions.json`. Please add some questions to the file!")
    st.stop()

# --- State Management ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'show_solution' not in st.session_state:
    st.session_state.show_solution = False

def next_question():
    if st.session_state.current_index < len(questions) - 1:
        st.session_state.current_index += 1
        st.session_state.show_solution = False

def prev_question():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        st.session_state.show_solution = False

def toggle_solution():
    st.session_state.show_solution = not st.session_state.show_solution

current_q = questions[st.session_state.current_index]

# --- Progress Bar ---
st.progress((st.session_state.current_index + 1) / len(questions))
st.caption(f"Question {st.session_state.current_index + 1} of {len(questions)}")

# --- The Flashcard ---
with st.container():
    st.markdown(f"""<div class="question-card">
<div class="topic-badge">{current_q.get('topic', 'General')}</div>
<div style="font-size: 1.1em; margin-top: 10px;">
{current_q["question"]} 
</div>
</div>""", unsafe_allow_html=True)

# --- Controls ---
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Previous", use_container_width=True):
        prev_question()
        st.rerun()
with col2:
    label = "🙈 Hide Solution" if st.session_state.show_solution else "👁️ Reveal Solution"
    if st.button(label, type="primary", use_container_width=True):
        toggle_solution()
        st.rerun()
with col3:
    if st.button("Next ➡️", use_container_width=True):
        next_question()
        st.rerun()

# --- Solution Reveal ---
if st.session_state.show_solution:
    st.markdown("---")
    st.success(current_q["solution"])
