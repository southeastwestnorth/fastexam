import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# This connects to the Google Sheet defined in your Streamlit Secrets
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def init_db():
    # With Google Sheets, the sheet itself is the DB. 
    # Just ensure you have a sheet with headers: 
    # student_name, score, total, percentage, date
    pass

def save_result(name, score, total, percentage, date):
    conn = get_conn()
    # Fetch existing data
    try:
        existing_data = conn.read(worksheet="Sheet1")
    except:
        existing_data = pd.DataFrame(columns=["student_name", "score", "total", "percentage", "date"])
    
    # Add new row
    new_row = pd.DataFrame([{
        "student_name": name,
        "score": score,
        "total": total,
        "percentage": percentage,
        "date": date
    }])
    
    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
    
    # Write back to Google Sheets
    conn.update(worksheet="Sheet1", data=updated_df)

def get_all_results():
    conn = get_conn()
    return conn.read(worksheet="Sheet1")
