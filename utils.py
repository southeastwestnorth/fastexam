import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def apply_custom_css():
    st.markdown("""
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        .footer {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background-color: #f1f1f1 !important; color: #333 !important; 
            text-align: center; padding: 10px; font-weight: bold; 
            border-top: 2px solid #007bff; z-index: 100;
        }
        .stRadio [data-testid="stWidgetLabel"] p {
            font-size: 18px !important; font-weight: bold !important; color: #4da3ff !important;
        }
        .q-text { font-size: 1.1rem; font-weight: 500; margin-top: 20px; color: white; }
        </style>
        <div class="footer">Made by Imran</div>
        """, unsafe_allow_html=True)

def render_timer(seconds_left):
    timer_html = f"""
    <div style="background-color:#ffeb3b; padding:10px; border-radius:10px; text-align:center; border:3px solid #f44336;">
        <span style="font-size:24px; font-weight:bold; color:black;">⏳ <span id="time">--:--</span></span>
    </div>
    <script>
    var timeLeft = {seconds_left};
    var timerDisplay = document.getElementById('time');
    var parentDoc = window.parent.document;
    function updateTimer() {{
        var mins = Math.floor(timeLeft / 60);
        var secs = timeLeft % 60;
        timerDisplay.innerHTML = (mins < 10 ? "0" : "") + mins + ":" + (secs < 10 ? "0" : "") + secs;
        if (timeLeft <= 0) {{ parentDoc.querySelector('button[kind="primary"]').click(); }} 
        else {{ timeLeft--; setTimeout(updateTimer, 1000); }}
    }}
    updateTimer();
    function removeRadioFocus() {{
        let el = parentDoc.activeElement;
        if (el && el.tagName.toLowerCase() === 'input' && el.type === 'radio') {{ el.blur(); }}
    }}
    parentDoc.addEventListener('wheel', removeRadioFocus, {{passive: true}});
    parentDoc.addEventListener('touchmove', removeRadioFocus, {{passive: true}});
    </script>
    """
    with st.sidebar:
        components.html(timer_html, height=100)

def generate_result_txt(score, total, df, user_answers):
    report = f"--- FAST EXAM RESULT CARD ---\n"
    report += f"Final Score: {score} / {total} ({round(score/total*100, 1)}%)\n\n"
    report += "REVIEW OF INCORRECT ANSWERS:\n" + "-"*30 + "\n"
    for i, row in df.iterrows():
        ans = user_answers.get(i)
        if str(ans) != str(row['Correct Answer']):
            report += f"Q: {row['Question']}\n - Your Answer: {ans}\n - Correct Answer: {row['Correct Answer']}\n\n"
    return report
