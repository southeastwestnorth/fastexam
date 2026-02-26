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

# --- 2. STYLING & FIXING VISIBILITY ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Footer Styling */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f1f1f1 !important; color: #333 !important; text-align: center;
        padding: 10px; font-weight: bold; border-top: 2px solid #007bff; z-index: 100;
    }
    
    /* Timer Box - Fixed Visibility for Dark/Light Mode */
    .timer-container {
        position: fixed; 
        top: 70px; 
        right: 20px;
        background-color: #ffeb3b !important; /* Bright Yellow Background */
        color: #000000 !important;           /* Black Text */
        padding: 15px; 
        border: 3px solid #f44336;
        border-radius: 12px; 
        z-index: 9999; 
        font-size: 22px; 
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }

    .question-style {
        font-size: 20px;
        font-weight: 600;
        color: #FFFFFF;
        background-color: #1E3A8A;
        padding: 10px;
        border-radius: 5px;
        margin-top: 20px;
    }
    </style>
    <div class="footer">Made by Imran</div>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'exam_started' not in st.session_state:
    st.session_state.exam_started = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'end_time' not in st.session_state:
    st.session_state.end_time = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'questions' not in st.session_state:
    try:
        df = pd.read_csv("questions.csv")
        # Store questions in session to prevent shuffling on every click
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    except Exception as e:
        st.error(f"Error: Ensure 'questions.csv' exists. ({e})")
        st.stop()

# --- 4. TIMER LOGIC (JavaScript) ---
def display_timer(seconds_left):
    # JS countdown that works even if Python is busy
    timer_html = f"""
        <div id="timer-box" class="timer-container">
            ⏳ <span id="time-display">--:--</span>
        </div>
        <script>
        var duration = {seconds_left};
        var display = document.querySelector('#time-display');
        var timer = duration, minutes, seconds;
        
        var interval = setInterval(function () {{
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            display.textContent = minutes + ":" + seconds;

            if (--timer < 0) {{
                clearInterval(interval);
                display.textContent = "00:00";
                // Trigger the hidden submit button if time runs out
                window.parent.document.querySelector('button[kind="primary"]').click();
            }}
        }}, 1000);
        </script>
    """
    st.markdown(timer_html, unsafe_allow_html=True)

# --- 5. RESULT CARD GENERATOR ---
def generate_result_card(score, total, df, user_answers):
    perc = (score / total) * 100
    card = f"FAST EXAM - RESULT CARD\n"
    card += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    card += f"Final Score: {score} / {total} ({perc:.1f}%)\n"
    card += "========================================\n\n"
    
    wrong_questions = []
    for i, row in df.iterrows():
        u_ans = user_answers.get(i)
        c_ans = row['Correct Answer']
        if str(u_ans) != str(c_ans):
            wrong_questions.append({
                "q": row['Question'],
                "mine": u_ans if u_ans else "Not Answered",
                "correct": c_ans
            })
            
    if not wrong_questions:
        card += "EXCELLENT! You got every question correct.\n"
    else:
        card += "REVIEW OF INCORRECT ANSWERS:\n\n"
        for idx, item in enumerate(wrong_questions):
            card += f"{idx+1}) QUESTION: {item['q']}\n"
            card += f"   - Your Answer: {item['mine']}\n"
            card += f"   - Right Answer: {item['correct']}\n"
            card += "----------------------------------------\n"
            
    return card

# --- 6. MAIN APP FLOW ---

df = st.session_state.questions
total_qs = len(df)
time_limit_secs = total_qs * 60  # Auto: 1 min per question

st.title("FastExam")

# SCREEN 1: START
if not st.session_state.exam_started and not st.session_state.submitted:
    st.markdown(f"### Total Questions found: `{total_qs}`")
    st.write(f"⏱️ You will have **{total_qs} minutes** to complete the exam.")
    st.info("The timer will appear in the top-right corner once you start.")
    
    if st.button("🚀 Start Exam Now", use_container_width=True):
        st.session_state.end_time = time.time() + time_limit_secs
        st.session_state.exam_started = True
        st.rerun()

# SCREEN 2: EXAM IN PROGRESS
elif st.session_state.exam_started and not st.session_state.submitted:
    # Calculate time remaining
    remaining = int(st.session_state.end_time - time.time())
    
    # Check if time is up
    if remaining <= 0:
        st.session_state.submitted = True
        st.session_state.exam_started = False
        st.rerun()

    # Show visible JS timer
    display_timer(remaining)

    # Use form to prevent laggy reruns on every selection
    with st.form("quiz_form"):
        current_selection = {}
        for i, row in df.iterrows():
            st.markdown(f"<div class='question-style'>Q{i+1}. {row['Question']}</div>", unsafe_allow_html=True)
            options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
            current_selection[i] = st.radio(
                f"Select for Q{i}", options, 
                index=None, key=f"q{i}", label_visibility="collapsed"
            )
            st.write("")
        
        # This button is used for manual submission and targeted by the timer JS
        submitted_manually = st.form_submit_button("Submit Exam", type="primary")
        if submitted_manually:
            st.session_state.user_answers = current_selection
            st.session_state.submitted = True
            st.session_state.exam_started = False
            st.rerun()

# SCREEN 3: RESULTS
elif st.session_state.submitted:
    st.header("📊 Exam Results")
    
    score = 0
    u_ans = st.session_state.user_answers
    for i, row in df.iterrows():
        if str(u_ans.get(i)) == str(row['Correct Answer']):
            score += 1
            
    perc = (score / total_qs) * 100
    st.subheader(f"Score: {score} / {total_qs} ({perc:.1f}%)")

    # Result Card Download
    result_card_txt = generate_result_card(score, total_qs, df, u_ans)
    st.download_button(
        label="📥 Download Result Card (TXT File)",
        data=result_card_txt,
        file_name=f"FastExam_Result_{datetime.now().strftime('%M%S')}.txt",
        mime="text/plain"
    )

    # UI Review of Wrong Answers
    with st.expander("🔍 View All Incorrect Answers"):
        has_wrong = False
        for i, row in df.iterrows():
            if str(u_ans.get(i)) != str(row['Correct Answer']):
                has_wrong = True
                st.error(f"**Q{i+1}: {row['Question']}**")
                st.write(f"❌ Your Answer: {u_ans.get(i)}")
                st.success(f"✅ Correct Answer: {row['Correct Answer']}")
                st.divider()
        if not has_wrong:
            st.balloons()
            st.success("Perfect Score! No errors to show.")

    if st.button("🔄 Restart Exam"):
        # Reset everything
        for key in ['exam_started', 'submitted', 'end_time', 'user_answers', 'questions']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
