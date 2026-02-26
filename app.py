import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime
from utils import apply_custom_css, render_timer, generate_result_txt
from database import save_result
from auth import require_login

st.set_page_config(page_title="FastExam", page_icon="🔬", layout="centered")
apply_custom_css()
require_login()

if 'exam_started' not in st.session_state: st.session_state.exam_started = False
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'end_time' not in st.session_state: st.session_state.end_time = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}

try:
    if 'questions' not in st.session_state:
        df = pd.read_csv("questions.csv")
        st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    df = st.session_state.questions
except:
    st.error("CSV file missing.")
    st.stop()

total_qs = len(df)
time_limit_secs = total_qs * 60

if not st.session_state.exam_started and not st.session_state.submitted:
    st.title(f"Welcome, {st.session_state.student_name}")
    with st.expander("🎮 Play Rock-Paper-Scissors"):
        c = st.columns(3)
        choice = None
        if c[0].button("Rock"): choice = "Rock"
        if c[1].button("Paper"): choice = "Paper"
        if c[2].button("Scissors"): choice = "Scissors"
        if choice: st.write(f"Computer chose {random.choice(['Rock', 'Paper', 'Scissors'])}!")

    if st.button("🚀 Start Exam", use_container_width=True, type="primary"):
        st.session_state.end_time = time.time() + time_limit_secs
        st.session_state.exam_started = True
        st.rerun()

elif st.session_state.exam_started and not st.session_state.submitted:
    rem = int(st.session_state.end_time - time.time())
    if rem <= 0:
        st.session_state.submitted = True
        st.session_state.exam_started = False
        st.rerun()
    render_timer(rem)
    with st.form("exam"):
        u_ans = {}
        for i, r in df.iterrows():
            st.markdown(f"<div class='q-text'>Q{i+1}. {r['Question']}</div>", unsafe_allow_html=True)
            u_ans[i] = st.radio("Ans:", [r['Option A'], r['Option B'], r['Option C'], r['Option D']], index=None, key=f"q{i}", label_visibility="collapsed")
        if st.form_submit_button("Submit Exam", type="primary", use_container_width=True):
            st.session_state.user_answers = u_ans
            st.session_state.submitted = True
            st.session_state.exam_started = False
            score = sum(1 for i, r in df.iterrows() if str(u_ans.get(i)) == str(r['Correct Answer']))
            save_result(st.session_state.student_name, score, total_qs, (score/total_qs)*100, datetime.now().strftime("%Y-%m-%d %H:%M"))
            st.rerun()

elif st.session_state.submitted:
    st.title("📊 Results")
    u_ans = st.session_state.user_answers
    score = sum(1 for i, r in df.iterrows() if str(u_ans.get(i)) == str(r['Correct Answer']))
    st.subheader(f"Score: {score}/{total_qs} ({round(score/total_qs*100,1)}%)")
    st.download_button("📥 Download Result Card", data=generate_result_txt(score, total_qs, df, u_ans), file_name="Result.txt")
    if st.button("Restart"):
        for k in ['exam_started','submitted','end_time','user_answers','questions','student_name']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()
