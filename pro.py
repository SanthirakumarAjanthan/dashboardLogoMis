import streamlit as st
import mysql.connector
import pandas as pd

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="170.64.176.75",
    user="ajanthan",
    password="Abcd@9920",
    database="LA_ANALYSIS"
)
cursor = conn.cursor()

# Sidebar filters
st.sidebar.title("Filters")

# Step 1: Select Provinces
cursor.execute("SELECT id, name FROM provinces")
provinces = cursor.fetchall()
province_choices = st.sidebar.multiselect("Select Provinces", [name for _, name in provinces])

# Step 2: Select Districts based on selected provinces
district_choices = []
if province_choices:
    selected_provinces_ids = [id for id, name in provinces if name in province_choices]
    format_strings = ','.join(['%s'] * len(selected_provinces_ids))
    cursor.execute(f"SELECT id, name FROM districts WHERE province_id IN ({format_strings})", tuple(selected_provinces_ids))
    districts = cursor.fetchall()
    district_choices = st.sidebar.multiselect("Select Districts", [name for _, name in districts])

# Step 3: Select Local Authorities based on selected districts
local_authority_choices = []
if district_choices:
    selected_districts_ids = [id for id, name in districts if name in district_choices]
    format_strings = ','.join(['%s'] * len(selected_districts_ids))
    cursor.execute(f"SELECT id, name FROM local_authorities WHERE district_id IN ({format_strings})", tuple(selected_districts_ids))
    local_authorities = cursor.fetchall()
    local_authority_choices = st.sidebar.multiselect("Select Local Authorities", [name for _, name in local_authorities])

# Step 4: Select Year based on the local_authority_information table
year_choices = []
if local_authority_choices:
    selected_local_authorities_ids = [id for id, name in local_authorities if name in local_authority_choices]
    format_strings = ','.join(['%s'] * len(selected_local_authorities_ids))
    cursor.execute(f"SELECT DISTINCT year FROM local_authority_information WHERE local_authority_id IN ({format_strings})", tuple(selected_local_authorities_ids))
    years = cursor.fetchall()
    year_choices = st.sidebar.multiselect("Select Year", [str(year[0]) for year in years])

# Step 5: Select Questions based on the questions table
questions_choices = []
if year_choices:
    cursor.execute("SELECT id, question FROM questions")
    questions = cursor.fetchall()
    questions_choices = st.sidebar.multiselect("Select General Questions", [question for _, question in questions])

# Step 6: Select Staff Types from staff_types table
staff_type_choices = []
if local_authority_choices:
    cursor.execute("SELECT id, name FROM staff_types")
    staff_types = cursor.fetchall()
    staff_type_choices = st.sidebar.multiselect("Select Staff Types", [name for _, name in staff_types])

# Main content area
st.title("Local Authority Data Display")

# Container for data display
with st.container():
    # Query and display General Questions data
    if questions_choices:
        selected_questions_ids = [id for id, question in questions if question in questions_choices]
        format_strings_local_authorities = ','.join(['%s'] * len(selected_local_authorities_ids))
        format_strings_questions = ','.join(['%s'] * len(selected_questions_ids))
        
        query = f"""
        SELECT p.name AS Province, d.name AS District, la.name AS Local_Authority, q.question AS General_Questions, lai.answer AS Answer
        FROM local_authority_information lai
        JOIN local_authorities la ON lai.local_authority_id = la.id
        JOIN districts d ON la.district_id = d.id
        JOIN provinces p ON d.province_id = p.id
        JOIN questions q ON lai.question_id = q.id
        WHERE lai.local_authority_id IN ({format_strings_local_authorities})
        AND lai.year IN ({','.join(['%s'] * len(year_choices))})
        AND lai.question_id IN ({format_strings_questions})
        """
        
        cursor.execute(query, tuple(selected_local_authorities_ids + year_choices + selected_questions_ids))
        data = cursor.fetchall()

        if data:
            st.subheader("General Information")
            df = pd.DataFrame(data, columns=["Province", "District", "Local Authority", "General Questions", "Answer"])
            st.dataframe(df)
        else:
            st.write("No data found for the selected General Questions filters.")
    
    # Query and display Staff Details data
    if staff_type_choices:
        selected_staff_types_ids = [id for id, name in staff_types if name in staff_type_choices]
        format_strings_local_authorities = ','.join(['%s'] * len(selected_local_authorities_ids))
        format_strings_staff_types = ','.join(['%s'] * len(selected_staff_types_ids))
        
        query = f"""
        SELECT p.name AS Province, d.name AS District, la.name AS Local_Authority, st.name AS Staff_Type, las.approved_carder, las.available_carder, las.male, las.female
        FROM local_authority_staff las
        JOIN local_authorities la ON las.local_authority_id = la.id
        JOIN districts d ON la.district_id = d.id
        JOIN provinces p ON d.province_id = p.id
        JOIN staff_types st ON las.staff_type_id = st.id
        WHERE las.local_authority_id IN ({format_strings_local_authorities})
        AND las.staff_type_id IN ({format_strings_staff_types})
        """
        
        cursor.execute(query, tuple(selected_local_authorities_ids + selected_staff_types_ids))
        staff_data = cursor.fetchall()

        if staff_data:
            st.subheader("Staff Details")
            df_staff = pd.DataFrame(staff_data, columns=["Province", "District", "Local Authority", "Staff Type", "Approved Carder", "Available Carder", "Male", "Female"])
            st.dataframe(df_staff)
        else:
            st.write("No data found for the selected Staff Types filters.")

# Close the database connection
cursor.close()
conn.close()
