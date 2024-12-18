import streamlit as st
from Login import login_page
from Dashboard import dashboard_page

# Page navigation
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_page()
else:
    dashboard_page()
