import mysql.connector
import streamlit as st
import pandas as pd
import json

# Function to connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

# Function to get option text by question_id and option_id
def get_option_text(cursor, question_id, option_id):
    cursor.execute(f"""
        SELECT `option`
        FROM question_options
        WHERE question_id = {question_id}
        AND id = {option_id}
    """)
    option = cursor.fetchone()
    return option[0] if option else None

# Function to format answers based on their type
def format_answer(cursor, question_id, answer):
    try:
        answer_dict = json.loads(answer)
        if isinstance(answer_dict, dict):
            return {get_option_text(cursor, question_id, key): value for key, value in answer_dict.items()}
    except (json.JSONDecodeError, TypeError):
        return answer
    return answer

# Function to equalize the length of all lists in the data dictionary
def equalize_lengths(data):
    max_length = max(len(lst) for lst in data.values())
    for key in data:
        while len(data[key]) < max_length:
            data[key].append(None)

# Custom CSS to increase table width and fit it fully on the page
st.markdown("""
    <style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    table {
        width: 100% !important;
    }
    thead th {
        background-color: darkblue;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit app layout
st.title("General Information Summary")

# Step 1: Select Provinces
db_connection = connect_to_db()
if db_connection is None:
    st.error("Failed to connect to the database.")
else:
    cursor = db_connection.cursor()

    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    province_choices = st.sidebar.multiselect("Select Provinces", [name for _, name in provinces])

    district_choices = []
    if province_choices:
        selected_provinces_ids = [id for id, name in provinces if name in province_choices]
        format_strings = ','.join(['%s'] * len(selected_provinces_ids))
        cursor.execute(f"SELECT id, name FROM districts WHERE province_id IN ({format_strings})", tuple(selected_provinces_ids))
        districts = cursor.fetchall()
        district_choices = st.sidebar.multiselect("Select Districts", [name for _, name in districts])

    local_authority_choices = []
    if district_choices:
        selected_districts_ids = [id for id, name in districts if name in district_choices]
        format_strings = ','.join(['%s'] * len(selected_districts_ids))
        cursor.execute(f"SELECT id, name FROM local_authorities WHERE district_id IN ({format_strings})", tuple(selected_districts_ids))
        local_authorities = cursor.fetchall()
        local_authority_choices = st.sidebar.multiselect("Select Local Authorities", [name for _, name in local_authorities])

    year_choices = []
    if local_authority_choices:
        selected_local_authorities_ids = [id for id, name in local_authorities if name in local_authority_choices]
        format_strings = ','.join(['%s'] * len(selected_local_authorities_ids))
        cursor.execute(f"SELECT DISTINCT year FROM local_authority_information WHERE local_authority_id IN ({format_strings})", tuple(selected_local_authorities_ids))
        years = cursor.fetchall()
        year_choices = st.sidebar.multiselect("Select Year", [str(year[0]) for year in years])

    questions_choices = []
    if year_choices:
        cursor.execute("SELECT id, question FROM questions")
        questions = cursor.fetchall()
        questions_dict = {question: id for id, question in questions}
        questions_choices = st.sidebar.multiselect("Select General Questions", [question for question in questions_dict])

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if local_authority_choices and year_choices and questions_choices:
            selected_local_authorities_ids = [id for id, name in local_authorities if name in local_authority_choices]
            selected_questions_ids = [questions_dict[question] for question in questions_choices]

            format_strings = ','.join(['%s'] * len(selected_local_authorities_ids))
            format_strings_questions = ','.join(['%s'] * len(selected_questions_ids))
            cursor.execute(f"""
                SELECT q.id, q.question, lai.answer, p.name as province, d.name as district, la.name as local_authority
                FROM questions q
                JOIN local_authority_information lai ON q.id = lai.question_id
                JOIN local_authorities la ON lai.local_authority_id = la.id
                JOIN districts d ON la.district_id = d.id
                JOIN provinces p ON d.province_id = p.id
                WHERE la.id IN ({format_strings})
                AND lai.year IN ({','.join(['%s'] * len(year_choices))})
                AND q.id IN ({format_strings_questions})
            """, tuple(selected_local_authorities_ids + year_choices + selected_questions_ids))
            combined_info = cursor.fetchall()

            if combined_info:
                data_combined = {"Province": [], "District": [], "Local Authority": []}
                seen_local_authorities = set()

                for question_id, question, answer, province, district, local_authority in combined_info:
                    formatted_answer = format_answer(cursor, question_id, answer)

                    if local_authority not in seen_local_authorities:
                        data_combined["Province"].append(province)
                        data_combined["District"].append(district)
                        data_combined["Local Authority"].append(local_authority)
                        seen_local_authorities.add(local_authority)

                    if isinstance(formatted_answer, dict):
                        for key, value in formatted_answer.items():
                            column_header = f"{question} - {key}"
                            if column_header not in data_combined:
                                data_combined[column_header] = []
                            data_combined[column_header].append(value)
                    else:
                        if question not in data_combined:
                            data_combined[question] = []
                        data_combined[question].append(formatted_answer)

                equalize_lengths(data_combined)
                df_combined = pd.DataFrame(data_combined)

                # Display the DataFrame in full width
                st.write(df_combined)
            else:
                st.write("No data available.")

    # Staff Type selection
    cursor.execute("SELECT id, name FROM staff_types")
    staff_types = cursor.fetchall()
    staff_type_choices = st.sidebar.multiselect("Select Staff Types", [name for _, name in staff_types])

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
            st.subheader("Staff Details Summary")

            df_staff = pd.DataFrame(staff_data, columns=["Province", "District", "Local Authority", "Staff Type", "Approved Carder", "Available Carder", "Male", "Female"])
            df_staff_pivot = df_staff.pivot_table(index=["Province", "District", "Local Authority"],
                                                  columns="Staff Type",
                                                  values=["Approved Carder", "Available Carder", "Male", "Female"],
                                                  aggfunc="first").reset_index()
            df_staff_pivot.columns = [' '.join(col).strip() for col in df_staff_pivot.columns.values]
            st.write(df_staff_pivot)
        else:
            st.write("No staff data available.")
   
    cursor.close()
    db_connection.close()