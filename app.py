import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Science Exam Portal", page_icon="🔬")

# --- 2. STYLING ---
st.markdown("""
    <style>
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f1f1f1; color: #333; text-align: center;
        padding: 10px; font-weight: bold; border-top: 2px solid #007bff;
    }
    .stRadio > label { font-size: 18px; font-weight: bold; color: #1E3A8A; }
    </style>
    <div class="footer">Developed for Students | Made by Imran</div>
    """, unsafe_allow_html=True)

# --- 3. DATA PERSISTENCE ---
@st.cache_data
def get_questions():
    try:
        # Load and shuffle once
        df = pd.read_csv("questions.csv")
        return df.sample(frac=1).reset_index(drop=True)
    except:
        st.error("Please ensure 'questions.csv' is in the same folder.")
        return None

# --- 4. TIMER & SESSION INITIALIZATION ---
if 'exam_active' not in st.session_state:
    st.session_state.exam_active = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'end_time' not in st.session_state:
    st.session_state.end_time = None
if 'questions' not in st.session_state:
    st.session_state.questions = get_questions()

# --- 5. RESULT CARD GENERATOR ---
def create_result_card(score, total, user_ans, df):
    perc = (score / total) * 100
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    card = f"--- SCIENCE EXAM RESULT CARD ---\n"
    card += f"Date: {timestamp}\n"
    card += f"Final Score: {score}/{total} ({perc:.1f}%)\n"
    card += f"Status: {'PASSED' if perc >= 40 else 'FAILED'}\n"
    card += f"{'='*35}\n\n"
    
    card += "INCORRECT QUESTIONS REVIEW:\n"
    wrong_found = False
    for i, row in df.iterrows():
        u_ans = user_ans.get(i)
        c_ans = str(row['Correct Answer'])
        if str(u_ans) != c_ans:
            wrong_found = True
            card += f"Q{i+1}: {row['Question']}\n"
            card += f"   - Your Answer: {u_ans}\n"
            card += f"   - Correct Answer: {c_ans}\n"
            card += f"{'-'*20}\n"
    
    if not wrong_found:
        card += "Congratulations! You got everything correct."
        
    return card

# --- 6. APP LOGIC ---
df = st.session_state.questions

if df is not None:
    total_qs = len(df)
    duration_secs = total_qs * 60  # Auto-calculate: 1 min per question

    # --- SCREEN 1: START PAGE ---
    if not st.session_state.exam_active and not st.session_state.submitted:
        st.title("🧪 Science Model Test")
        st.info(f"📋 Total Questions: {total_qs}")
        st.info(f"⏳ Time Allotted: {total_qs} Minutes")
        
        if st.button("🚀 Start Exam"):
            st.session_state.end_time = time.time() + duration_secs
            st.session_state.exam_active = True
            st.rerun()

    # --- SCREEN 2: EXAM IN PROGRESS ---
    elif st.session_state.exam_active and not st.session_state.submitted:
        # Calculate remaining time
        current_time = time.time()
        remaining = st.session_state.end_time - current_time
        
        # Auto-submit if time is up
        if remaining <= 0:
            st.session_state.submitted = True
            st.session_state.exam_active = False
            st.error("Time is up! Auto-submitting...")
            st.rerun()

        # Display Timer in Sidebar
        mins, secs = divmod(int(remaining), 60)
        st.sidebar.header("⏳ Timer")
        st.sidebar.subheader(f"{mins:02d}:{secs:02d}")
        if remaining < 60:
            st.sidebar.warning("Less than 1 minute left!")

        # Exam Form (Using form prevents reruns on every radio click)
        with st.form("quiz_form"):
            st.title("Exam in Progress")
            user_answers = {}
            
            for i, row in df.iterrows():
                st.write(f"**Q{i+1}. {row['Question']}**")
                options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
                user_answers[i] = st.radio(f"Select answer for Q{i+1}:", options, index=None, key=f"ans_{i}")
                st.write("---")
            
            submit_clicked = st.form_submit_button("Submit Exam")
            
            if submit_clicked:
                st.session_state.final_answers = user_answers
                st.session_state.submitted = True
                st.session_state.exam_active = False
                st.rerun()

    # --- SCREEN 3: RESULT PAGE ---
    elif st.session_state.submitted:
        st.title("📊 Exam Results")
        
        score = 0
        ans_data = st.session_state.get('final_answers', {})
        
        for i, row in df.iterrows():
            if str(ans_data.get(i)) == str(row['Correct Answer']):
                score += 1
        
        perc = (score / total_qs) * 100
        st.subheader(f"Your Score: {score} / {total_qs} ({perc:.1f}%)")
        
        # Result Card Download
        result_text = create_result_card(score, total_qs, ans_data, df)
        st.download_button(
            label="📥 Download Result Card",
            data=result_text,
            file_name="exam_result.txt",
            mime="text/plain"
        )
        
        # UI Review
        with st.expander("Review My Wrong Answers"):
            for i, row in df.iterrows():
                u_ans = ans_data.get(i)
                c_ans = row['Correct Answer']
                if str(u_ans) != str(c_ans):
                    st.error(f"**Q{i+1}: {row['Question']}**")
                    st.write(f"Your Answer: {u_ans}")
                    st.write(f"Correct Answer: {c_ans}")
                    st.write("---")

        if st.button("🔄 Restart Exam"):
            for key in ['exam_active', 'submitted', 'end_time', 'questions', 'final_answers']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
