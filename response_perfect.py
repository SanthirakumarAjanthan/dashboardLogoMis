import pandas as pd
import streamlit as st
import mysql.connector

# Function to connect to the database
def connect_to_db():
    try:
        return mysql.connector.connect(
            host="170.64.176.75",
            user="vaitheki",
            password="Abcd@878172",
            database="PERFECT20"
        )
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        st.stop()  # Stop execution if the connection fails

# Establish the connection to the database
db_connection = connect_to_db()
cursor = db_connection.cursor()

try:
    # Fetch provinces
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    provinces_df = pd.DataFrame(provinces, columns=["province_id", "province_name"])
    province_names = provinces_df['province_name'].tolist()

    # Sidebar for selecting Province
    selected_province = st.sidebar.selectbox("Select a Province", province_names)
    if selected_province:
        province_id = int(provinces_df.loc[provinces_df['province_name'] == selected_province, 'province_id'].values[0])

        # Fetch districts for the selected province
        cursor.execute("SELECT id, name FROM districts WHERE province_id = %s", (province_id,))
        districts = cursor.fetchall()
        districts_df = pd.DataFrame(districts, columns=["district_id", "district_name"])
        district_names = districts_df['district_name'].tolist()

        # Sidebar for selecting District
        selected_district = st.sidebar.selectbox("Select a District", district_names)
        if selected_district:
            district_id = int(districts_df.loc[districts_df['district_name'] == selected_district, 'district_id'].values[0])

            # Fetch local authorities for the selected district
            cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s", (district_id,))
            local_authorities = cursor.fetchall()
            local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])
            local_authority_names = local_authorities_df['local_authority_name'].tolist()

            # Sidebar for selecting Local Authority
            selected_local_authority = st.sidebar.selectbox("Select a Local Authority", local_authority_names)
            if selected_local_authority:
                local_authority_id = int(local_authorities_df.loc[
                    local_authorities_df['local_authority_name'] == selected_local_authority,
                    'local_authority_id'
                ].values[0])

                # Dropdown for selecting Assessment Type
                assessment_types = {
                    "Provincial Assessment": 1,
                    "Other Assessment Type 0": 0,
                    "Other Assessment Type 2": 2,
                    "Other Assessment Type 3": 3,
                }

                # Update the selectbox to display keys from the dictionary
                selected_assessment_type_name = st.sidebar.selectbox("Select Assessment Type", list(assessment_types.keys()))

                # Map the selected name back to the corresponding assessment type value
                selected_assessment_type = assessment_types[selected_assessment_type_name]

                # Fetch distinct years from surveys
                cursor.execute("SELECT DISTINCT YEAR(created_at) AS year FROM surveys WHERE local_authority_id = %s", (local_authority_id,))
                years = cursor.fetchall()
                year_list = [year[0] for year in years]

                # Sidebar for selecting Year
                selected_year = st.sidebar.selectbox("Select Year", year_list)
                if selected_year:
                    # Fetch questionnaire sections
                    cursor.execute("SELECT id, name FROM questionnaire_sections")
                    sections = cursor.fetchall()
                    sections_df = pd.DataFrame(sections, columns=["section_id", "section_name"])
                    section_titles = sections_df['section_name'].tolist()

                    # Sidebar for selecting Questionnaire Section
                    selected_section = st.sidebar.selectbox("Select a Questionnaire Section", section_titles)
                    if selected_section:
                        section_id = int(sections_df.loc[sections_df['section_name'] == selected_section, 'section_id'].values[0])

                        # Display selected section
                        st.subheader(f"Selected Questionnaire Section: {selected_section}")

                        # Fetch sub-sections and display them
                        cursor.execute(
                            """
                            SELECT id, name
                            FROM questionnaire_sub_sections
                            WHERE questionnaire_section_id = %s
                            """,
                            (section_id,)
                        )
                        sub_sections = cursor.fetchall()

                        # Display sub-sections and related data
                        if sub_sections:
                            for sub_section in sub_sections:
                                sub_section_id, sub_section_name = sub_section
                                st.subheader(sub_section_name)  # Display sub-section name

                                # Fetch survey responses with selected assessment_type and year
                                cursor.execute(
                                    """
                                    SELECT
                                        q.id AS question_id,
                                        q.question,
                                        GROUP_CONCAT(DISTINCT qo.slug SEPARATOR ', ') AS options,
                                        GROUP_CONCAT(DISTINCT sr.answer SEPARATOR ', ') AS answers
                                    FROM questionnaires AS q
                                    LEFT JOIN question_options qo ON q.id = qo.questionnaire_id
                                    LEFT JOIN survey_responses sr ON sr.questionnaire_id = q.id
                                        AND sr.questionnaire_section_id = %s
                                        AND sr.survey_id IN (
                                            SELECT id
                                            FROM surveys
                                            WHERE local_authority_id = %s
                                            AND assessment_type = %s  -- Filter by selected assessment type
                                            AND YEAR = %s -- Filter by selected year
                                        )
                                    WHERE q.sub_section = %s  -- Ensure you're filtering by sub-section ID
                                    GROUP BY q.id, q.question
                                    """,
                                    (section_id, local_authority_id, selected_assessment_type, selected_year, sub_section_id)
                                )
                                results = cursor.fetchall()

                                # Prepare to display the results
                                if results:
                                    # Create a DataFrame from the fetched results
                                    results_df = pd.DataFrame(
                                        results,
                                        columns=["question_id", "question", "options", "answers"]
                                    )

                                    # Process the 'answers' column to create the 'response' column
                                    results_df['response'] = results_df['answers'].apply(lambda x: x if x.count(',') == 0 else '')  # Only display single answers

                                    # Combine 'options' and 'response' into a single column, handling None values
                                    results_df['combined_response'] = results_df.apply(
                                        lambda row: f" {row['options'] or ''}  {row['response'] or ''}", axis=1
                                    )

                                    # Reorganize the DataFrame to display only the necessary columns with renamed column
                                    results_df = results_df.rename(columns={"combined_response": "Responses"})  # Rename column
                                    results_df = results_df[['question_id', 'question', 'Responses']]  # Remove 'record_number'

                                    st.write(f"Survey Responses for {sub_section_name}:")
                                    st.dataframe(results_df)  # Display the DataFrame as a table
                                else:
                                    st.info(f"No survey responses found for {sub_section_name}.")
                        else:
                            st.info("No sub-sections found for the selected section.")

except mysql.connector.Error as err:
    st.error(f"Database error: {err}")

finally:
    # Close cursor and database connection
    cursor.close()
    db_connection.close() 

