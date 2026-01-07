import streamlit as st
import json
import os

# --- Configuration ---
FILE_NAME = "questions.json"

# --- THE QUESTION BANK ---
INITIAL_QUESTIONS = [
    {
        "id": 1,
        "topic": "Sensitivity Analysis",
        "question": """
**Consider the LP:** Max $Z = 5x_1 + 2x_2 + 3x_3$

**Subject to:**
1) $x_1 + 5x_2 + 2x_3 \\le 30$
2) $x_1 - 5x_2 - 6x_3 \\le 40$
$x_1, x_2, x_3 \\ge 0$

**Given:** Optimal inverse basis $B^{-1} = \\begin{bmatrix} 1 & 0 \\\\ -1 & 1 \\end{bmatrix}$.

**Task:** Calculate the optimal dual solution $w^*$.
""",
        "solution": """
**Formula:** $w = c_B B^{-1}$

* Basic variables: $x_1$ and $s_2$.
* $c_B = [5, 0]$
* Calculation: $[5, 0] \\times \\begin{bmatrix} 1 & 0 \\\\ -1 & 1 \\end{bmatrix} = [5, 0]$

**Answer:** $w_1 = 5, w_2 = 0$
"""
    },
    {
        "id": 2,
        "topic": "Dantzig-Wolfe",
        "question": """
**Problem:** Minimization LP.
**Scenario:** Subproblem returns an unbounded ray $d^* = [3, 1]^T$.

**Task:** What is the coefficient in the convexity row for the new column added to the Master Problem?
""",
        "solution": """
**Answer:** 0

**Explanation:** Since $d^*$ is a direction (ray), we can add any non-negative multiple of it. It does not satisfy the convexity constraint (sum = 1) like extreme points do. Thus, the coefficient is 0.
"""
    },
    {
        "id": 3,
        "topic": "Primal-Dual Theory",
        "question": """
**True or False:** If the Primal LP has a unique optimal solution that is degenerate, the Dual LP must have a unique optimal solution.
""",
        "solution": """
**Answer:** False.

**Justification:** According to the Uniqueness/Degeneracy theorem, if the Primal has a unique but degenerate solution, the Dual problem has **multiple** optimal solutions.
"""
    },
    {
        "id": 4,
        "topic": "Dantzig-Wolfe (Initialization)",
        "question": """
**Scenario:** You are initializing a Dantzig-Wolfe problem.
The Master Problem constraints are:
$2x_1 + 4x_2 + 5x_3 + 2x_4 \\le 7$
$\\sum \\lambda_j = 1$

You find an initial corner point $v_1 = (0, 3)$ from Block 2.
Constraint contribution: $5(0) + 2(3) = 6$.

**Question:** Is this point sufficient to start the Master Problem using only Slack variables?
""",
        "solution": """
**Answer:** Yes.

**Explanation:**
The resource usage of this point is 6.
The available resource is 7.
Since $6 \\le 7$, the slack variable $s$ will be positive ($s = 7-6 = 1$). A valid basic feasible solution exists without needing artificial variables.
"""
    },
    {
        "id": 5,
        "topic": "Theoretical Proof",
        "question": """
**Prove or Disprove:**
If $x^*$ is an optimal solution to the LP:
$\\min c^Tx$ s.t. $Ax \\le b$ and $Dx \\le e$

And if $Dx^* < e$ (strictly less), then $x^*$ is also optimal for the relaxed problem:
$\\min c^Tx$ s.t. $Ax \\le b$
""",
        "solution": """
**Answer:** True.

**Proof (KKT Approach):**
1. By Complementary Slackness, if $Dx^* < e$, the corresponding dual variables $\\mu$ must be **0**.
2. The stationarity condition for the original problem is $c + A^T\\lambda + D^T\\mu = 0$.
3. Since $\\mu=0$, this reduces to $c + A^T\\lambda = 0$.
4. This matches exactly the stationarity condition for the relaxed problem.
5. Thus, $x^*$ satisfies KKT for the relaxed problem.
"""
    },
    {
        "id": 6,
        "topic": "Sensitivity Analysis",
        "question": """
**Given:** A Maximization problem where $x_2$ is non-basic.
Optimal Dual $w^* = [14, 5, 1]$.
Column for $x_2$ is $A_2 = [2, 1, 4]^T$.
Current objective coefficient $c_2 = 3$.

**Task:** Calculate the Reduced Cost of $x_2$. Is it attractive to enter?
""",
        "solution": """
**Calculation:**
Reduced Cost $(z_2 - c_2) = w^* A_2 - c_2$
$= (14(2) + 5(1) + 1(4)) - 3$
$= (28 + 5 + 4) - 3$
$= 37 - 3 = 34$

**Conclusion:**
The reduced cost is **34** (positive).
Since this is a Maximization problem, a positive $(z_j - c_j)$ means the variable is **NOT** attractive. We are already making more 'value' ($z$) than the cost ($c$).
"""
    }
]

# --- Helper Functions ---
def load_questions():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w") as f:
            json.dump(INITIAL_QUESTIONS, f, indent=4)
        return INITIAL_QUESTIONS
    
    with open(FILE_NAME, "r") as f:
        try:
            file_questions = json.load(f)
            # Sync new questions from code
            existing_ids = {q["id"] for q in file_questions}
            new_questions_found = False
            for q in INITIAL_QUESTIONS:
                if q["id"] not in existing_ids:
                    file_questions.append(q)
                    new_questions_found = True
            
            if new_questions_found:
                with open(FILE_NAME, "w") as f_out:
                    json.dump(file_questions, f_out, indent=4)
            return file_questions
        except json.JSONDecodeError:
            return INITIAL_QUESTIONS

# --- App Layout ---
st.set_page_config(page_title="OR Exam Prep", layout="centered")

# --- VISIBILITY FIX: FORCE BLACK TEXT EVERYWHERE ---
st.markdown("""
<style>
    /* 1. Force Main Background to White */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* 2. Force ALL text to be black */
    p, h1, h2, h3, h4, h5, h6, li, div, span {
        color: #000000 !important;
    }
    
    /* 3. Question Card Styling */
    .question-card {
        background-color: #f8f9fa; /* Light Grey background */
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* 4. Fix Success Box (Solution Area) Text Color */
    .stSuccess {
        background-color: #d4edda !important;
        color: #155724 !important; /* Dark Green Text */
    }
    .stSuccess p, .stSuccess div {
        color: #155724 !important;
    }
    
    
    /* 5. Topic Badge */
    .topic-badge {
        background-color: #007bff;
        color: white !important;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Linear Optimization Final Prep")

questions = load_questions()

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

st.progress((st.session_state.current_index + 1) / len(questions))
st.caption(f"Question {st.session_state.current_index + 1} of {len(questions)}")

# --- The Question Card ---
with st.container():
    # We render the topic badge and structure via HTML
    st.markdown(f"""
    <div class="question-card">
        <span class="topic-badge">{current_q.get('topic', 'General')}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # We render the Question Text separately using Streamlit Markdown
    # This ensures LaTeX math renders correctly while inheriting our black text color
    st.info(current_q["question"])

# --- Controls ---
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Previous", use_container_width=True):
        prev_question()
        st.rerun()
with col2:
    btn_text = "🙈 Hide Solution" if st.session_state.show_solution else "👁️ Reveal Solution"
    if st.button(btn_text, type="primary", use_container_width=True):
        toggle_solution()
        st.rerun()
with col3:
    if st.button("Next ➡️", use_container_width=True):
        next_question()
        st.rerun()

# --- Solution Area ---
if st.session_state.show_solution:
    st.markdown("### Solution")
    st.success(current_q["solution"])