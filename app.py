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

# --- 2. STYLING & FOOTER ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f1f1f1; color: #333; text-align: center;
        padding: 10px; font-weight: bold; border-top: 2px solid #007bff; z-index: 100;
    }
    .stRadio > label { font-size: 18px; font-weight: bold; color: #1E3A8A; }
    .timer-container {
        position: fixed; top: 10px; right: 10px;
        background: white; padding: 10px; border: 2px solid #007bff;
        border-radius: 10px; z-index: 1000; font-size: 20px; font-weight: bold;
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
        # Load the CSV
        df = pd.read_csv("questions.csv")
        # Store in session state to prevent reshuffling on every rerun
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    except FileNotFoundError:
        st.error("Error: 'questions.csv' not found. Please upload the file.")
        st.stop()

# --- 4. TIMER LOGIC (JS Injection for smoothness) ---
def display_timer(seconds_left):
    # This JS keeps the timer ticking visually even when Streamlit is 'busy'
    timer_html = f"""
        <div id="timer" class="timer-container">⏳ Time Left: <span id="time-display">--:--</span></div>
        <script>
        var duration = {seconds_left};
        var display = document.querySelector('#time-display');
        var timer = duration, minutes, seconds;
        var countdown = setInterval(function () {{
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
            display.textContent = minutes + ":" + seconds;
            if (--timer < 0) {{
                clearInterval(countdown);
                window.parent.document.querySelector('button[kind="primary"]').click();
            }}
        }}, 1000);
        </script>
    """
    st.markdown(timer_html, unsafe_allow_html=True)

# --- 5. RESULT CARD GENERATOR ---
def generate_result_text(score, total, df, user_answers):
    perc = (score / total) * 100
    text = f"--- SCIENCE EXAM PORTAL RESULT CARD ---\n"
    text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += f"Score: {score}/{total} ({perc:.1f}%)\n"
    text += f"Status: {'PASSED' if perc >= 40 else 'FAILED'}\n"
    text += "-"*40 + "\n\n"
    
    text += "INCORRECT ANSWERS REVIEW:\n"
    incorrect_count = 0
    for i, row in df.iterrows():
        u_ans = user_answers.get(i)
        c_ans = row['Correct Answer']
        if str(u_ans) != str(c_ans):
            incorrect_count += 1
            text += f"Q{i+1}: {row['Question']}\n"
            text += f"   - Your Answer: {u_ans if u_ans else 'No Answer'}\n"
            text += f"   - Correct Answer: {c_ans}\n"
            text += "-"*20 + "\n"
            
    if incorrect_count == 0:
        text += "Excellent! You got everything correct."
    
    return text

# --- 6. APP FLOW ---

df = st.session_state.questions
total_qs = len(df)
time_limit_secs = total_qs * 60  # Auto-calculate: 1 min per question

st.title("🧪 Science Model Test")

# SCENE 1: Start Screen
if not st.session_state.exam_started and not st.session_state.submitted:
    st.info(f"📋 Exam contains **{total_qs} questions**.")
    st.info(f"⏳ You have **{total_qs} minutes** total.")
    if st.button("🚀 Start Exam Now"):
        st.session_state.end_time = time.time() + time_limit_secs
        st.session_state.exam_started = True
        st.rerun()

# SCENE 2: The Exam
elif st.session_state.exam_started and not st.session_state.submitted:
    # Calculate time remaining for the JS timer
    now = time.time()
    remaining = int(st.session_state.end_time - now)

    # Force auto-submit if time is actually up
    if remaining <= 0:
        st.session_state.submitted = True
        st.session_state.exam_started = False
        st.rerun()

    display_timer(remaining)

    # Question Form
    with st.form("exam_form"):
        current_answers = {}
        for i, row in df.iterrows():
            st.markdown(f"**Q{i+1}. {row['Question']}**")
            options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
            current_answers[i] = st.radio(
                f"Select answer for {i}", options, 
                index=None, key=f"q{i}", label_visibility="collapsed"
            )
            st.write("---")
        
        # This button triggers the submission
        submit_button = st.form_submit_button("Submit Exam", type="primary")
        if submit_button:
            st.session_state.user_answers = current_answers
            st.session_state.submitted = True
            st.session_state.exam_started = False
            st.rerun()

# SCENE 3: Results Screen
elif st.session_state.submitted:
    st.header("📊 Exam Result")
    
    # Calculate Score
    score = 0
    user_ans = st.session_state.user_answers
    for i, row in df.iterrows():
        if str(user_ans.get(i)) == str(row['Correct Answer']):
            score += 1
            
    perc = (score / total_qs) * 100
    st.subheader(f"Your Final Score: {score} / {total_qs}")
    
    if perc >= 80: st.success(f"Grade: Excellent ({perc:.1f}%) 🌟")
    elif perc >= 40: st.warning(f"Grade: Passed ({perc:.1f}%) 👍")
    else: st.error(f"Grade: Failed ({perc:.1f}%) 📚")

    # Result Card Download
    result_card_data = generate_result_text(score, total_qs, df, user_ans)
    st.download_button(
        label="📥 Download Result Card",
        data=result_card_data,
        file_name=f"Result_Card_{datetime.now().strftime('%H%M%S')}.txt",
        mime="text/plain"
    )

    # Review Section
    with st.expander("🔍 Review Incorrect Answers"):
        found_wrong = False
        for i, row in df.iterrows():
            u_ans = user_ans.get(i)
            c_ans = row['Correct Answer']
            if str(u_ans) != str(c_ans):
                found_wrong = True
                st.markdown(f"**Q{i+1}: {row['Question']}**")
                st.write(f"❌ Your Answer: {u_ans}")
                st.write(f"✅ Correct Answer: {c_ans}")
                st.write("---")
        if not found_wrong:
            st.write("No incorrect answers to show!")

    if st.button("🔄 Take Exam Again"):
        st.session_state.exam_started = False
        st.session_state.submitted = False
        st.session_state.end_time = None
        st.session_state.user_answers = {}
        # Reshuffle questions for new attempt
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
        st.rerun()

