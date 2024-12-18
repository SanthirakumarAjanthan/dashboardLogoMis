import mysql.connector
import streamlit as st
import pandas as pd
import json

# Function to connect to the MySQL database
def connect_to_db():
    try:
        return mysql.connector.connect(
            host="170.64.176.75",
            user="vaitheki",
            password="Abcd@878172",
            database="LA_ANALYSIS"
        )
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Example variable for selecting the view option; update this with your actual implementation
view_option = st.sidebar.selectbox("Select View", ["General_Info", "Other_Option"])

# Check if the view option is "General_Info"
if view_option == "General_Info":
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

        # Local Authority Selection based on District
        if selected_district:
            district_id = district_options[selected_district]
            cursor.execute(f"SELECT id, name FROM local_authorities WHERE district_id = {district_id}")
            local_authorities = cursor.fetchall()
            local_authority_options = {name: id for id, name in local_authorities}
            selected_local_authority = st.sidebar.selectbox("Select Local Authority", list(local_authority_options.keys()))

        # Accounting Year Selection
        selected_year = st.sidebar.selectbox("Select Accounting Year", range(2022, 2025))

        st.title("Local Authority Information")

        # Function to get option text by question_id and option_id
        def get_option_text(question_id, option_id):
            cursor.execute(f"""
                SELECT `option`
                FROM question_options
                WHERE question_id = {question_id}
                AND id = {option_id}
            """)
            option = cursor.fetchone()
            return option[0] if option else None

        # Function to format answers based on their type
        def format_answer(question_id, answer):
            try:
                # Check if answer is JSON formatted
                answer_dict = json.loads(answer)
                if isinstance(answer_dict, dict):
                    # Return a list of tuples (label, value) for separate display
                    return [(get_option_text(question_id, int(key)), value) for key, value in answer_dict.items()]
            except (json.JSONDecodeError, TypeError):
                # Handle case where answer is not JSON or is a different type
                return [(None, str(answer))]

            return [(None, str(answer))]

        # Function to create a styled HTML box for answers
        def styled_box(content):
            return f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin: 5px 0;
                background-color: #f9f9f9;">
                {content}
            </div>
            """

        # Part A: General Information
        st.header("Part A: General Information")

        if selected_local_authority:
            cursor.execute(f"""
                SELECT q.id, q.question, lai.answer
                FROM questions q
                JOIN local_authority_information lai ON q.id = lai.question_id
                WHERE lai.local_authority_id = {local_authority_options[selected_local_authority]}
                AND lai.year = {selected_year}
                AND q.id BETWEEN 1 AND 12
            """)
            general_info = cursor.fetchall()

            if general_info:
                for question_id, question, answer in general_info:
                    answers = format_answer(question_id, answer)

                    # Create two columns for question and answers
                    col1, col2 = st.columns([2, 3])

                    with col1:
                        st.write(f"{question}:")

                    with col2:
                        # Display each label and value in separate cells
                        for label, value in answers:
                            label_html = styled_box(f"{label}") if label else ""
                            value_html = styled_box(value)
                            st.markdown(f"""
                            <div style="display: flex;">
                                <div style="flex: 1;">{label_html}</div>
                                <div style="flex: 1;">{value_html}</div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.write("No data available for General Information.")

        # Part B: Infrastructure Information
        st.header("Part B: Service Related Assets and Infrastructure of LAs")

        if selected_local_authority:
            cursor.execute(f"""
                SELECT q.id, q.question, lai.answer
                FROM questions q
                JOIN local_authority_information lai ON q.id = lai.question_id
                WHERE lai.local_authority_id = {local_authority_options[selected_local_authority]}
                AND lai.year = {selected_year}
                AND q.id BETWEEN 13 AND 35
            """)
            infrastructure_info = cursor.fetchall()

            if infrastructure_info:
                for question_id, question, answer in infrastructure_info:
                    answers = format_answer(question_id, answer)

                    # Create two columns for question and answers
                    col1, col2 = st.columns([2, 3])

                    with col1:
                        st.write(f"{question}:")

                    with col2:
                        # Display each label and value in separate cells
                        for label, value in answers:
                            label_html = styled_box(f"{label}") if label else ""
                            value_html = styled_box(value)
                            st.markdown(f"""
                            <div style="display: flex;">
                                <div style="flex: 1;">{label_html}</div>
                                <div style="flex: 1;">{value_html}</div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.write("No data available for Infrastructure Information.")

        # Part C: Vehicle Information
        st.header("Part C: Details of vehicles owned by the LA")

        if selected_local_authority:
            cursor.execute(f"""
                SELECT vt.name AS vehicle_type,
                       COALESCE(lav.running, 0) AS running,
                       COALESCE(lav.not_running, 0) AS not_running
                FROM vehicle_types vt
                LEFT JOIN local_authority_vehicles lav
                ON vt.id = lav.vehicle_type_id
                AND lav.local_authority_id = {local_authority_options[selected_local_authority]}
                AND lav.year = {selected_year}
            """)
            vehicles_info = cursor.fetchall()

            if vehicles_info:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader("Vehicle Type")
                    for vehicle_type, _, _ in vehicles_info:
                        st.write(vehicle_type)

                with col2:
                    st.subheader("Running")
                    for _, running, _ in vehicles_info:
                        st.write(running)

                with col3:
                    st.subheader("Not Running")
                    for _, _, not_running in vehicles_info:
                        st.write(not_running)
            else:
                st.write("No vehicle information available.")

        cursor.close()
        db_connection.close()
else:
    st.write("Please select an option to view.")