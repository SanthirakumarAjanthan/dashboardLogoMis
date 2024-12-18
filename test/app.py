import streamlit as st
from LogoMis import GeneralSummary, StaffSummary, VeichleSummary, BudgetStatus
from Perfect20 import mappingDB

# Login Functionality
def login():
    st.title("Login Page")
    st.markdown("### Enter your credentials")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    if st.button("Login"):
        if username == "admin@gmail.com" and password == "Admin@123":
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Dashboard Functionality
def dashboard():
    st.title("Dashboard")
    st.markdown("### Select an Option")

    col1, col2 = st.columns(2)
    with col1:
        button1 = st.button("LogoMis")
    with col2:
        button2 = st.button("Perfect20")

    # Navigate to specific pages
    if button1:
        st.session_state.page = "LogoMis"
        st.experimental_rerun()
    elif button2:
        st.session_state.page = "Perfect20"
        st.experimental_rerun()

# Main Application Logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if not st.session_state.logged_in:
    login()
else:
    if st.session_state.page == "dashboard":
        dashboard()
    elif st.session_state.page == "LogoMis":
        GeneralSummary.show()
    elif st.session_state.page == "LogoMis":
        StaffSummary.show()
    elif st.session_state.page == "LogoMis":
        VeichleSummary.show()
    elif st.session_state.page == "LogoMis":
        BudgetStatus.show()
    elif st.session_state.page == "Perfect20":
        mappingDB.show()