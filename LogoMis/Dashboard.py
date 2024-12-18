import streamlit as st

def dashboard_page():
    st.set_page_config(page_title="Dashboard", layout="wide")
    
    # Topbar with two buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("LogoMis")
    with col2:
        st.button("Perfect2.0")
    
    # Dashboard content
    st.title("Welcome to the Dashboard")
    st.write("This is the main page after login.")
