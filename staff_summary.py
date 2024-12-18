import mysql.connector
import streamlit as st
import pandas as pd

# Function to connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

# Custom CSS to increase table width and make Province, District, Local Authority columns sticky
st.markdown("""
    <style>
    .reportview-container .main .block-container{
        padding: 2rem;
    }
    table {
        width: 100% !important;
        border-collapse: collapse;
    }
    th, td {
        padding: 10px;
        text-align: left;
        border: 1px solid #ddd;
    }
    thead th {
        background-color: darkblue;
        color: white;
        position: sticky;
        top: 0;
        z-index: 2;
    }
    .sticky-column {
        position: sticky;
        left: 0;
        background-color: white;
        z-index: 1;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit app layout
st.title("Staff Details Summary")

# Connect to the database
db_connection = connect_to_db()
if db_connection is None:
    st.error("Failed to connect to the database.")
else:
    cursor = db_connection.cursor()

    # Sidebar: Select Province
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    province_choices = st.sidebar.selectbox("Select Province", [name for _, name in provinces])

    # Sidebar: Select District based on selected Province
    cursor.execute(f"SELECT id, name FROM districts WHERE province_id = (SELECT id FROM provinces WHERE name = %s)", (province_choices,))
    districts = cursor.fetchall()
    district_choices = st.sidebar.selectbox("Select District", [name for _, name in districts])

    # Sidebar: Select Year based on selected Local Authority
    cursor.execute(f"SELECT DISTINCT year FROM local_authority_information WHERE local_authority_id IN (SELECT id FROM local_authorities WHERE district_id = (SELECT id FROM districts WHERE name = %s))", (district_choices,))
    years = cursor.fetchall()
    year_choices = st.sidebar.selectbox("Select Year", [str(year[0]) for year in years])

    # Fetch all Local Authorities based on the selected District
    cursor.execute(f"SELECT id, name FROM local_authorities WHERE district_id = (SELECT id FROM districts WHERE name = %s)", (district_choices,))
    local_authorities = cursor.fetchall()

    # Query to fetch staff details for all Local Authorities in the selected district and province
    query = f"""
        SELECT p.name AS Province, 
               d.name AS District, 
               la.name AS Local_Authority, 
               st.name AS Staff_Type, 
               las.approved_carder, 
               las.available_carder, 
               las.male, 
               las.female
        FROM local_authority_staff las
        JOIN local_authorities la ON las.local_authority_id = la.id
        JOIN districts d ON la.district_id = d.id
        JOIN provinces p ON d.province_id = p.id
        JOIN staff_types st ON las.staff_type_id = st.id
        WHERE p.name = %s AND d.name = %s AND las.year = %s
    """

    cursor.execute(query, (province_choices, district_choices, year_choices))
    staff_data = cursor.fetchall()

    if staff_data:
        # Create a DataFrame from the staff data
        df_staff = pd.DataFrame(staff_data, columns=["Province", "District", "Local Authority", "Staff Type", "Approved Carder", "Available Carder", "Male", "Female"])
        
        # Pivot the DataFrame to have separate columns for Approved Carder and Available Carder for each Staff Type
        df_staff_pivot = df_staff.pivot_table(index=["Province", "District", "Local Authority"],
                                              columns="Staff Type",
                                              values=["Approved Carder", "Available Carder"],
                                              aggfunc="first").reset_index()

        # Flatten the multi-index column headers for easier access
        df_staff_pivot.columns = [' '.join(col).strip() for col in df_staff_pivot.columns.values]

        # Add CSS class for sticky columns (Province, District, Local Authority)
        df_staff_pivot_html = df_staff_pivot.to_html(classes=["table", "table-striped", "table-bordered"], escape=False)

        # Inject CSS to make the columns sticky
        df_staff_pivot_html = df_staff_pivot_html.replace('<table', '<table style="width:100%" class="table table-striped table-bordered" id="staff_table"')
        df_staff_pivot_html = df_staff_pivot_html.replace("<thead>", "<thead><tr>")
        df_staff_pivot_html = df_staff_pivot_html.replace("</thead>", "</thead><tr>")

        # Make first three columns sticky using custom class
        df_staff_pivot_html = df_staff_pivot_html.replace('<td class="data column">', '<td class="sticky-column">')

        st.markdown(df_staff_pivot_html, unsafe_allow_html=True)
    else:
        st.write("No staff data available.")

    cursor.close()
    db_connection.close()
