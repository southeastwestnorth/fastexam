import streamlit as st
import pandas as pd
import time
from datetime import datetime
import streamlit.components.v1 as components
import random

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FastExam",
    page_icon="🔬",
    layout="centered"
)

# --- 2. CSS STYLING (Forcing Visibility for Dark Mode) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Force Light background for Footer to contrast with black */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f1f1f1 !important; color: #333 !important; 
        text-align: center; padding: 10px; font-weight: bold; 
        border-top: 2px solid #007bff; z-index: 100;
    }
    
    /* Styling Radio Buttons for readability */
    .stRadio[data-testid="stWidgetLabel"] p {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #4da3ff !important;
    }

    /* Fixing question text visibility */
    .q-text {
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 20px;
        color: white;
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
if 'game_result' not in st.session_state:
    st.session_state.game_result = ""

# --- 4. DATA LOADING ---
if 'questions' not in st.session_state:
    try:
        df = pd.read_csv("questions.csv")
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    except:
        st.error("Error: 'questions.csv' not found.")
        st.stop()

# --- 5. ROBUST TIMER LOGIC (WITH SCROLL FIX) ---
def render_timer(seconds_left):
    timer_html = f"""
    <div style="
        background-color: #ffeb3b; 
        padding: 10px; 
        border-radius: 10px; 
        text-align: center; 
        border: 3px solid #f44336;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
    ">
        <span style="font-size: 24px; font-weight: bold; color: black; font-family: sans-serif;">
            ⏳ <span id="time">--:--</span>
        </span>
    </div>

    <script>
    var timeLeft = {seconds_left};
    var timerDisplay = document.getElementById('time');
    var parentDoc = window.parent.document;
    
    function updateTimer() {{
        var minutes = Math.floor(timeLeft / 60);
        var seconds = timeLeft % 60;
        
        timerDisplay.innerHTML = (minutes < 10 ? "0" + minutes : minutes) + ":" + 
                                 (seconds < 10 ? "0" + seconds : seconds);
        
        if (timeLeft <= 0) {{
            // Force submit by finding the primary button in the parent window
            parentDoc.querySelector('button[kind="primary"]').click();
        }} else {{
            timeLeft--;
            setTimeout(updateTimer, 1000);
        }}
    }}
    updateTimer();

    // --- SCROLL FIX: Prevent scroll wheel/swipes from changing radio buttons ---
    function removeRadioFocus() {{
        let activeEl = parentDoc.activeElement;
        if (activeEl && activeEl.tagName.toLowerCase() === 'input' && activeEl.type === 'radio') {{
            activeEl.blur(); // Instantly removes focus to stop accidental switching
        }}
    }}
    
    parentDoc.addEventListener('wheel', removeRadioFocus, {{passive: true}});
    parentDoc.addEventListener('touchmove', removeRadioFocus, {{passive: true}});
    // --------------------------------------------------------------------------
    </script>
    """
    with st.sidebar:
        st.markdown("### ⏲️ Exam Clock")
        components.html(timer_html, height=100)

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
            report += f"Q{i+1}: {row['Question']}\n"
            report += f"   - Your Answer: {ans if ans else 'None'}\n"
            report += f"   - Correct Answer: {row['Correct Answer']}\n"
            report += f"{'-'*40}\n"
            
    if not incorrect_found:
        report += "PERFECT SCORE! No errors found."
        
    return report

# --- 7. APP LOGIC ---
df = st.session_state.questions
total_qs = len(df)
time_limit_secs = total_qs * 60  # Auto calculate 1 min per question

st.title("FastExam")

# SCREEN: START
if not st.session_state.exam_started and not st.session_state.submitted:
    st.info(f"📋 Questions: **{total_qs}** | ⏳ Time: **{total_qs} Minutes**")
    
    # --- MINI GAME ADDED HERE ---
    with st.expander("🎮 Warm-up Mini Game: Rock-Paper-Scissors", expanded=False):
        st.write("Take a deep breath and play a quick game against the computer before you start!")
        
        choices =['🪨 Rock', '📄 Paper', '✂️ Scissors']
        cols = st.columns(3)
        
        def play_rps(user_choice):
            bot_choice = random.choice(choices)
            if user_choice == bot_choice:
                st.session_state.game_result = f"Computer chose {bot_choice}. It's a Tie! 🤝"
            elif (user_choice == '🪨 Rock' and bot_choice == '✂️ Scissors') or \
                 (user_choice == '📄 Paper' and bot_choice == '🪨 Rock') or \
                 (user_choice == '✂️ Scissors' and bot_choice == '📄 Paper'):
                st.session_state.game_result = f"Computer chose {bot_choice}. You Win! 🎉"
            else:
                st.session_state.game_result = f"Computer chose {bot_choice}. You Lose! 😢"

        with cols[0]:
            if st.button("🪨 Rock", use_container_width=True): play_rps('🪨 Rock')
        with cols[1]:
            if st.button("📄 Paper", use_container_width=True): play_rps('📄 Paper')
        with cols[2]:
            if st.button("✂️ Scissors", use_container_width=True): play_rps('✂️ Scissors')
            
        if st.session_state.game_result:
            if "Win" in st.session_state.game_result:
                st.success(st.session_state.game_result)
            elif "Lose" in st.session_state.game_result:
                st.error(st.session_state.game_result)
            else:
                st.info(st.session_state.game_result)
    # ----------------------------

    st.write("") # Spacer
    if st.button("🚀 Start Exam Now", use_container_width=True, type="primary"):
        st.session_state.end_time = time.time() + time_limit_secs
        st.session_state.exam_started = True
        st.rerun()

# SCREEN: EXAM
elif st.session_state.exam_started and not st.session_state.submitted:
    # Check current time
    remaining = int(st.session_state.end_time - time.time())
    
    if remaining <= 0:
        st.session_state.submitted = True
        st.session_state.exam_started = False
        st.rerun()

    # Call the fixed timer
    render_timer(remaining)

    with st.form("exam_form"):
        temp_answers = {}
        for i, row in df.iterrows():
            st.markdown(f"<div class='q-text'>Q{i+1}. {row['Question']}</div>", unsafe_allow_html=True)
            options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
            temp_answers[i] = st.radio("Select:", options, index=None, key=f"q{i}", label_visibility="collapsed")
            st.write("---")
        
        # Primary button used by JS for auto-submit
        if st.form_submit_button("Submit Exam", type="primary", use_container_width=True):
            st.session_state.user_answers = temp_answers
            st.session_state.submitted = True
            st.session_state.exam_started = False
            st.rerun()

# SCREEN: RESULTS
elif st.session_state.submitted:
    st.header("📊 Exam Statistics")
    
    score = 0
    u_ans = st.session_state.user_answers
    for i, row in df.iterrows():
        if str(u_ans.get(i)) == str(row['Correct Answer']):
            score += 1
            
    perc = (score / total_qs) * 100
    st.subheader(f"Final Score: {score} / {total_qs} ({perc:.1f}%)")
    
    # Download Card
    result_txt = generate_result_txt(score, total_qs, df, u_ans)
    st.download_button(
        label="📥 Download Detailed Result Card",
        data=result_txt,
        file_name="FastExam_Result.txt",
        mime="text/plain"
    )

    # Detailed Review for wrong ones
    with st.expander("🔍 Click to review your mistakes"):
        for i, row in df.iterrows():
            if str(u_ans.get(i)) != str(row['Correct Answer']):
                st.error(f"**Q{i+1}: {row['Question']}**")
                st.write(f"❌ Your Answer: {u_ans.get(i)}")
                st.success(f"✅ Right Answer: {row['Correct Answer']}")
                st.divider()

    if st.button("🔄 Try Again"):
        for key in['exam_started', 'submitted', 'end_time', 'user_answers', 'questions', 'game_result']:
            if key in st.session_state: del st.session_state[key]
        st.rerun()
