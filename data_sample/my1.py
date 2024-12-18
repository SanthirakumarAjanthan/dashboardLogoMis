import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# Function to connect to the MySQL database using SQLAlchemy
def connect_to_db():
    engine = create_engine('mysql+mysqlconnector://ajanthan:Abcd@9920@170.64.176.75/LA_ANALYSIS')
    return engine

# Corrected SQLAlchemy connection string
def connect_to_db():
    engine = create_engine('mysql+mysqlconnector://ajanthan:Abcd@9920@170.64.176.75/LA_ANALYSIS')
    return engine

# Function to retrieve data from a table
def load_data(table_name):
    engine = connect_to_db()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, engine)
    return df

# Function to retrieve schema of a table
def get_table_schema(table_name):
    engine = connect_to_db()
    query = f"DESCRIBE {table_name}"
    schema = pd.read_sql(query, engine)
    return schema

# Streamlit app layout
st.title("LA_ANALYSIS Database Viewer")

# Retrieve and display all local authorities
local_authorities_df = load_data('local_authorities')

if not local_authorities_df.empty:
    # Sidebar for selecting a local authority
    st.sidebar.title("Local Authority Selector")
    selected_authority = st.sidebar.selectbox("Select a Local Authority", local_authorities_df['name'])
    
    if selected_authority:
        # Get the selected local authority ID
        authority_id = local_authorities_df[local_authorities_df['name'] == selected_authority]['id'].values[0]
        
        # Query the staff data related to the selected local authority
        query = f"""
        SELECT 
            la.name AS local_authority,
            st.name AS staff_type,
            las.approved_carder,
            las.available_carder,
            las.male,
            las.female
        FROM 
            local_authority_staff las
        JOIN 
            local_authorities la ON las.local_authority_id = la.id
        JOIN 
            staff_types st ON las.staff_type_id = st.id
        WHERE
            la.id = {authority_id}
        """
        
        # Load the data into a DataFrame and display it
        staff_data = pd.read_sql(query, connect_to_db())
        
        st.subheader(f"Staff Data for {selected_authority}")
        st.dataframe(staff_data)
