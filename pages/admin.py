import streamlit as st
import pandas as pd
from database import get_all_results
from utils import apply_custom_css

st.set_page_config(page_title="Teacher Dashboard", icon="🔒")
apply_custom_css()

st.title("👨‍🏫 Teacher Dashboard")

password = st.text_input("Enter Admin Password", type="password")
if password != "1234": 
    st.warning("Please enter the password.")
    st.stop()

tab1, tab2 = st.tabs(["📊 Student Scores", "📁 Update Questions"])

with tab1:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
    
    df_scores = get_all_results()
    st.dataframe(df_scores, use_container_width=True)

with tab2:
    uploaded_file = st.file_uploader("Upload questions.csv", type=["csv"])
    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        new_df.to_csv("questions.csv", index=False)
        st.success("Exam updated! (Note: Restart app to see changes)")
