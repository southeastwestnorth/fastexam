import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime
from utils import apply_custom_css, render_timer, generate_result_txt
from database import init_db, save_result
from auth import require_login

# 1. Config & Setup
st.set_page_config(page_title="FastExam", page_icon="🔬", layout="centered")
apply_custom_css()
init_db() # Ensure DB is created
require_login() # Ask for Student Name

# 2. Session State
if 'exam_started' not in st.session_state: st.session_state.exam_started = False
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'end_time' not in st.session_state: st.session_state.end_time = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'game_result' not in st.session_state: st.session_state.game_result = ""

# 3. Load Data
if 'questions' not in st.session_state:
    try:
        df = pd.read_csv("questions.csv")
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    except:
        st.error("Teacher Notice: 'questions.csv' is missing. Please upload it via the Admin panel.")
        st.stop()

df = st.session_state.questions
total_qs = len(df)
time_limit_secs = total_qs * 60

st.title(f"FastExam - {st.session_state.student_name}")

# --- START SCREEN ---
if not st.session_state.exam_started and not st.session_state.submitted:
    st.info(f"📋 Questions: **{total_qs}** | ⏳ Time: **{total_qs} Minutes**")
    
    with st.expander("🎮 Warm-up: Rock-Paper-Scissors", expanded=False):
        choices =['🪨 Rock', '📄 Paper', '✂️ Scissors']
        cols = st.columns(3)
        def play_rps(u_choice):
            b_choice = random.choice(choices)
            if u_choice == b_choice: st.session_state.game_result = f"Computer chose {b_choice}. Tie! 🤝"
            elif (u_choice=='🪨 Rock' and b_choice=='✂️ Scissors') or (u_choice=='📄 Paper' and b_choice=='🪨 Rock') or (u_choice=='✂️ Scissors' and b_choice=='📄 Paper'):
                st.session_state.game_result = f"Computer chose {b_choice}. You Win! 🎉"
            else: st.session_state.game_result = f"Computer chose {b_choice}. You Lose! 😢"

        with cols[0]: 
            if st.button("🪨 Rock", use_container_width=True): play_rps('🪨 Rock')
        with cols[1]: 
            if st.button("📄 Paper", use_container_width=True): play_rps('📄 Paper')
        with cols[2]: 
            if st.button("✂️ Scissors", use_container_width=True): play_rps('✂️ Scissors')
            
        if st.session_state.game_result: st.write(st.session_state.game_result)

    if st.button("🚀 Start Exam Now", use_container_width=True, type="primary"):
        st.session_state.end_time = time.time() + time_limit_secs
        st.session_state.exam_started = True
        st.rerun()

# --- EXAM SCREEN ---
elif st.session_state.exam_started and not st.session_state.submitted:
    remaining = int(st.session_state.end_time - time.time())
    if remaining <= 0:
        st.session_state.submitted = True
        st.session_state.exam_started = False
        st.rerun()

    render_timer(remaining)

    with st.form("exam_form"):
        temp_answers = {}
        for i, row in df.iterrows():
            st.markdown(f"<div class='q-text'>Q{i+1}. {row['Question']}</div>", unsafe_allow_html=True)
            options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]
            temp_answers[i] = st.radio("Select:", options, index=None, key=f"q{i}", label_visibility="collapsed")
            st.write("---")
        
        if st.form_submit_button("Submit Exam", type="primary", use_container_width=True):
            st.session_state.user_answers = temp_answers
            st.session_state.submitted = True
            st.session_state.exam_started = False
            
            # --- SAVE TO DATABASE ---
            score = sum(1 for i, row in df.iterrows() if str(temp_answers.get(i)) == str(row['Correct Answer']))
            save_result(st.session_state.student_name, score, total_qs, (score/total_qs)*100, datetime.now().strftime("%Y-%m-%d %H:%M"))
            st.rerun()

# --- RESULT SCREEN ---
elif st.session_state.submitted:
    st.header("📊 Exam Statistics")
    score = sum(1 for i, row in df.iterrows() if str(st.session_state.user_answers.get(i)) == str(row['Correct Answer']))
    perc = (score / total_qs) * 100
    st.subheader(f"Final Score: {score} / {total_qs} ({perc:.1f}%)")
    
    st.download_button("📥 Download Detailed Result Card", data=generate_result_txt(score, total_qs, df, st.session_state.user_answers), file_name="FastExam_Result.txt", mime="text/plain")

    with st.expander("🔍 Click to review your mistakes"):
        for i, row in df.iterrows():
            if str(st.session_state.user_answers.get(i)) != str(row['Correct Answer']):
                st.error(f"**Q{i+1}: {row['Question']}**")
                st.write(f"❌ Your Answer: {st.session_state.user_answers.get(i)}")
                st.success(f"✅ Right Answer: {row['Correct Answer']}")
                st.divider()

    if st.button("🔄 Restart"):
        for key in['exam_started', 'submitted', 'end_time', 'user_answers', 'questions', 'game_result', 'student_name']:
            if key in st.session_state: del st.session_state[key]
        st.rerun()
