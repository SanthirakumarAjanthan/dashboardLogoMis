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
   
""", unsafe_allow_html=True)

# Streamlit app layout
st.title("General Information Summary")

# Database connection
db_connection = connect_to_db()
if db_connection is None:
    st.error("Failed to connect to the database.")
else:
    cursor = db_connection.cursor()

    # Province selection
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    province_choice = st.sidebar.selectbox("Select Province", [name for _, name in provinces])
    selected_province_id = next(id for id, name in provinces if name == province_choice)

    # District selection
    cursor.execute("SELECT id, name FROM districts WHERE province_id = %s", (selected_province_id,))
    districts = cursor.fetchall()
    district_choice = st.sidebar.selectbox("Select District", [name for _, name in districts])
    selected_district_id = next(id for id, name in districts if name == district_choice)

    # Fetch all Local Authorities in the selected district
    cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s", (selected_district_id,))
    local_authorities = cursor.fetchall()

    # Year selection
    cursor.execute("SELECT DISTINCT year FROM local_authority_information WHERE local_authority_id IN (%s)" %
                   ','.join(['%s'] * len(local_authorities)),
                   tuple(id for id, _ in local_authorities))
    years = cursor.fetchall()
    year_choice = st.sidebar.selectbox("Select Year", [str(year[0]) for year in years])

    # Fetch all questions
    cursor.execute("SELECT id, question FROM questions")
    questions = cursor.fetchall()

    # Output table
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if district_choice and year_choice:
            local_authority_ids = [id for id, _ in local_authorities]
            format_strings_local_authorities = ','.join(['%s'] * len(local_authority_ids))
            format_strings_questions = ','.join(['%s'] * len(questions))

            cursor.execute(f"""
                SELECT q.id, q.question, lai.answer, p.name as province, d.name as district, la.name as local_authority
                FROM questions q
                JOIN local_authority_information lai ON q.id = lai.question_id
                JOIN local_authorities la ON lai.local_authority_id = la.id
                JOIN districts d ON la.district_id = d.id
                JOIN provinces p ON d.province_id = p.id
                WHERE la.id IN ({format_strings_local_authorities})
                AND lai.year = %s
            """, (*local_authority_ids, year_choice))
            combined_info = cursor.fetchall()

            if combined_info:
                data_combined = {"Province": [], "District": [], "Local Authority": []}

                for question_id, question, answer, province, district, local_authority in combined_info:
                    if local_authority not in data_combined["Local Authority"]:
                        data_combined["Province"].append(province)
                        data_combined["District"].append(district)
                        data_combined["Local Authority"].append(local_authority)

                    formatted_answer = format_answer(cursor, question_id, answer)
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

    cursor.close()
    db_connection.close()
