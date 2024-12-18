import mysql.connector
import pandas as pd
import streamlit as st

# Function to connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

# Streamlit app layout
st.set_page_config(page_title="LA_ANALYSIS Database Viewer", layout="wide")

st.title("LA_ANALYSIS Database Viewer")

# Sidebar for Province selection
db_connection = connect_to_db()
cursor = db_connection.cursor()

# Fetch and display provinces
cursor.execute("SELECT id, name FROM provinces")
provinces = cursor.fetchall()
provinces_df = pd.DataFrame(provinces, columns=["province_id", "province_name"])
province_names = provinces_df['province_name'].tolist()
selected_province = st.sidebar.selectbox("Select a Province", province_names)

if selected_province:
    # Convert numpy.int64 to int
    province_id = int(provinces_df.loc[provinces_df['province_name'] == selected_province, 'province_id'].values[0])

    # Fetch and display districts based on selected province
    cursor.execute("SELECT id, name FROM districts WHERE province_id = %s", (province_id,))
    districts = cursor.fetchall()
    districts_df = pd.DataFrame(districts, columns=["district_id", "district_name"])
    district_names = districts_df['district_name'].tolist()
    selected_district = st.sidebar.selectbox("Select a District", district_names)

    if selected_district:
        # Convert numpy.int64 to int
        district_id = int(districts_df.loc[districts_df['district_name'] == selected_district, 'district_id'].values[0])

        # Fetch and display local authorities based on selected district
        cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s", (district_id,))
        local_authorities = cursor.fetchall()
        local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])
        local_authority_names = local_authorities_df['local_authority_name'].tolist()
        selected_local_authority = st.sidebar.selectbox("Select a Local Authority", local_authority_names)

        if selected_local_authority:
            # Convert numpy.int64 to int
            local_authority_id = int(local_authorities_df.loc[local_authorities_df['local_authority_name'] == selected_local_authority, 'local_authority_id'].values[0])

            # Fetch and display available years for the selected local authority
            cursor.execute("SELECT DISTINCT year FROM gnds WHERE local_authority_id = %s ORDER BY year DESC", (local_authority_id,))
            years = cursor.fetchall()
            years_df = pd.DataFrame(years, columns=["year"])
            year_list = years_df['year'].tolist()
            selected_year = st.sidebar.selectbox("Select a Year", year_list)

            if selected_year:
                # Fetch and display data from gnds based on selected filters
                cursor.execute("""
                    SELECT gnd_name, gnd_number, population
                    FROM gnds
                    WHERE local_authority_id = %s AND year = %s
                """, (local_authority_id, selected_year))
                
                gnds = cursor.fetchall()
                gnds_df = pd.DataFrame(gnds, columns=["GND Name", "GND Number", "Population"])

                # Display the results
                st.subheader(f"GND Data for {selected_province} -> {selected_district} -> {selected_local_authority} ({selected_year})")
                st.dataframe(gnds_df, use_container_width=True)

cursor.close()
db_connection.close()
