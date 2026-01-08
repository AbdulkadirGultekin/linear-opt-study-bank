import streamlit as st
import json
import os

# --- Configuration ---
FILE_NAME = "questions.json"

# --- Helper Functions ---
def load_questions():
    """Strictly loads from questions.json."""
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

# --- CSS STYLING ---
st.markdown("""
<style>
    /* Dark Card Design */
    .question-card {
        background-color: #262730;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #4a4a4a;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-top: 10px;
        margin-bottom: 25px;
    }
    .question-card p, .question-card li, .question-card div, .question-card span, h1, h2, h3 {
        color: #FAFAFA !important;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.6;
    }
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
    .stSuccess {
        background-color: #1b2e21 !important;
        color: #d4edda !important;
        border: 1px solid #2e5c3b;
    }
    .stSuccess p, .stSuccess div { color: #d4edda !important; }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        height: 3rem;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
all_questions = load_questions()

# --- SIDEBAR: COURSE SELECTION ---
st.sidebar.title("📚 Select Course")
course_options = ["IE553 Linear Optimization", "IE455 Combinatorial Analysis"]

# We use a session state to track if the course changed so we can reset index
if "selected_course" not in st.session_state:
    st.session_state.selected_course = course_options[0]

# Radio button for selection
new_course_selection = st.sidebar.radio(
    "Available Lessons:", 
    course_options, 
    index=course_options.index(st.session_state.selected_course)
)

# Detect Change & Reset
if new_course_selection != st.session_state.selected_course:
    st.session_state.selected_course = new_course_selection
    st.session_state.current_index = 0 # Reset to Q1
    st.session_state.show_solution = False # Hide solution
    st.rerun()

# --- FILTERING LOGIC ---
# Extract the code (IE553 or IE455) from the selection string
target_code = st.session_state.selected_course.split()[0]

# Filter list. Default to "IE553" if 'lesson' key is missing.
filtered_questions = [
    q for q in all_questions 
    if q.get("lesson", "IE553") == target_code
]

# --- MAIN CONTENT ---
st.title(f"🎓 {target_code} Prep")

if not filtered_questions:
    st.info(f"No questions found for **{target_code}**. Add some to `questions.json` with `\"lesson\": \"{target_code}\"`!")
    st.stop()

# --- State Management ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'show_solution' not in st.session_state:
    st.session_state.show_solution = False

# Ensure index is valid (safety check)
if st.session_state.current_index >= len(filtered_questions):
    st.session_state.current_index = 0

current_q = filtered_questions[st.session_state.current_index]

# --- Helper Functions ---
def next_question():
    if st.session_state.current_index < len(filtered_questions) - 1:
        st.session_state.current_index += 1
        st.session_state.show_solution = False

def prev_question():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        st.session_state.show_solution = False

def toggle_solution():
    st.session_state.show_solution = not st.session_state.show_solution

# --- Progress Bar ---
st.progress((st.session_state.current_index + 1) / len(filtered_questions))
st.caption(f"Question {st.session_state.current_index + 1} of {len(filtered_questions)}")

# --- CONTROLS ---
st.markdown("###")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Previous", use_container_width=True):
        prev_question()
        st.rerun()

with col2:
    btn_text = "🙈 Hide Solution" if st.session_state.show_solution else "👁️ Reveal Solution"
    btn_type = "primary" if not st.session_state.show_solution else "secondary"
    if st.button(btn_text, type=btn_type, use_container_width=True):
        toggle_solution()
        st.rerun()

with col3:
    if st.button("Next ➡️", use_container_width=True):
        next_question()
        st.rerun()

# --- CARD ---
with st.container():
    st.markdown(f"""<div class="question-card">
<div class="topic-badge">{current_q.get('topic', 'General')}</div>
<div style="font-size: 1.1em; margin-top: 10px;">
{current_q["question"]} 
</div>
</div>""", unsafe_allow_html=True)

# --- SOLUTION ---
if st.session_state.show_solution:
    st.markdown("---")
    st.success(current_q["solution"])
