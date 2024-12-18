import mysql.connector
import pandas as pd
import streamlit as st
import os
from PIL import Image
from graphviz import Digraph

# Function to connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

# Function to retrieve data from a table
def load_data(table_name):
    db_connection = connect_to_db()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, db_connection)
    db_connection.close()
    return df

# Function to retrieve schema of a table
def get_table_schema(table_name):
    db_connection = connect_to_db()
    cursor = db_connection.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    schema = cursor.fetchall()
    cursor.close()
    db_connection.close()
    return schema

# Function to retrieve all foreign key relationships
def get_foreign_keys():
    db_connection = connect_to_db()
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT
            TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE
            REFERENCED_TABLE_SCHEMA = 'LA_ANALYSIS'
            AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    foreign_keys = cursor.fetchall()
    cursor.close()
    db_connection.close()
    return foreign_keys

# Function to generate the ER diagram
def generate_er_diagram():
    foreign_keys = get_foreign_keys()
    dot = Digraph(comment='ER Diagram', format='png')
    
    tables = set()
    
    for fk in foreign_keys:
        table, column, ref_table, ref_column = fk
        dot.node(table, table)
        dot.node(ref_table, ref_table)
        dot.edge(f"{table}:{column}", f"{ref_table}:{ref_column}", label=f"{column} -> {ref_column}")
        tables.add(table)
        tables.add(ref_table)
    
    for table in tables:
        if not dot.node(table):
            dot.node(table, table)
    
    diagram_path = 'er_diagram'
    dot.render(diagram_path, view=False)
    return diagram_path + ".png"

# Streamlit app layout
st.title("LA_ANALYSIS Database Viewer")

# Retrieve and display all tables
db_connection = connect_to_db()
cursor = db_connection.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
cursor.close()
db_connection.close()

if tables:
    # Sidebar for table selection
    st.sidebar.title("Table Selector")
    selected_table = st.sidebar.selectbox("Select a Table", [table[0] for table in tables])
   
    if selected_table:
        # Display the schema of the selected table in the sidebar
        st.sidebar.subheader(f"Schema for Table: {selected_table}")
        schema = get_table_schema(selected_table)
        schema_df = pd.DataFrame(schema, columns=["Field", "Type", "Null", "Key", "Default", "Extra"])
        st.sidebar.dataframe(schema_df)
       
        # Load and display the data from the selected table
        st.subheader(f"Data from Table: {selected_table}")
        data = load_data(selected_table)
        st.dataframe(data)
    
    # Display ER Diagram
    st.subheader("ER Diagram of the Database")
    diagram_path = generate_er_diagram()
    st.image(diagram_path, use_column_width=True)
