import streamlit as st

def show():
    st.title("General Info - LogoMis")
    st.markdown("### Welcome to the General Info Page!")
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.experimental_rerun()

