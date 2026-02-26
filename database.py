import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def save_result(name, score, total, percentage, date):
    conn = get_conn()
    
    # 1. READ LATEST DATA (ttl=0 avoids using old cached data)
    try:
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        existing_data = existing_data.dropna(how='all')
    except:
        existing_data = pd.DataFrame(columns=["student_name", "score", "total", "percentage", "date"])
    
    # 2. CREATE NEW RECORD
    new_row = pd.DataFrame([{
        "student_name": str(name),
        "score": int(score),
        "total": int(total),
        "percentage": round(float(percentage), 2),
        "date": str(date)
    }])
    
    # 3. APPEND (Don't overwrite)
    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
    
    # 4. UPDATE GOOGLE SHEET
    conn.update(worksheet="Sheet1", data=updated_df)
    st.cache_data.clear()

def get_all_results():
    conn = get_conn()
    return conn.read(worksheet="Sheet1", ttl=0)
