import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FastExam",
    page_icon="🔬",
    layout="centered"
)

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Footer */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f1f1f1 !important; color: #333 !important; 
        text-align: center; padding: 10px; font-weight: bold; 
        border-top: 2px solid #007bff; z-index: 100;
    }
    
    /* Radio Buttons High Contrast */
    .stRadio[data-testid="stWidgetLabel"] p {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #4da3ff !important;
    }
    </style>
    <div class="footer">Made by Imran</div>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'exam_started' not in st.session_state:
    st.session_state.exam_started = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'end_time' not in st.session_state:
    st.session_state.end_time = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

# --- 4. DATA LOADING ---
if 'questions' not in st.session_state:
    try:
        df = pd.read_csv("questions.csv")
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    except Exception as e:
        st.error("Error: 'questions.csv' not found. Please place it in the same folder.")
        st.stop()

# --- 5. BULLETPROOF TIMER LOGIC ---
def render_timer(seconds_left):
    # Placed right at the top of the page, NOT floating. 
    # Formatted strictly to prevent Streamlit from parsing it as Markdown.
    timer_html = f"""
    <div style="background-color: #FFEB3B !important; color: #000000 !important; padding: 15px !important; border-radius: 10px !important; border: 4px solid #F44336 !important; text-align: center !important; font-size: 28px !important; font-weight: 900 !important; margin-bottom: 25px !important; box-shadow: 0px 4px 10px rgba(0,0,0,0.5);">
        ⏳ Time Remaining: <span id="clock-display">--:--</span>
    </div>
    <script>
    (function(){{
        var timeLeft = {seconds_left};
        var display = document.getElementById('clock-display');
        var timerId = setInterval(function() {{
            if (timeLeft <= 0) {{
                clearInterval(timerId);
                display.innerText = "00:00";
                // Auto-submit when time is up
                var btns = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {{
                    if (btns[i].innerText.includes('Submit Exam')) {{
                        btns[i].click();
                        break;
                    }}
                }}
            }} else {{
                var m = Math.floor(timeLeft / 60);
                var s = timeLeft % 60;
                display.innerText = (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
                timeLeft--;
            }}
        }}, 1000);
    }})();
    </script>
    """
    st.markdown(timer_html, unsafe_allow_html=True)

# --- 6. RESULT CARD GENERATOR ---
def generate_result_txt(score, total, df, user_answers):
    report = f"--- FAST EXAM RESULT CARD ---\n"
    report += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"Final Score: {score} / {total} ({round(score/total*100, 1)}%)\n"
    report += "-------------------------------------------\n\n"
    
    report += "REVIEW OF INCORRECT ANSWERS:\n\n"
    
    incorrect_found = False
    for i, row in df.iterrows():
        ans = user_answers.get(i)
        if str(ans) != str(row['Correct Answer']):
            incorrect_found = True
            report += f"QUESTION: {row['Question']}\n"
            report += f"   [X] Your Answer: {ans if ans else 'Not Answered'}\n"
            report += f"   [✓] Correct Answer: {row['Correct Answer']}\n"
            report += f"{'-'*40}\n"
            
    if not incorrect_found:
        report += "PERFECT SCORE! No errors found."
        
    return report

# --- 7. APP LOGIC ---
df = st.session_state.questions
total_qs = len(df)
time_limit_secs = total_qs * 60  # Auto calculate 1 min per question

st.title("FastExam")

# SCREEN 1: START
if not st.session_state.exam_started and not st.session_state.submitted:
    st.info(f"📋 **Total Questions:** {total_qs}")
    st.info(f"⏳ **Total Time:** {total_qs} Minutes")
    st.warning("Once started, the timer will not stop even if you refresh the page.")
    
    if st.button("🚀 Start Exam Now", use_container_width=True, type="primary"):
        st.session_state.end_time = time.time() + time_limit_secs
        st.session_state.exam_started = True
        st.rerun()

# SCREEN 2: EXAM
elif st.session_state.exam_started and not st.session_state.submitted:
    # 1. Server-side time check
    remaining = int(st.session_state.end_time - time.time())
    
    if remaining <= 0:
        st.session_state.submitted = True
        st.session_state.exam_started = False
        st.rerun()

    # 2. Render the giant visible timer
    render_timer(remaining)

    # 3. The Exam Form
    with st.form("exam_form"):
        temp_answers = {}
        for i, row in df.iterrows():
            st.markdown(f"### Q{i+1}. {row['Question']}")
            options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
            temp_answers[i] = st.radio("Select answer:", options, index=None, key=f"q{i}", label_visibility="collapsed")
            st.write("---")
        
        # This button is clicked manually by user, OR automatically by the Javascript timer
        if st.form_submit_button("Submit Exam", type="primary", use_container_width=True):
            st.session_state.user_answers = temp_answers
            st.session_state.submitted = True
            st.session_state.exam_started = False
            st.rerun()

# SCREEN 3: RESULTS
elif st.session_state.submitted:
    st.header("📊 Exam Statistics")
    
    score = 0
    u_an
