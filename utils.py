import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def apply_custom_css():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .footer {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background-color: #f1f1f1 !important; color: #333 !important; 
            text-align: center; padding: 10px; font-weight: bold; 
            border-top: 2px solid #007bff; z-index: 100;
        }
        
        .stRadio[data-testid="stWidgetLabel"] p {
            font-size: 18px !important; font-weight: bold !important; color: #4da3ff !important;
        }

        .q-text {
            font-size: 1.1rem; font-weight: 500; margin-top: 20px; color: white;
        }
        </style>
        <div class="footer">Made by Imran</div>
        """, unsafe_allow_html=True)

def render_timer(seconds_left):
    timer_html = f"""
    <div style="background-color: #ffeb3b; padding: 10px; border-radius: 10px; text-align: center; border: 3px solid #f44336; box-shadow: 0px 4px 6px rgba(0,0,0,0.3);">
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
        timerDisplay.innerHTML = (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds < 10 ? "0" + seconds : seconds);
        
        if (timeLeft <= 0) {{
            parentDoc.querySelector('button[kind="primary"]').click();
        }} else {{
            timeLeft--;
            setTimeout(updateTimer, 1000);
        }}
    }}
    updateTimer();

    function removeRadioFocus() {{
        let activeEl = parentDoc.activeElement;
        if (activeEl && activeEl.tagName.toLowerCase() === 'input' && activeEl.type === 'radio') {{
            activeEl.blur(); 
        }}
    }}
    parentDoc.addEventListener('wheel', removeRadioFocus, {{passive: true}});
    parentDoc.addEventListener('touchmove', removeRadioFocus, {{passive: true}});
    </script>
    """
    with st.sidebar:
        st.markdown("### ⏲️ Exam Clock")
        components.html(timer_html, height=100)

def generate_result_txt(score, total, df, user_answers):
    report = f"--- FAST EXAM RESULT CARD ---\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"Final Score: {score} / {total} ({round(score/total*100, 1)}%)\n-------------------------------------------\n\n"
    report += "REVIEW OF INCORRECT ANSWERS:\n\n"
    
    incorrect_found = False
    for i, row in df.iterrows():
        ans = user_answers.get(i)
        if str(ans) != str(row['Correct Answer']):
            incorrect_found = True
            report += f"Q{i+1}: {row['Question']}\n   - Your Answer: {ans if ans else 'None'}\n   - Correct Answer: {row['Correct Answer']}\n{'-'*40}\n"
            
    if not incorrect_found: report += "PERFECT SCORE! No errors found."
    return report
