import mysql.connector
import pandas as pd
import streamlit as st

# Function to connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="abinaya",
        password="Abcd@901928",
        database="LA_ANALYSIS"
    )

# Streamlit app layout
st.title("LA_ANALYSIS Database Viewer")

# Sidebar to choose between viewing tables or staff data
view_option = st.sidebar.radio("Choose what to display", ("Tables"))

if view_option == "Tables":
    # Display tables in the database
    db_connection = connect_to_db()
    cursor = db_connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    db_connection.close()

    table_names = [table[0] for table in tables]

    selected_table = st.sidebar.selectbox("Select a table to view", table_names)

    if selected_table:
        st.subheader(f"Table: {selected_table}")

        db_connection = connect_to_db()
        cursor = db_connection.cursor()
        cursor.execute(f"DESCRIBE {selected_table}")
        schema = cursor.fetchall()
        schema_df = pd.DataFrame(schema, columns=["Field", "Type", "Null", "Key", "Default", "Extra"])
        st.write("Schema:")
        st.dataframe(schema_df)

        data = pd.read_sql(f"SELECT * FROM {selected_table}", db_connection)
        st.write("Data:")
        st.dataframe(data)

        cursor.close()
        db_connection.close()


    cursor.close()
    db_connection.close()
