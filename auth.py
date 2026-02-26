import streamlit as st

def require_login():
    """Forces the student to enter their name before seeing the exam."""
    if 'student_name' not in st.session_state:
        st.session_state.student_name = None
        
    if not st.session_state.student_name:
        st.markdown("### 🎓 Welcome to FastExam Portal")
        name = st.text_input("Please enter your Full Name to begin:")
        
        if st.button("Login & Continue", type="primary"):
            if name.strip():
                st.session_state.student_name = name.strip()
                st.rerun()
            else:
                st.error("Name cannot be empty.")
        st.stop() # Stops the rest of the app from running until logged in
