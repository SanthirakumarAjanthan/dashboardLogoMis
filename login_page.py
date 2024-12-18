import streamlit as st

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"  # Default page is Home

# Define a function to change pages
def navigate_to(page_name):
    st.session_state.page = page_name

# Handle page navigation
if st.session_state.page == "Home":
    # Set the page title
    st.title("Home")

    # Add navigation buttons at the top
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("LoGoMIS"):
            navigate_to("LoGoMIS")
    with col2:
        if st.button("PERFECT 2.0"):
            navigate_to("PERFECT 2.0")

elif st.session_state.page == "LoGoMIS":
    st.title("LoGoMIS")
    
    # Create columns for grouping buttons side by side
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("General Info"):
            st.write("Displaying General Info...")
        if st.button("Staff summary"):
            st.write("Displaying Staff summary...")
        if st.button("Vehicle summary"):
            st.write("Displaying Vehicle summary...")
        if st.button("Actual this month"):
            st.write("Displaying Actual this month...")
    
    with col2:
        if st.button("Actual Upto this month"):
            st.write("Displaying Actual Upto this month...")
        if st.button("Budget status"):
            st.write("Displaying Budget status...")
        if st.button("Own revenue vs Expenditure"):
            st.write("Displaying Own revenue vs Expenditure...")
        if st.button("Total revenue vs Expenditure"):
            st.write("Displaying Total revenue vs Expenditure...")
    
    with col3:
        if st.button("Additional revenue summary"):
            st.write("Displaying Additional revenue summary...")
        if st.button("Actual summary"):
            st.write("Displaying Actual summary...")

    # Add button to navigate to the LoGoMIS Dashboard
    if st.button("Go to Data Mapping Dashboard"):
        navigate_to("LoGoMIS Dashboard")
    if st.button("Back to Home"):
        navigate_to("Home")

elif st.session_state.page == "PERFECT 2.0":
    st.title("PERFECT 2.0")
    st.markdown("""
    **Data Mapping**  
    -----------------------------------  
    """)
    
    # Add buttons for Data Mapping options
    if st.button("Availability status report"):
        st.write("Displaying Availability status report...")
    if st.button("Response summary"):
        st.write("Displaying Response summary...")
    if st.button("Value summary"):
        st.write("Displaying Value summary...")
    if st.button("District Average summary"):
        st.write("Displaying District Average summary...")
    if st.button("Scoring summary (response base & calculation base)"):
        st.write("Displaying Scoring summary...")

    # Add button to navigate to the PERFECT 2.0 Dashboard
    if st.button("Go to Data Mapping Dashboard"):
        navigate_to("PERFECT 2.0 Dashboard")
    if st.button("Back to Home"):
        navigate_to("Home")

elif st.session_state.page == "LoGoMIS Dashboard":
    st.title("LoGoMIS Dashboard")
    st.write("Welcome to the LoGoMIS Data Mapping Dashboard!")
    if st.button("Back to Home"):
        navigate_to("Home")

elif st.session_state.page == "PERFECT 2.0 Dashboard":
    st.title("PERFECT 2.0 Dashboard")
    st.write("Welcome to the PERFECT 2.0 Data Mapping Dashboard!")
    
    # Add buttons for the dashboard-specific functionality
    if st.button("Availability status report"):
        st.write("Displaying Availability status report on the Dashboard...")
    if st.button("Response summary"):
        st.write("Displaying Response summary on the Dashboard...")
    if st.button("Value summary"):
        st.write("Displaying Value summary on the Dashboard...")
    if st.button("District Average summary"):
        st.write("Displaying District Average summary on the Dashboard...")
    if st.button("Scoring summary (response base & calculation base)"):
        st.write("Displaying Scoring summary on the Dashboard...")

    # Navigation to Home
    if st.button("Back to Home"):
        navigate_to("Home")
