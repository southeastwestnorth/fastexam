import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Science Exam Portal",
    page_icon="🔬",
    layout="centered"
)

# --- 2. CSS & JAVASCRIPT FOR TIMER ---
# We inject custom JS to handle the visual countdown so it doesn't freeze the Python UI
def display_timer(remaining_seconds):
    # Calculate minutes and seconds for the initial display
    mins, secs = divmod(int(remaining_seconds), 60)
    
    # HTML/JS for the timer
    timer_html = f"""
        <div style="
            position: fixed; 
            top: 60px; 
            right: 20px; 
            background-color: #ffeeba; 
            color: #856404; 
            padding: 10px 20px; 
            border-radius: 10px; 
            border: 1px solid #ffeeba; 
            font-weight: bold; 
            font-size: 20px; 
            z-index: 999; 
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);">
            ⏳ <span id="time">Loading...</span>
        </div>
        <script>
        var timeLeft = {remaining_seconds};
        var timerElement = document.getElementById('time');
        
        var countdown = setInterval(function() {{
            if (timeLeft <= 0) {{
                clearInterval(countdown);
                timerElement.innerHTML = "00:00";
            }} else {{
                var minutes = Math.floor(timeLeft / 60);
                var seconds = Math.floor(timeLeft % 60);
                seconds = seconds < 10 ? '0' + seconds : seconds;
                minutes = minutes < 10 ? '0' + minutes : minutes;
                timerElement.innerHTML = minutes + ":" + seconds;
                timeLeft--;
            }}
        }}, 1000);
        </script>
        """
    st.markdown(timer_html, unsafe_allow_html=True)

# Footer Styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #333;
        text-align: center;
        padding: 10px;
        font-weight: bold;
        border-top: 2px solid #007bff;
        z-index: 100;
    }
    .stRadio {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    <div class="footer">
        Developed for Students | Made by Imran
    </div>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING & STATE MANAGEMENT ---
def load_exam_data():
    try:
        # Check if we already have questions loaded in session to prevent reshuffling
        if 'questions_data' not in st.session_state:
            df = pd.read_csv("questions.csv")
            # Shuffle once and store in session state
            st.session_state.questions_data = df.sample(frac=1).reset_index(drop=True)
        return st.session_state.questions_data
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.warning("Make sure 'questions.csv' exists with columns: Question, Option A, Option B, Option C, Option D, Correct Answer")
        return None

# Initialize Session State Variables
if 'exam_started' not in st.session_state:
    st.session_state.exam_started = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'end_time' not in st.session_state:
    st.session_state.end_time = 0

# Load Data
df = load_exam_data()

# --- 4. REPORT GENERATION ---
def generate_report(score, total, user_answers, df):
    report_text = f"SCIENCE EXAM PORTAL - RESULT CARD\n"
    report_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report_text += f"------------------------------------------------\n"
    report_text += f"FINAL SCORE: {score} / {total} ({score/total*100:.1f}%)\n"
    report_text += f"------------------------------------------------\n\n"
    report_text += "REVIEW OF INCORRECT ANSWERS:\n\n"

    wrong_count = 0
    for i, row in df.iterrows():
        u_ans = user_answers.get(i)
        c_ans = row['Correct Answer']
        
        if u_ans != c_ans:
            wrong_count += 1
            report_text += f"Q{i+1}: {row['Question']}\n"
            report_text += f"   [X] Your Answer: {u_ans if u_ans else 'No Answer'}\n"
            report_text += f"   [V] Correct Answer: {c_ans}\n"
            report_text += "-" * 40 + "\n"
    
    if wrong_count == 0:
        report_text += "Great job! No incorrect answers found."

    return report_text

# --- 5. MAIN LOGIC ---

if df is not None:
    total_qs = len(df)
    time_limit_secs = total_qs * 60  # 1 Minute per Question

    st.title("🧪 Science Model Test")
    
    # --- START PAGE ---
    if not st.session_state.exam_started and not st.session_state.submitted:
        st.write("### Instructions:")
        st.info(f"📋 **Total Questions:** {total_qs}")
        st.info(f"⏳ **Duration:** {total_qs} Minutes (Auto-calculated)")
        st.warning("⚠️ Do not refresh the page during the exam, or you will lose your progress.")
        
        if st.button("🚀 Start Exam Now", type="primary"):
            st.session_state.exam_started = True
            # Set the END time based on current server time
            st.session_state.end_time = time.time() + time_limit_secs
            st.rerun()

    # --- EXAM PAGE ---
    elif st.session_state.exam_started and not st.session_state.submitted:
        # Calculate Remaining Time (Server Side)
        remaining = st.session_state.end_time - time.time()
        
        # 1. Check if time is up
        if remaining <= 0:
            st.session_state.submitted = True
            st.session_state.exam_started = False
            st.error("Time is up! Processing results...")
            st.rerun()
        
        # 2. Display Visual Timer (Client Side JS)
        display_timer(remaining)
        
        # 3. Exam Form
        with st.form("exam_form"):
            user_answers = {}
            for i, row in df.iterrows():
                st.write(f"**Q{i+1}. {row['Question']}**")
                options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
                
                user_answers[i] = st.radio(
                    f"Select answer for Question {i+1}", 
                    options, 
                    index=None, 
                    key=f"q{i}", 
                    label_visibility="collapsed"
                )
                st.write("") # Spacer
            
            # Submit Button
            submitted = st.form_submit_button("✅ Submit Exam")
            
            if submitted:
                # Double check time upon submission
                if time.time() > st.session_state.end_time:
                    st.error("Submission rejected. Time limit exceeded.")
                    st.session_state.submitted = True
                    st.session_state.exam_started = False
                    st.rerun()
                else:
                    st.session_state.user_results = user_answers
                    st.session_state.submitted = True
                    st.session_state.exam_started = False
                    st.rerun()

    # --- RESULT PAGE ---
    elif st.session_state.submitted:
        st.header("📊 Exam Result")
        
        score = 0
        results_data = st.session_state.get('user_results', {})
        
        # Calculate Score
        for i, row in df.iterrows():
            if results_data.get(i) == row['Correct Answer']:
                score += 1
        
        perc = (score / total_qs) * 100
        
        # Display Score
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Score", f"{score} / {total_qs}")
        with col2:
            st.metric("Percentage", f"{perc:.1f}%")
            
        # Feedback Messages
        if perc >= 80: st.success("Grade: Excellent! 🌟")
        elif perc >= 40: st.warning("Grade: Passed 👍")
        else: st.error("Grade: Fail - Needs more practice 📚")

        # GENERATE REPORT FOR DOWNLOAD
        report_data = generate_report(score, total_qs, results_data, df)
        
        st.download_button(
            label="📥 Download Result Card (.txt)",
            data=report_data,
            file_name="science_exam_result.txt",
            mime="text/plain"
        )

        st.divider()
        st.subheader("Review Incorrect Answers")
        
        # On-screen review
        count_wrong = 0
        for i, row in df.iterrows():
            u_ans = results_data.get(i)
            c_ans = row['Correct Answer']
            
            if u_ans != c_ans:
                count_wrong += 1
                with st.expander(f"❌ Q{i+1}: {row['Question'][:50]}..."):
                    st.write(f"**Question:** {row['Question']}")
                    st.error(f"Your Answer: {u_ans}")
                    st.success(f"Correct Answer: {c_ans}")
        
        if count_wrong == 0:
            st.balloons()
            st.info("Perfect Score! No errors to review.")
        
        if st.button("🔄 Retry Exam"):
            # Clear state to restart
            for key in ['exam_started', 'submitted', 'user_results', 'questions_data', 'end_time']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
