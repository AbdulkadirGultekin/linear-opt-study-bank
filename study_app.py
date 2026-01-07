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
    },
    {
        "id": 101,
        "topic": "Dantzig-Wolfe (Bounds)",
        "question": """
**Problem:** You are maximizing $Z$ using Dantzig-Wolfe.
At the current iteration:
1. The Master Problem optimal value is $Z_{MP} = 100$.
2. The current dual solution is $(\\pi, \\alpha)$.
3. You solve the subproblem and find an optimal solution $x_{sub}$ with objective value $Z_{sub} = 20$.
4. The value of the dual variable for the convexity constraint is $\\alpha = 15$.

**Task:** Determine the **Upper Bound** on the true optimal objective value $Z^*$.
""",
        "solution": """
**Answer:** 105

**Explanation:**
For a Maximization problem:
* **Lower Bound:** The current Master Problem value ($Z_{MP} = 100$).
* **Upper Bound:** $Z_{MP} + \\text{Reduced Cost of the new column}$.

First, calculate the Reduced Cost:
$\\text{Reduced Cost} = Z_{sub} - \\alpha = 20 - 15 = 5$.

Upper Bound = $100 + 5 = 105$.
*(Note: If the reduced cost were $\\le 0$, we would be optimal.)*
"""
    },
    {
        "id": 102,
        "topic": "Sensitivity Analysis (Structural)",
        "question": """
**Scenario:** You have an optimal basis $B$.
You want to change a constraint coefficient $a_{ij}$ for a variable $x_j$.

**Question:** Why is the sensitivity analysis much harder if $x_j$ is a **Basic** variable compared to a **Non-Basic** variable?
""",
        "solution": """
**Answer:** It alters the Basis Matrix $B$ itself.

**Explanation:**
* **If $x_j$ is Non-Basic:** Only its column in $N$ changes. We essentially just check if its new reduced cost remains correct. $B^{-1}$ stays the same.
* **If $x_j$ is Basic:** The column is inside $B$. Changing it changes $B$, which changes $B^{-1}$. Since $B^{-1}$ affects **every** calculation in the tableau (RHS, shadow prices, all reduced costs), the entire tableau structure is disrupted. We usually cannot use simple range formulas and may need to re-invert or use the Sherman-Morrison formula.
"""
    },
    {
        "id": 103,
        "topic": "Primal-Dual Theory",
        "question": """
**Statement:** "If the Dual LP has alternative optimal solutions, then the Primal LP must be degenerate."

**Task:** Prove this statement is True using Complementary Slackness.
""",
        "solution": """
**Proof:**
1. Let $w^1$ and $w^2$ be two distinct optimal dual solutions.
2. Their convex combination $w^* = 0.5w^1 + 0.5w^2$ is also optimal.
3. Since $w^1 \\neq w^2$, there exists some index (constraint) where the dual constraints are "looser" for the mix than for the individual corners, or simply that the set of binding dual constraints is smaller than the number of variables.
4. More formally: If the Dual has multiple solutions, the Dual feasible region's optimal face has dimension $\\ge 1$.
5. By Strict Complementary Slackness, if the Dual has "extra" freedom (variables not fixed to zero/boundaries), the corresponding Primal variables must be fixed to zero.
6. This forces "extra" zeros in the Primal solution beyond the standard $n-m$ non-basics, satisfying the definition of Primal Degeneracy.
"""
    },
    {
        "id": 104,
        "topic": "Dantzig-Wolfe (Unboundedness)",
        "question": """
**True or False:**
In the Dantzig-Wolfe algorithm, if the **Subproblem** is unbounded (returns a ray), then the **Original Master Problem** must also be unbounded.
""",
        "solution": """
**Answer:** False.

**Explanation:**
The Subproblem ignores the coupling constraints (A matrices). It only checks $x \\in X$.
* It is possible that $x$ can go to infinity inside the region $X$ (Subproblem unbounded).
* However, the **Coupling Constraints** in the Master Problem might "cut off" that ray.
* When we add the ray to the Master Problem, the Master Problem will assign a finite weight ($\\mu$) to it, limited by the coupling constraints. The original problem is only unbounded if the Master Problem *also* becomes unbounded after adding the ray.
"""
    },
    {
        "id": 105,
        "topic": "Strict Complementary Slackness",
        "question": """
**Problem:**
You have 3 distinct optimal primal-dual pairs: $(x^1, w^1), (x^2, w^2), (x^3, w^3)$.
None of them individually satisfy Strict Complementary Slackness (SCS) for all indices.

**Task:** How can you mathematically generate a single pair $(x^*, w^*)$ that is guaranteed to satisfy SCS for the entire problem?
""",
        "solution": """
**Method:** Barycenter (Averaging)

**Formula:**
$x^* = \\frac{1}{3}(x^1 + x^2 + x^3)$
$w^* = \\frac{1}{3}(w^1 + w^2 + w^3)$

**Why it works:**
For any index $j$, if *any* of the individual solutions has a strict inequality (e.g., $x_j^k > 0$), the average $x_j^*$ will be positive because all $x \\ge 0$. The average "accumulates" the positivity of all individual solutions. Since an SCS solution is known to exist (Goldman-Tucker Theorem), the convex combination of all BFS optima will yield it.
"""
    },
    {
        "id": 12,
        "topic": "Sensitivity Analysis (Matrix)",
        "question": """
**Problem:**
Consider an LP with optimal basis $B$. You want to check if the current basis remains optimal if the objective coefficient of a **basic** variable $x_k$ changes by $\\Delta$.

**Task:**
Explain why you cannot simply check $z_k - c_k \\ge 0$. What specific formula must be satisfied for *all* non-basic variables $j$?
""",
        "solution": """
**Answer:**
Changing $c_k$ (where $x_k$ is basic) changes the dual vector $w = c_B B^{-1}$.
Since $w$ changes, the reduced cost of **every** non-basic variable potentially changes.

**Formula:**
You must check:
$(z_j - c_j)_{new} = (w_{old} + \\Delta \\cdot (B^{-1})_{row \\ k}) A_j - c_j \\ge 0$
for **all** non-basic variables $j$. The range is determined by the tightest of these constraints.
"""
    },
    {
        "id": 13,
        "topic": "Dantzig-Wolfe (Block Structure)",
        "question": """
**Scenario:**
You are solving a problem with 2 blocks using Dantzig-Wolfe.
* Block 1 generates a proposal $v_1$ with profit 10 and resource usage 4.
* Block 2 generates a proposal $v_2$ with profit 12 and resource usage 6.

The Master Problem has a single coupling constraint with capacity 8.

**Question:**
Can the Master Problem simply select $v_1$ and $v_2$ both at full strength? If not, how does it mathematically combine them?
""",
        "solution": """
**Answer:** No.

**Explanation:**
Total resource usage = $4 + 6 = 10$, which exceeds capacity 8.
The Master Problem will find weights $\\lambda_{1}$ and $\\lambda_{2}$ such that:
1. $4\\lambda_{1} + 6\\lambda_{2} \\le 8$
2. $\\lambda_{1} = 1$ (Convexity Block 1)
3. $\\lambda_{2} = 1$ (Convexity Block 2)

Since this system is infeasible with $\\lambda=1$, the Master Problem cannot pick both fully. It implies the current set of columns might be insufficient to find a feasible solution if these are the only options, or it must use slack/artificial variables if available. In a real iteration, it would mix these with the 'zero' solution or other columns.
"""
    },
    {
        "id": 14,
        "topic": "Primal-Dual Theory (Strict Slackness)",
        "question": """
**Problem:**
Let $x^*$ and $w^*$ be a primal-dual optimal pair.
Suppose for a specific variable $x_j$, we have $x_j^* = 0$ and the corresponding reduced cost is also 0 (i.e., $z_j - c_j = 0$).

**Task:**
Does this pair satisfy **Strict** Complementary Slackness? What does this imply about the solution space?
""",
        "solution": """
**Answer:** No.

**Explanation:**
Strict Complementary Slackness requires that $x_j + s_j > 0$. Here, both are zero ($x_j^*=0$ and dual slack $s_j = z_j - c_j = 0$).

**Implication:**
This indicates **Degeneracy**. specifically, it usually implies that there are alternative optimal solutions (either in the primal or the dual) that could be pivoted to. This specific pair sits on the boundary where strictness fails.
"""
    },
    {
        "id": 15,
        "topic": "Sensitivity Analysis (RHS)",
        "question": """
**Problem:**
You are given the optimal inverse basis $B^{-1} = \\begin{bmatrix} 2 & -1 \\\\ -1 & 1 \\end{bmatrix}$ and the original RHS $b = \\begin{bmatrix} 10 \\\\ 8 \\end{bmatrix}$.

**Task:**
Calculate the current values of the basic variables $x_B$. Then, determine how much $b_2$ can increase before the current basis becomes infeasible.
""",
        "solution": """
**1. Current Values:**
$x_B = B^{-1}b = \\begin{bmatrix} 2 & -1 \\\\ -1 & 1 \\end{bmatrix} \\begin{bmatrix} 10 \\\\ 8 \\end{bmatrix} = \\begin{bmatrix} 20 - 8 \\\\ -10 + 8 \\end{bmatrix} = \\begin{bmatrix} 12 \\\\ -2 \\end{bmatrix}$.
*(Wait! The current basis is infeasible ($x_2 = -2$). If this was an optimal table provided in a problem, check for typos. Assuming standard feasibility context:)*

**2. Range for $b_2$ (let $b_2 = 8 + \\Delta$):**
$x_B(\\Delta) = \\begin{bmatrix} 2 & -1 \\\\ -1 & 1 \\end{bmatrix} \\begin{bmatrix} 10 \\\\ 8+\\Delta \\end{bmatrix} = \\begin{bmatrix} 12 - \\Delta \\\\ -2 + \\Delta \\end{bmatrix}$.

For feasibility ($x_B \\ge 0$):
* $12 - \\Delta \\ge 0 \\implies \\Delta \\le 12$
* $-2 + \\Delta \\ge 0 \\implies \\Delta \\ge 2$

**Answer:** $b_2$ must **increase** by at least 2 units (to make $x_2 \\ge 0$) and can increase up to 12 additional units.
"""
    },
    {
        "id": 16,
        "topic": "Dantzig-Wolfe (Initialization)",
        "question": """
**Scenario:**
You are initializing a Master Problem. You cannot find any obvious feasible starting columns from the subproblems that satisfy the coupling constraint $Ax \\le b$.

**Task:**
What is the standard "Phase 1" approach to handle this in Dantzig-Wolfe?
""",
        "solution": """
**Answer:** Add Artificial Variables.

**Explanation:**
1. Introduce artificial variables $a_i$ to the coupling constraints: $\\sum \\lambda_j (Ax_j) + a = b$.
2. Assign a large penalty cost (Big-M) to $a$ in the Master objective.
3. Run the Dantzig-Wolfe iterations. The high cost will force the Master Problem to request columns from the subproblems that help reduce $a$ to zero.
4. Once $a=0$, discard it and continue with the feasible columns found.
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
st.set_page_config(page_title="OR Exam Prep", layout="centered", page_icon="🎓")

# --- CSS STYLING (THE "DARK MODE NATIVE" THEME) ---
st.markdown("""
<style>
    /* 1. Reset: We let Streamlit control the main background (Black/Dark Grey) */
    
    /* 2. Dark Card Design */
    .question-card {
        background-color: #262730; /* Streamlit's Native Dark Grey */
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #4a4a4a; /* Subtle border for definition */
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); /* Stronger shadow for depth */
        margin-bottom: 25px;
    }
    
    /* 3. Text Contrast Enforcement */
    /* Force text inside the card to be White/Light Grey */
    .question-card p, .question-card li, .question-card div, .question-card span, h1, h2, h3 {
        color: #FAFAFA !important;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.6;
    }

    /* 4. Topic Badge (Cyan/Blue for Cyber look) */
    .topic-badge {
        background-color: #0e1117; /* Very dark contrast */
        color: #4db8ff !important; /* Bright Cyan text */
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

    /* 5. Success/Solution Box (Dark Green Theme) */
    .stSuccess {
        background-color: #1b2e21 !important; /* Dark Green bg */
        color: #d4edda !important; /* Light Green text */
        border: 1px solid #2e5c3b;
    }
    .stSuccess p, .stSuccess div {
        color: #d4edda !important;
    }
    
    /* 6. Streamlit Info Box Override (Make it blend) */
    .stAlert {
        background-color: transparent !important;
        border: none !important;
        color: #FAFAFA !important;
    }

    /* 7. Buttons */
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

questions = load_questions()

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
    # FIXED: Indentation removed from HTML string to prevent Code Block rendering
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
