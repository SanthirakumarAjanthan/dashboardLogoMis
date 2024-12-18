import mysql.connector
import streamlit as st
import pandas as pd

# Function to connect to the MySQL database
def connect_to_db():
    try:
        return mysql.connector.connect(
            host="170.64.176.75",
            user="ajanthan",
            password="Abcd@9920",
            database="LA_ANALYSIS"
        )
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Example variable for selecting the view option
view_option = st.sidebar.selectbox("Select View", ["Vehicle Information"])

if view_option == "Vehicle Information":
    db_connection = connect_to_db()
    if db_connection is None:
        st.error("Failed to connect to the database.")
    else:
        cursor = db_connection.cursor()

        # Province Selection
        cursor.execute("SELECT id, name FROM provinces")
        provinces = cursor.fetchall()
        province_options = {name: id for id, name in provinces}
        selected_province = st.sidebar.selectbox("Select Province", list(province_options.keys()))

        # District Selection based on Province
        if selected_province:
            province_id = province_options[selected_province]
            cursor.execute(f"SELECT id, name FROM districts WHERE province_id = {province_id}")
            districts = cursor.fetchall()
            district_options = {name: id for id, name in districts}
            selected_district = st.sidebar.selectbox("Select District", list(district_options.keys()))

        # Accounting Year Selection
        selected_year = st.sidebar.selectbox("Select Accounting Year", range(2022, 2025))

        # Vehicle Status Selection
        vehicle_status = st.sidebar.selectbox("Select Vehicle Status", ["Running", "Not Running", "Both"])

        st.title("Vehicles Summary")

        if selected_district and vehicle_status:
            district_id = district_options[selected_district]

            # Query to fetch vehicle information with dynamic column naming
            if vehicle_status == "Both":
                # Fetch both Running and Not Running counts
                cursor.execute(f"""
                    SELECT la.name AS local_authority,
                           vt.name AS vehicle_type,
                           COALESCE(lav.running, 0) AS running_count,
                           COALESCE(lav.not_running, 0) AS not_running_count
                    FROM local_authorities la
                    JOIN vehicle_types vt
                    LEFT JOIN local_authority_vehicles lav
                    ON vt.id = lav.vehicle_type_id
                    AND lav.local_authority_id = la.id
                    AND lav.year = {selected_year}
                    WHERE la.district_id = {district_id}
                """)
                # Expect 4 columns: local_authority, vehicle_type, running_count, not_running_count
                vehicles_info = cursor.fetchall()

            else:
                # Fetch only the selected status (Running or Not Running)
                status_column = "running" if vehicle_status == "Running" else "not_running"
                cursor.execute(f"""
                    SELECT la.name AS local_authority,
                           vt.name AS vehicle_type,
                           COALESCE(lav.{status_column}, 0) AS status_count
                    FROM local_authorities la
                    JOIN vehicle_types vt
                    LEFT JOIN local_authority_vehicles lav
                    ON vt.id = lav.vehicle_type_id
                    AND lav.local_authority_id = la.id
                    AND lav.year = {selected_year}
                    WHERE la.district_id = {district_id}
                """)
                # Expect 3 columns: local_authority, vehicle_type, status_count
                vehicles_info = cursor.fetchall()

            if vehicles_info:
                # Group the data by local authority and vehicle type, creating a dictionary of counts
                grouped_data = {}
                for record in vehicles_info:
                    if vehicle_status == "Both":
                        # Handle case for Both (4 columns)
                        local_authority, vehicle_type, running_count, not_running_count = record
                        if local_authority not in grouped_data:
                            grouped_data[local_authority] = {}
                        grouped_data[local_authority][f"{vehicle_type} Running"] = running_count
                        grouped_data[local_authority][f"{vehicle_type} Not Running"] = not_running_count
                    else:
                        # Handle case for either Running or Not Running (3 columns)
                        local_authority, vehicle_type, status_count = record
                        if local_authority not in grouped_data:
                            grouped_data[local_authority] = {}
                        grouped_data[local_authority][f"{vehicle_type} {vehicle_status}"] = status_count

                # Create the DataFrame with dynamic columns
                local_authorities = list(grouped_data.keys())
                vehicle_types = set(vt for data in grouped_data.values() for vt in data.keys())

                # Construct the column names (Local Authority + Vehicle Type + Status)
                columns = ["Local Authority"] + list(vehicle_types)

                # Prepare data for the DataFrame
                table_data = []
                for local_authority in local_authorities:
                    row = [local_authority]
                    for vehicle_type in vehicle_types:
                        row.append(grouped_data[local_authority].get(vehicle_type, 0))
                    table_data.append(row)

                # Create DataFrame
                df = pd.DataFrame(table_data, columns=columns)
                st.dataframe(df)
            else:
                st.write(f"No vehicle information available for {vehicle_status.lower()}.")

        cursor.close()
        db_connection.close()
else:
    st.write("Please select an option to view.")
