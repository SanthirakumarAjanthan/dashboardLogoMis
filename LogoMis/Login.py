import streamlit as st

def login_page():
    st.title("Login")
    st.markdown("""
        <style>
        body {
            background-color: #f0f2f6;
        }
        div.stButton > button {
            color: white;
            background-color: #6c63ff;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #5a52d1;
        }
        </style>
    """, unsafe_allow_html=True)


    # Input fields
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")

    # Login button
    if st.button("Login"):
        if username == "admin@gmail.com" and password == "Admin@123":
            st.success("Login successful!")
            # Set authentication state
            st.session_state.authenticated = True
            # Reload the app to navigate to the dashboard
            st.experimental_set_query_params(logged_in="true")
        else:
            st.error("Invalid username or password")
