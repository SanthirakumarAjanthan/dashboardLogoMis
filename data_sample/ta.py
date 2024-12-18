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
st.title("LA_ANALYSIS Database Viewer")

# Sidebar to choose between viewing tables or staff data
view_option = st.sidebar.radio("Choose what to display", ("Tables", "Staff Data", "Combined Staff Table"))

if view_option == "Tables":
    # (Existing code to display tables...)
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

elif view_option == "Staff Data":
    # (Existing code to display staff data...)
    db_connection = connect_to_db()
    cursor = db_connection.cursor()

    st.subheader("Staff Types")
    cursor.execute("SELECT * FROM staff_types")
    staff_types = cursor.fetchall()
    staff_types_df = pd.DataFrame(staff_types, columns=[i[0] for i in cursor.description])
    st.write("Staff Types Data:")
    st.dataframe(staff_types_df)

    st.subheader("Local Authority Staff")
    cursor.execute("SELECT * FROM local_authority_staff")
    local_authority_staff = cursor.fetchall()
    local_authority_staff_df = pd.DataFrame(local_authority_staff, columns=[i[0] for i in cursor.description])
    st.write("Local Authority Staff Data:")
    st.dataframe(local_authority_staff_df)

    cursor.close()
    db_connection.close()

elif view_option == "Combined Staff Table":
    db_connection = connect_to_db()
    cursor = db_connection.cursor()

    # Fetch all provinces
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    provinces_df = pd.DataFrame(provinces, columns=["province_id", "province_name"])
    province_names = provinces_df['province_name'].tolist()

    # Select Province
    selected_province = st.sidebar.selectbox("Select a Province", province_names)
    if selected_province:
        province_id = int(provinces_df[provinces_df['province_name'] == selected_province]['province_id'].values[0])

        # Fetch districts in the selected province
        cursor.execute("SELECT id, name FROM districts WHERE province_id = %s", (province_id,))
        districts = cursor.fetchall()
        districts_df = pd.DataFrame(districts, columns=["district_id", "district_name"])
        district_names = districts_df['district_name'].tolist()

        # Select District
        selected_district = st.sidebar.selectbox("Select a District", district_names)
        if selected_district:
            district_id = int(districts_df[districts_df['district_name'] == selected_district]['district_id'].values[0])

            # Fetch local authorities in the selected district
            cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s", (district_id,))
            local_authorities = cursor.fetchall()
            local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])
            local_authority_names = local_authorities_df['local_authority_name'].tolist()

            # Select Local Authority
            selected_local_authority = st.sidebar.selectbox("Select a Local Authority", local_authority_names)
            if selected_local_authority:
                local_authority_id = int(local_authorities_df[local_authorities_df['local_authority_name'] == selected_local_authority]['local_authority_id'].values[0])

                # Fetch years available for the selected local authority
                cursor.execute("SELECT DISTINCT year FROM local_authority_information WHERE local_authority_id = %s", (local_authority_id,))
                years = cursor.fetchall()
                years_df = pd.DataFrame(years, columns=["year"])
                year_list = years_df['year'].tolist()

                # Select Year
                selected_year = st.sidebar.selectbox("Select a Year", year_list)
                if selected_year:
                    # Fetch data from staff_types
                    cursor.execute("SELECT id AS no, name AS staff_type FROM staff_types")
                    staff_types = cursor.fetchall()
                    staff_types_df = pd.DataFrame(staff_types, columns=["no", "staff_type"])

                    # Fetch data from local_authority_staff based on selected filters
                    query = """
                        SELECT approved_carder, available_carder, male, female
                        FROM local_authority_staff
                        WHERE local_authority_id = %s AND year = %s
                    """
                    cursor.execute(query, (local_authority_id, selected_year))
                    local_authority_staff = cursor.fetchall()
                    local_authority_staff_df = pd.DataFrame(local_authority_staff, columns=["approved_carder", "available_carder", "male", "female"])

                    # Combine data into a new DataFrame
                    combined_df = pd.concat([staff_types_df, local_authority_staff_df], axis=1)

                    # Display the combined DataFrame
                    st.subheader("Combined Staff Table")
                    st.write(f"Data for {selected_province} -> {selected_district} -> {selected_local_authority} ({selected_year})")
                    st.dataframe(combined_df)

    cursor.close()
    db_connection.close()
