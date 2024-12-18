import mysql.connector
import pandas as pd
import streamlit as st
import json
from graphviz import Digraph
from PIL import Image
import os

# Function to connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

# Function to retrieve data from a table
def load_data(table_name):
    db_connection = connect_to_db()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, db_connection)
    db_connection.close()
    return df

# Function to retrieve schema of a table
def get_table_schema(table_name):
    db_connection = connect_to_db()
    cursor = db_connection.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    schema = cursor.fetchall()
    cursor.close()
    db_connection.close()
    return schema

# Function to retrieve all foreign key relationships
def get_foreign_keys():
    db_connection = connect_to_db()
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT
            TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE
            REFERENCED_TABLE_SCHEMA = 'LA_ANALYSIS'
            AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    foreign_keys = cursor.fetchall()
    cursor.close()
    db_connection.close()
    return foreign_keys

# Function to generate the ER diagram
def generate_er_diagram():
    foreign_keys = get_foreign_keys()
    dot = Digraph(comment='ER Diagram', format='png')
    
    tables = set()
    
    for fk in foreign_keys:
        table, column, ref_table, ref_column = fk
        dot.node(table, table)
        dot.node(ref_table, ref_table)
        dot.edge(f"{table}:{column}", f"{ref_table}:{ref_column}", label=f"{column} -> {ref_column}")
        tables.add(table)
        tables.add(ref_table)
    
    for table in tables:
        if not dot.node(table):
            dot.node(table, table)
    
    output_path = os.path.join(os.getcwd(), 'er_diagram')
    dot.render(output_path)
    return f"{output_path}.png"

# Function to format answers based on their type
def format_answer(question_id, answer, cursor):
    try:
        # Check if answer is JSON formatted
        answer_dict = json.loads(answer)
        if isinstance(answer_dict, dict):
            return [f"{get_option_text(cursor, question_id, key)}: {value}" for key, value in answer_dict.items()]
    except (json.JSONDecodeError, TypeError):
        # Handle case where answer is not JSON or is a different type
        return [str(answer)]
    return [str(answer)]

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

# Streamlit app layout
st.title("LA_ANALYSIS Database Viewer")

# Sidebar to choose between different functionalities
view_option = st.sidebar.radio("Choose what to display", ("Database_Tables", "Staff_Details", "General_Info","Annual_Budgets","Program_Title","Detail_of_GNDs","Details_of_Wards","Actual_budgets", "ER Diagram"))

if view_option == "Database_Tables":
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

        schema = get_table_schema(selected_table)
        schema_df = pd.DataFrame(schema, columns=["Field", "Type", "Null", "Key", "Default", "Extra"])
        st.write("Schema:")
        st.dataframe(schema_df)

        data = load_data(selected_table)
        st.write("Data:")
        st.dataframe(data)

elif view_option == "Staff_Details":
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

                # Fetch years available for the selected local authority, including 2024
                cursor.execute("SELECT DISTINCT year FROM local_authority_information WHERE local_authority_id = %s OR year = 2024", (local_authority_id,))
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

elif view_option == "General_Info":
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
                    return [f"{get_option_text(question_id, key)}: {value}" for key, value in answer_dict.items()]
            except (json.JSONDecodeError, TypeError):
                # Handle case where answer is not JSON or is a different type
                return [str(answer)]

            return [str(answer)]

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
                        st.write(f"**{question}:**")
                   
                    with col2:
                        for ans in answers:
                            st.markdown(styled_box(ans), unsafe_allow_html=True)  # Display each answer with a border box
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
                        st.write(f"**{question}:**")
                   
                    with col2:
                        for ans in answers:
                            st.markdown(styled_box(ans), unsafe_allow_html=True)  # Display each answer with a border box
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
    

elif view_option == "Annual_Budgets":

    # Establishing the connection to the database
    db_connection = connect_to_db()

    # Creating a cursor object to interact with the database
    cursor = db_connection.cursor()

    # Fetch provinces
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    provinces_df = pd.DataFrame(provinces, columns=["province_id", "province_name"])
    province_names = provinces_df['province_name'].tolist()

    # Sidebar for selecting Province
    selected_province = st.sidebar.selectbox("Select a Province", province_names)
    if selected_province:
        province_id = int(provinces_df[provinces_df['province_name'] == selected_province]['province_id'].values[0])

        # Fetch districts for selected Province
        cursor.execute("SELECT id, name FROM districts WHERE province_id = %s", (province_id,))
        districts = cursor.fetchall()
        districts_df = pd.DataFrame(districts, columns=["district_id", "district_name"])
        district_names = districts_df['district_name'].tolist()

        # Sidebar for selecting District
        selected_district = st.sidebar.selectbox("Select a District", district_names)
        if selected_district:
            district_id = int(districts_df[districts_df['district_name'] == selected_district]['district_id'].values[0])

            # Fetch local authorities for selected District
            cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s", (district_id,))
            local_authorities = cursor.fetchall()
            local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])
            local_authority_names = local_authorities_df['local_authority_name'].tolist()

            # Sidebar for selecting Local Authority
            selected_local_authority = st.sidebar.selectbox("Select a Local Authority", local_authority_names)
            if selected_local_authority:
                local_authority_id = int(local_authorities_df[local_authorities_df['local_authority_name'] == selected_local_authority]['local_authority_id'].values[0])

                # Fetch years for selected Local Authority
                cursor.execute("SELECT DISTINCT year FROM annual_budgets WHERE local_authority_id = %s", (local_authority_id,))
                years = cursor.fetchall()
                years_df = pd.DataFrame(years, columns=["year"])
                year_list = years_df['year'].tolist()

                # Sidebar for selecting Year
                selected_year = st.sidebar.selectbox("Select a Year", year_list)
                if selected_year:
                    # Fetch program titles dynamically
                    cursor.execute("""
                        SELECT id, program_title 
                        FROM local_authority_programs 
                        WHERE local_authority_id = %s AND year = %s 
                        ORDER BY id LIMIT 6
                    """, (local_authority_id, selected_year))
                    programs = cursor.fetchall()
                    program_titles = [program[1] for program in programs]

                    # Ensure unique program titles for the columns
                    program_titles = list(dict.fromkeys(program_titles))

                    # Adjust the number of program columns to avoid duplicates
                    if len(program_titles) < 6:
                        program_titles += [f"Program_{i+1}" for i in range(6 - len(program_titles))]

                    revenue_columns = ["Revenue Name", "Total Amount"] + program_titles

                    # Fetch Revenue Details for selected filters
                    query_revenue = """
                    SELECT r.name, abd.total_amount, abd.program_1, abd.program_2, abd.program_3, abd.program_4, abd.program_5, abd.program_6
                    FROM revenues r
                    JOIN annual_budget_details abd ON r.id = abd.revenue_id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s
                    """
                    cursor.execute(query_revenue, (local_authority_id, selected_year))
                    all_revenue_data = cursor.fetchall()
                    all_revenue_df = pd.DataFrame(all_revenue_data, columns=revenue_columns)
                    
                    # Exclude the last 4 records for Revenue Details
                    revenue_count = len(all_revenue_df)
                    if revenue_count > 4:
                        revenue_df = all_revenue_df.iloc[:-4]
                    else:
                        revenue_df = all_revenue_df

                    # Fetch the last 4 records from the Revenue Details table
                    query_internal_cash_flow = """
                    SELECT r.name, abd.total_amount, abd.program_1, abd.program_2, abd.program_3, abd.program_4, abd.program_5, abd.program_6
                    FROM revenues r
                    JOIN annual_budget_details abd ON r.id = abd.revenue_id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s
                    ORDER BY abd.id DESC
                    LIMIT 4
                    """
                    cursor.execute(query_internal_cash_flow, (local_authority_id, selected_year))
                    internal_cash_flow_data = cursor.fetchall()
                    internal_cash_flow_df = pd.DataFrame(internal_cash_flow_data, columns=revenue_columns)

                    # Remove the last 2 records from Additional Revenue Data Breakup (previously Internal Cash Flow In)
                    if len(internal_cash_flow_df) > 2:
                        additional_revenue_data_df = internal_cash_flow_df.iloc[:-2]
                    else:
                        additional_revenue_data_df = internal_cash_flow_df

                    # Extract the last 2 records from the Internal Cash Flow In table
                    if len(internal_cash_flow_df) >= 2:
                        internal_cash_flow_in_df = internal_cash_flow_df.iloc[-2:]
                    else:
                        internal_cash_flow_in_df = internal_cash_flow_df

                    # Fetch Expenditure Details for selected filters
                    query_expenditure = """
                    SELECT e.name, abd.total_amount, abd.program_1, abd.program_2, abd.program_3, abd.program_4, abd.program_5, abd.program_6
                    FROM expenditures e
                    JOIN annual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s
                    """
                    cursor.execute(query_expenditure, (local_authority_id, selected_year))
                    expenditure_data = cursor.fetchall()
                    expenditure_columns = ["Expenditure Name", "Total Amount"] + program_titles
                    expenditure_df = pd.DataFrame(expenditure_data, columns=expenditure_columns)

                    # Extract the last 6 records from Expenditure Details
                    if len(expenditure_df) >= 6:
                        additional_capital_expenses_df = expenditure_df.iloc[-6:]
                        # Remove the last 6 records from Expenditure Details for display
                        expenditure_df = expenditure_df.iloc[:-6]
                    else:
                        additional_capital_expenses_df = expenditure_df

                    # Extract the last 2 records from Additional Capital Expenses Data Breakup (for Internal Cash Flow Out)
                    if len(additional_capital_expenses_df) >= 2:
                        internal_cash_flow_out_df = additional_capital_expenses_df.iloc[-2:]
                    else:
                        internal_cash_flow_out_df = additional_capital_expenses_df

                    # Remove the last 2 records from Additional Capital Expenses Data Breakup
                    if len(additional_capital_expenses_df) > 2:
                        additional_capital_expenses_df = additional_capital_expenses_df.iloc[:-2]
                    else:
                        additional_capital_expenses_df = pd.DataFrame(columns=additional_capital_expenses_df.columns)

                    # Display the Revenue Details table (excluding last 4 records)
                    st.subheader("Revenue Details")
                    st.dataframe(revenue_df)

                    # Display the Additional Revenue Data Breakup table (previously Internal Cash Flow In)
                    st.subheader("Additional Revenue Data Breakup")
                    st.dataframe(additional_revenue_data_df)

                    # Display the Internal Cash Flow In table (previously Additional Revenue Data Breakup In)
                    st.subheader("Internal Cash Flow In")
                    st.dataframe(internal_cash_flow_in_df)

                    # Display the Expenditure Details table (excluding last 6 records)
                    st.subheader("Expenditure Details")
                    st.dataframe(expenditure_df)

                    # Display the Additional Capital Expenses Data Breakup table
                    st.subheader("Additional Capital Expenses Data Breakup")
                    st.dataframe(additional_capital_expenses_df)

                    # Display the Internal Cash Flow Out table
                    st.subheader("Internal Cash Flow Out")
                    st.dataframe(internal_cash_flow_out_df)

    # Closing the cursor and database connection
    cursor.close()
    db_connection.close()


elif view_option == "Program_Title":
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

                # Fetch and display years based on selected local authority
                cursor.execute("SELECT DISTINCT year FROM local_authority_programs WHERE local_authority_id = %s", (local_authority_id,))
                years = cursor.fetchall()
                years_df = pd.DataFrame(years, columns=["year"])
                year_list = years_df['year'].tolist()
                selected_year = st.sidebar.selectbox("Select a Year", year_list)

                if selected_year:
                    # Fetch program types and program titles based on selected filters
                    cursor.execute("""
                        SELECT pt.name AS Program_Type, lap.program_title AS Program_Title
                        FROM program_types pt
                        JOIN local_authority_programs lap ON lap.program_type_id = pt.id
                        WHERE lap.local_authority_id = %s AND lap.year = %s
                    """, (local_authority_id, selected_year))
                    
                    results = cursor.fetchall()
                    results_df = pd.DataFrame(results, columns=["Program Type", "Program Title"])

                    # Display the results in full view
                    st.subheader(f"Program Types and Titles for {selected_province} -> {selected_district} -> {selected_local_authority} ({selected_year})")
                    st.dataframe(results_df, use_container_width=True)  # Ensure full-width display

    cursor.close()
    db_connection.close()

elif view_option == "Detail_of_GNDs":
        
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

elif view_option == "Details_of_Wards":
        
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
                cursor.execute("SELECT DISTINCT year FROM wards WHERE local_authority_id = %s ORDER BY year DESC", (local_authority_id,))
                years = cursor.fetchall()
                years_df = pd.DataFrame(years, columns=["year"])
                year_list = years_df['year'].tolist()
                selected_year = st.sidebar.selectbox("Select a Year", year_list)

                if selected_year:
                    # Fetch and display data from wards based on selected filters
                    cursor.execute("""
                        SELECT ward_name, ward_number, population
                        FROM wards
                        WHERE local_authority_id = %s AND year = %s
                    """, (local_authority_id, selected_year))
                    
                    wards = cursor.fetchall()
                    wards_df = pd.DataFrame(wards, columns=["Ward Name", "Ward Number", "Population"])

                    # Display the results
                    st.subheader(f"Ward Data for {selected_province} -> {selected_district} -> {selected_local_authority} ({selected_year})")
                    st.dataframe(wards_df, use_container_width=True)

    cursor.close()
    db_connection.close()


elif view_option == "ER Diagram":
    # Generate and display the ER diagram
    st.subheader("Entity-Relationship Diagram")
    er_diagram_path = generate_er_diagram()
    image = Image.open(er_diagram_path)
    st.image(image, caption="ER Diagram", use_column_width=True)

elif view_option == "Actual_budgets":

    # Establishing the connection to the database
    db_connection = connect_to_db()

    # Creating a cursor object to interact with the database
    cursor = db_connection.cursor()

    # Fetch provinces
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    provinces_df = pd.DataFrame(provinces, columns=["province_id", "province_name"])
    province_names = provinces_df['province_name'].tolist()

    # Sidebar for selecting Province
    selected_province = st.sidebar.selectbox("Select a Province", province_names)
    if selected_province:
        province_id = int(provinces_df[provinces_df['province_name'] == selected_province]['province_id'].values[0])

        # Fetch districts for selected Province
        cursor.execute("SELECT id, name FROM districts WHERE province_id = %s", (province_id,))
        districts = cursor.fetchall()
        districts_df = pd.DataFrame(districts, columns=["district_id", "district_name"])
        district_names = districts_df['district_name'].tolist()

        # Sidebar for selecting District
        selected_district = st.sidebar.selectbox("Select a District", district_names)
        if selected_district:
            district_id = int(districts_df[districts_df['district_name'] == selected_district]['district_id'].values[0])

            # Fetch local authorities for selected District
            cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s", (district_id,))
            local_authorities = cursor.fetchall()
            local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])
            local_authority_names = local_authorities_df['local_authority_name'].tolist()

            # Sidebar for selecting Local Authority
            selected_local_authority = st.sidebar.selectbox("Select a Local Authority", local_authority_names)
            if selected_local_authority:
                local_authority_id = int(local_authorities_df[local_authorities_df['local_authority_name'] == selected_local_authority]['local_authority_id'].values[0])

                # Fetch years for selected Local Authority
                cursor.execute("SELECT DISTINCT year FROM actual_budgets WHERE local_authority_id = %s", (local_authority_id,))
                years = cursor.fetchall()
                years_df = pd.DataFrame(years, columns=["year"])
                year_list = years_df['year'].tolist()

                # Sidebar for selecting Year
                selected_year = st.sidebar.selectbox("Select a Year", year_list)
                if selected_year:

                    # Map months to their corresponding numeric values
                    month_mapping = {
                        "January": 1, "February": 2, "March": 3, "April": 4,
                        "May": 5, "June": 6, "July": 7, "August": 8,
                        "September": 9, "October": 10, "November": 11, "December": 12, "Total Actual Budgets": 0
                    }

                    # Sidebar for selecting Month
                    selected_month_name = st.sidebar.selectbox("Select a Month", list(month_mapping.keys()))
                    selected_month = month_mapping[selected_month_name]

                    # Fetch program titles dynamically
                    cursor.execute("""
                        SELECT id, program_title 
                        FROM local_authority_programs 
                        WHERE local_authority_id = %s AND year = %s 
                        ORDER BY id LIMIT 6
                    """, (local_authority_id, selected_year))
                    programs = cursor.fetchall()
                    program_titles = [program[1] for program in programs]

                    # Ensure unique program titles for the columns
                    program_titles = list(dict.fromkeys(program_titles))

                    # Adjust the number of program columns to avoid duplicates
                    if len(program_titles) < 6:
                        program_titles += [f"Program_{i+1}" for i in range(6 - len(program_titles))]

                    revenue_columns = ["Revenue Name", "Total Amount"] + program_titles
                    expenditure_columns = ["Expenditure Name", "Total Amount"] + program_titles

                    if selected_month == 0:
                        # Total Actual Budgets case
                        query_revenue = """
                        SELECT r.name, SUM(abd.total_amount) AS total_amount, 
                            SUM(abd.program_1) AS program_1, SUM(abd.program_2) AS program_2, 
                            SUM(abd.program_3) AS program_3, SUM(abd.program_4) AS program_4, 
                            SUM(abd.program_5) AS program_5, SUM(abd.program_6) AS program_6
                        FROM revenues r
                        JOIN actual_budget_details abd ON r.id = abd.revenue_id
                        JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                        WHERE ab.local_authority_id = %s AND ab.year = %s
                        GROUP BY r.name
                        """
                        cursor.execute(query_revenue, (local_authority_id, selected_year))
                        all_revenue_data = cursor.fetchall()
                        all_revenue_df = pd.DataFrame(all_revenue_data, columns=revenue_columns)
                        
                        # Fetch Expenditure Details for selected filters
                        query_expenditure = """
                        SELECT e.name, SUM(abd.total_amount) AS total_amount, 
                            SUM(abd.program_1) AS program_1, SUM(abd.program_2) AS program_2, 
                            SUM(abd.program_3) AS program_3, SUM(abd.program_4) AS program_4, 
                            SUM(abd.program_5) AS program_5, SUM(abd.program_6) AS program_6
                        FROM expenditures e
                        JOIN actual_budget_details abd ON e.id = abd.expenditure_id
                        JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                        WHERE ab.local_authority_id = %s AND ab.year = %s
                        GROUP BY e.name
                        """
                        cursor.execute(query_expenditure, (local_authority_id, selected_year))
                        expenditure_data = cursor.fetchall()
                        expenditure_df = pd.DataFrame(expenditure_data, columns=expenditure_columns)

                        st.subheader("Total Actual Budgets")
                        st.dataframe(all_revenue_df)
                        st.dataframe(expenditure_df)
                    else:
                        # Monthly data case
                        # Fetch Revenue Details for selected filters
                        query_revenue = """
                        SELECT r.name, abd.total_amount, abd.program_1, abd.program_2, abd.program_3, abd.program_4, abd.program_5, abd.program_6
                        FROM revenues r
                        JOIN actual_budget_details abd ON r.id = abd.revenue_id
                        JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                        WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month = %s
                        """
                        cursor.execute(query_revenue, (local_authority_id, selected_year, selected_month))
                        all_revenue_data = cursor.fetchall()
                        all_revenue_df = pd.DataFrame(all_revenue_data, columns=revenue_columns)
                        
                        # Exclude the last 4 records for Revenue Details
                        revenue_count = len(all_revenue_df)
                        if revenue_count > 4:
                            revenue_df = all_revenue_df.iloc[:-4]
                        else:
                            revenue_df = all_revenue_df

                        # Fetch the last 4 records from the Revenue Details table
                        query_internal_cash_flow = """
                        SELECT r.name, abd.total_amount, abd.program_1, abd.program_2, abd.program_3, abd.program_4, abd.program_5, abd.program_6
                        FROM revenues r
                        JOIN actual_budget_details abd ON r.id = abd.revenue_id
                        JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                        WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month = %s
                        ORDER BY abd.id DESC
                        LIMIT 4
                        """
                        cursor.execute(query_internal_cash_flow, (local_authority_id, selected_year, selected_month))
                        internal_cash_flow_data = cursor.fetchall()
                        internal_cash_flow_df = pd.DataFrame(internal_cash_flow_data, columns=revenue_columns)

                        # Remove the last 2 records from Additional Revenue Data Breakup (previously Internal Cash Flow In)
                        if len(internal_cash_flow_df) > 2:
                            additional_revenue_data_df = internal_cash_flow_df.iloc[:-2]
                        else:
                            additional_revenue_data_df = internal_cash_flow_df

                        # Extract the last 2 records from the Internal Cash Flow In table
                        if len(internal_cash_flow_df) >= 2:
                            internal_cash_flow_in_df = internal_cash_flow_df.iloc[-2:]
                        else:
                            internal_cash_flow_in_df = internal_cash_flow_df

                        # Fetch Expenditure Details for selected filters
                        query_expenditure = """
                        SELECT e.name, abd.total_amount, abd.program_1, abd.program_2, abd.program_3, abd.program_4, abd.program_5, abd.program_6
                        FROM expenditures e
                        JOIN actual_budget_details abd ON e.id = abd.expenditure_id
                        JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                        WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month = %s
                        """
                        cursor.execute(query_expenditure, (local_authority_id, selected_year, selected_month))
                        expenditure_data = cursor.fetchall()
                        expenditure_df = pd.DataFrame(expenditure_data, columns=expenditure_columns)

                        st.subheader("Revenue Details")
                        st.dataframe(revenue_df)
                        st.subheader("Additional Revenue Data Breakup")
                        st.dataframe(additional_revenue_data_df)
                        st.subheader("Internal Cash Flow In")
                        st.dataframe(internal_cash_flow_in_df)
                        st.subheader("Expenditure Details")
                        st.dataframe(expenditure_df)

    # Close the database connection
    cursor.close()
    db_connection.close()
