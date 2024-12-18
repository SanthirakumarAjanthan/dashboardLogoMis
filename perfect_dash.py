import mysql.connector
import streamlit as st
import pandas as pd

# Database connection function
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="vaitheki",
        password="Abcd@878172",
        database="PERFECT20"
    )

# Function to fetch all table names from the database
def get_table_names():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return [table[0] for table in tables]

# Function to fetch table schema (column names and data types)
def get_table_schema(table_name):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    schema = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(schema, columns=["Field", "Type", "Null", "Key", "Default", "Extra"])

# Function to fetch data from a selected table
def get_table_data(table_name):
    conn = connect_to_db()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Streamlit UI
def main():
    st.title("Database Table Viewer")

    # Get list of table names
    tables = get_table_names()
   
    # Create a select box for users to choose a table
    table_name = st.selectbox("Select a table", tables)
   
    if table_name:
        # Display the schema of the selected table
        st.subheader(f"Schema of {table_name}")
        table_schema = get_table_schema(table_name)
        st.dataframe(table_schema)
       
        # Display the selected table's content
        st.subheader(f"Data from {table_name}")
        table_data = get_table_data(table_name)
        st.dataframe(table_data)

if __name__ == "__main__":
    main()