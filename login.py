import streamlit as st
import pandas as pd
import mysql.connector
import json

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
# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"  # Default page is Home

# Define a function to connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

# Define a function to change pages
def navigate_to(page_name):
    st.session_state.page = page_name

# Handle page navigation
if st.session_state.page == "Home":
    st.title("Home")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("LoGoMIS"):
            navigate_to("LoGoMIS")
    with col2:
        if st.button("PERFECT 2.0"):
            navigate_to("PERFECT 2.0")    


elif st.session_state.page == "LoGoMIS":
    st.title("LoGoMIS")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("LogoMis Mapping"):
            navigate_to("LogoMis Mapping")
        if st.button("General Info"):
            navigate_to("General Info")
        if st.button("Actual This Month"):
            navigate_to("Actual This Month")

    with col2:
        if st.button("Staff Summary"):
            navigate_to("Staff Summary")
        if st.button("Upto This Month"):
            navigate_to("Staff Summary")

    with col3:
        if st.button("Vehicle Summary"):
            navigate_to("Vehicle summary")
        if st.button("Budget Status"):
            navigate_to("Budget Status")

    if st.button("Back to Home"):
        navigate_to("Home")

elif st.session_state.page == "PERFECT 2.0":
    st.title("PERFECT 2.0")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Perfect Schema"):
            navigate_to("Perfect Schema")

    with col2:
        if st.button("Response perfect"):
            navigate_to("Response perfect")

        if st.button("Back to Home"):
          navigate_to("Home")

elif st.session_state.page == "Logomis Mapping": 
    
    # Streamlit app layout
    st.title("LA_ANALYSIS Database Viewer")

    # Sidebar to choose a table to view
    st.sidebar.header("Select a Table to View")

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

        # Fetch and display schema and data for the selected table
        db_connection = connect_to_db()
        cursor = db_connection.cursor()
        cursor.execute(f"DESCRIBE {selected_table}")
        schema = cursor.fetchall()
        schema_df = pd.DataFrame(schema, columns=["Field", "Type", "Null", "Key", "Default", "Extra"])
        st.write("Schema:")
        st.dataframe(schema_df)

        # Fetch table data
        data = pd.read_sql(f"SELECT * FROM {selected_table}", db_connection)
        st.write("Data:")
        st.dataframe(data)

        cursor.close()
        db_connection.close()

    if st.button("Back to Home"):
        navigate_to("Home")

elif st.session_state.page == "General Info":
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

    if st.button("Back"):
        navigate_to("LoGoMIS")

elif st.session_state.page == "Staff Summary":

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

    if st.button("Back"):
        navigate_to("LoGoMIS")

elif st.session_state.page == "Vehicle summary":
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

    if st.button("Back"):
        navigate_to("LoGoMIS")

elif st.session_state.page == "Upto This Month":
    #Establishing the connection to the database
    db_connection = connect_to_db()
    cursor = db_connection.cursor()

    # Fetch provinces
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    provinces_df = pd.DataFrame(provinces, columns=["province_id", "province_name"])
    province_names = provinces_df['province_name'].tolist()
    st.write("### upto This month")
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

            # Sidebar for selecting Local Authority Type
            selected_local_authority_type = st.sidebar.selectbox("Select Local Authority Type", ["MC", "UC", "PS"])

            # Fetch local authorities for the selected type
            cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s AND type = %s", (district_id, selected_local_authority_type))
            local_authorities = cursor.fetchall()
            local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])

            # Fetch years for all local authorities of the selected type
            local_authority_ids = local_authorities_df['local_authority_id'].tolist()
            local_authority_names = local_authorities_df['local_authority_name'].tolist()

            # Sidebar for selecting Year
            cursor.execute("SELECT DISTINCT year FROM actual_budgets WHERE local_authority_id IN (%s)" % ','.join(map(str, local_authority_ids)))
            years = cursor.fetchall()
            years_df = pd.DataFrame(years, columns=["year"])
            year_list = years_df['year'].tolist()

            selected_year = st.sidebar.selectbox("Select a Year", year_list)
            if selected_year:

                # Map months to their corresponding numeric values
                month_mapping = {
                    "ANNUAL": 0, "January": 1, "February": 2, "March": 3, "April": 4,
                    "May": 5, "June": 6, "July": 7, "August": 8,
                    "September": 9, "October": 10, "November": 11, "December": 12
                }

                # Sidebar for selecting Month
                selected_month_name = st.sidebar.selectbox("Select a Month", list(month_mapping.keys()))
                selected_month = month_mapping[selected_month_name]

                # Initialize DataFrames for revenues and expenditures with province and district columns
                revenue_columns = [
                    "Province", "District", "Local Authority",
                    "Rate & Taxes (BUDGET)", "Rate & Taxes (Actual)",
                    "Rent (BUDGET)", "Rent (Actual)",
                    "License (BUDGET)", "License (Actual)",
                    "Fees for Service (BUDGET)", "Fees for Service (Actual)",
                    "Warrant Cost, Fine & Penalties (BUDGET)", "Warrant Cost, Fine & Penalties (Actual)",
                    "Other Revenue (BUDGET)", "Other Revenue (Actual)",
                    "Revenue Grants (All Salary related) (BUDGET)", "Revenue Grants (All Salary related) (Actual)",
                    "Revenue Grants (Other than Salary related) (BUDGET)", "Revenue Grants (Other than Salary related) (Actual)",
                    "Recurrent Revenue Total (BUDGET)", "Recurrent Revenue Total (Actual)",
                    "Capital Grants (BUDGET)", "Capital Grants (Actual)",
                    "Capital Loans (BUDGET)", "Capital Loans (Actual)",
                    "Sale of Capital Assets (BUDGET)", "Sale of Capital Assets (Actual)",
                    "Any other capital receipts (BUDGET)", "Any other capital receipts (Actual)",
                    "Non Recurrent Revenue Total (BUDGET)", "Non Recurrent Revenue Total (Actual)"
                ]
                total_revenue_df = pd.DataFrame(columns=revenue_columns)

                # Adding new columns for recurrent and non-recurrent expenditure totals to expenditure_columns
                expenditure_columns = [
                    "Province", "District", "Local Authority",
                    "Personal Emoluments (BUDGET)", "Personal Emoluments (Actual)",
                    "Traveling Expenses (BUDGET)", "Traveling Expenses (Actual)",
                    "Supplies & Requisites (BUDGET)", "Supplies & Requisites (Actual)",
                    "Repairs & Maintenance of Capital Assets (BUDGET)", "Repairs & Maintenance of Capital Assets (Actual)",
                    "Transportation Communication & Utility Service (BUDGET)", "Transportation Communication & Utility Service (Actual)",
                    "Interest Payments, Dividends (BUDGET)", "Interest Payments, Dividends (Actual)",
                    "Grants Contributions & Subsidies (BUDGET)", "Grants Contributions & Subsidies (Actual)",
                    "Pensions, Retirement Benefits & Gratuities (BUDGET)", "Pensions, Retirement Benefits & Gratuities (Actual)",
                    "Recurrent Expenditure Total (BUDGET)", 
                    "Recurrent Expenditure Actual (This Month)",
                    "Capital Expenditure (BUDGET)", "Capital Expenditure (Actual)",
                    "Rehabilitation Fund (BUDGET)", "Rehabilitation Fund (Actual)",
                    "Loan Repayment (BUDGET)", "Loan Repayment (Actual)",
                    "Any other capital expenditure (BUDGET)", "Any other capital expenditure (Actual)",
                    "Non Recurrent Expenditure Total (BUDGET)",
                    "Non Recurrent Expenditure Actual (This Month)"
                ]
                total_expenditure_df = pd.DataFrame(columns=expenditure_columns)

                # List to store DataFrames for concatenation later
                revenue_data_list = []
                expenditure_data_list = []

                for local_authority_id, local_authority_name in zip(local_authority_ids, local_authority_names):
                    # Initialize revenue and expenditure data
                    revenue_data = {col: 0 for col in revenue_columns}
                    revenue_data["Province"] = selected_province
                    revenue_data["District"] = selected_district
                    revenue_data["Local Authority"] = local_authority_name

                    expenditure_data = {col: 0 for col in expenditure_columns}
                    expenditure_data["Province"] = selected_province
                    expenditure_data["District"] = selected_district
                    expenditure_data["Local Authority"] = local_authority_name

                    # Fetch and populate annual and actual data for revenue
                    cursor.execute(""" 
                    SELECT r.name, SUM(abd.total_amount) AS annual_total
                    FROM revenues r
                    JOIN annual_budget_details abd ON r.id = abd.revenue_id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s
                    GROUP BY r.name
                    """, (local_authority_id, selected_year))
                    annual_budget_revenue_data = cursor.fetchall()
                    for revenue_name, annual_total in annual_budget_revenue_data:
                        if f"{revenue_name} (BUDGET)" in revenue_data:
                            revenue_data[f"{revenue_name} (BUDGET)"] = annual_total

                    # Create a string of months for SQL query
                    months_in_query = ', '.join([str(i) for i in range(1, selected_month + 1)])
                    cursor.execute(f"""
                    SELECT r.name, SUM(abd.total_amount) AS actual_total
                    FROM revenues r
                    JOIN actual_budget_details abd ON r.id = abd.revenue_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN ({months_in_query})
                    GROUP BY r.name
                    """, (local_authority_id, selected_year))
                    actual_revenue_data = cursor.fetchall()
                    for revenue_name, actual_total in actual_revenue_data:
                        if f"{revenue_name} (Actual)" in revenue_data:
                            revenue_data[f"{revenue_name} (Actual)"] = actual_total

                    # Calculate Recurrent Revenue Totals
                    recurrent_budget_keys = [
                        "Rate & Taxes (BUDGET)", "Rent (BUDGET)", "License (BUDGET)", "Fees for Service (BUDGET)",
                        "Warrant Cost, Fine & Penalties (BUDGET)", "Other Revenue (BUDGET)",
                        "Revenue Grants (All Salary related) (BUDGET)", "Revenue Grants (Other than Salary related) (BUDGET)"
                    ]
                    recurrent_actual_keys = [
                        "Rate & Taxes (Actual)", "Rent (Actual)", "License (Actual)", "Fees for Service (Actual)",
                        "Warrant Cost, Fine & Penalties (Actual)", "Other Revenue (Actual)",
                        "Revenue Grants (All Salary related) (Actual)", "Revenue Grants (Other than Salary related) (Actual)"
                    ]
                    revenue_data["Recurrent Revenue Total (BUDGET)"] = sum(revenue_data[key] for key in recurrent_budget_keys)
                    revenue_data["Recurrent Revenue Total (Actual)"] = sum(revenue_data[key] for key in recurrent_actual_keys)

                    # Non Recurrent Revenue Totals
                    revenue_data["Non Recurrent Revenue Total (BUDGET)"] = sum(revenue_data[key] for key in [
                        "Capital Grants (BUDGET)", "Capital Loans (BUDGET)", "Sale of Capital Assets (BUDGET)",
                        "Any other capital receipts (BUDGET)"
                    ])
                    revenue_data["Non Recurrent Revenue Total (Actual)"] = sum(revenue_data[key] for key in [
                        "Capital Grants (Actual)", "Capital Loans (Actual)", "Sale of Capital Assets (Actual)",
                        "Any other capital receipts (Actual)"
                    ])

                    # Append revenue data to the list
                    revenue_data_list.append(pd.DataFrame([revenue_data]))

                    # Fetch and populate annual and actual data for expenditure
                    cursor.execute(""" 
                    SELECT e.name, SUM(abd.total_amount) AS annual_total
                    FROM expenditures e
                    JOIN annual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s
                    GROUP BY e.name
                    """, (local_authority_id, selected_year))
                    annual_budget_expenditure_data = cursor.fetchall()
                    for expenditure_name, annual_total in annual_budget_expenditure_data:
                        if f"{expenditure_name} (BUDGET)" in expenditure_data:
                            expenditure_data[f"{expenditure_name} (BUDGET)"] = annual_total

                    cursor.execute(f"""
                    SELECT e.name, SUM(abd.total_amount) AS actual_total
                    FROM expenditures e
                    JOIN actual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN ({months_in_query})
                    GROUP BY e.name
                    """, (local_authority_id, selected_year))
                    actual_expenditure_data = cursor.fetchall()
                    for expenditure_name, actual_total in actual_expenditure_data:
                        if f"{expenditure_name} (Actual)" in expenditure_data:
                            expenditure_data[f"{expenditure_name} (Actual)"] = actual_total

                    # Calculate Recurrent Expenditure Totals
                    recurrent_budget_keys = [
                        "Personal Emoluments (BUDGET)", "Traveling Expenses (BUDGET)", "Supplies & Requisites (BUDGET)",
                        "Repairs & Maintenance of Capital Assets (BUDGET)", 
                        "Transportation Communication & Utility Service (BUDGET)", 
                        "Interest Payments, Dividends (BUDGET)", "Grants Contributions & Subsidies (BUDGET)",
                        "Pensions, Retirement Benefits & Gratuities (BUDGET)"
                    ]
                    recurrent_actual_keys = [
                        "Personal Emoluments (Actual)", "Traveling Expenses (Actual)", "Supplies & Requisites (Actual)",
                        "Repairs & Maintenance of Capital Assets (Actual)", 
                        "Transportation Communication & Utility Service (Actual)", 
                        "Interest Payments, Dividends (Actual)", "Grants Contributions & Subsidies (Actual)",
                        "Pensions, Retirement Benefits & Gratuities (Actual)"
                    ]
                    expenditure_data["Recurrent Expenditure Total (BUDGET)"] = sum(expenditure_data[key] for key in recurrent_budget_keys)
                    expenditure_data["Recurrent Expenditure Actual (This Month)"] = sum(expenditure_data[key] for key in recurrent_actual_keys)

                    # Non Recurrent Expenditure Totals
                    expenditure_data["Non Recurrent Expenditure Total (BUDGET)"] = sum(expenditure_data[key] for key in [
                        "Capital Expenditure (BUDGET)", "Rehabilitation Fund (BUDGET)", 
                        "Loan Repayment (BUDGET)", "Any other capital expenditure (BUDGET)"
                    ])
                    expenditure_data["Non Recurrent Expenditure Actual (This Month)"] = sum(expenditure_data[key] for key in [
                        "Capital Expenditure (Actual)", "Rehabilitation Fund (Actual)", 
                        "Loan Repayment (Actual)", "Any other capital expenditure (Actual)"
                    ])

                    # Append expenditure data to the list
                    expenditure_data_list.append(pd.DataFrame([expenditure_data]))

                # Concatenate all revenue and expenditure DataFrames
                total_revenue_df = pd.concat(revenue_data_list, ignore_index=True)
                total_expenditure_df = pd.concat(expenditure_data_list, ignore_index=True)

                # Display cumulative revenues and expenditures
                st.write("### Cumulative Revenues")
                st.dataframe(total_revenue_df)
                st.write("### Cumulative Expenditures")
                st.dataframe(total_expenditure_df)

    # Closing the database connection
    cursor.close()
    db_connection.close()

    if st.button("Back"):
        navigate_to("LoGoMIS")

elif st.session_state.page == "Actual This Month":
    #Establishing the connection to the database
    db_connection = connect_to_db()
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

            # Sidebar for selecting Local Authority Type
            selected_local_authority_type = st.sidebar.selectbox("Select Local Authority Type", ["MC", "UC", "PS"])

            # Fetch local authorities for the selected type
            cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s AND type = %s", (district_id, selected_local_authority_type))
            local_authorities = cursor.fetchall()
            local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])

            # Fetch years for all local authorities of the selected type
            local_authority_ids = local_authorities_df['local_authority_id'].tolist()
            local_authority_names = local_authorities_df['local_authority_name'].tolist()

            # Sidebar for selecting Year
            cursor.execute("SELECT DISTINCT year FROM actual_budgets WHERE local_authority_id IN (%s)" % ','.join(map(str, local_authority_ids)))
            years = cursor.fetchall()
            years_df = pd.DataFrame(years, columns=["year"])
            year_list = years_df['year'].tolist()

            selected_year = st.sidebar.selectbox("Select a Year", year_list)
            if selected_year:

                # Map months to their corresponding numeric values
                month_mapping = {
                    "January": 1, "February": 2, "March": 3, "April": 4,
                    "May": 5, "June": 6, "July": 7, "August": 8,
                    "September": 9, "October": 10, "November": 11, "December": 12, "ANNUAL": 0,
                }

                # Sidebar for selecting Month
                selected_month_name = st.sidebar.selectbox("Select a Month", list(month_mapping.keys()))
                selected_month = month_mapping[selected_month_name]

                # Initialize DataFrames for revenues and expenditures with separated BUDGET and Actual columns
                revenue_columns = [
                    "Local Authority",
                    "Rate & Taxes (BUDGET)", "Rate & Taxes (Actual)",
                    "Rent (BUDGET)", "Rent (Actual)",
                    "License (BUDGET)", "License (Actual)",
                    "Fees for Service (BUDGET)", "Fees for Service (Actual)",
                    "Warrant Cost, Fine & Penalties (BUDGET)", "Warrant Cost, Fine & Penalties (Actual)",
                    "Other Revenue (BUDGET)", "Other Revenue (Actual)",
                    "Revenue Grants (All Salary related) (BUDGET)", "Revenue Grants (All Salary related) (Actual)",
                    "Revenue Grants (Other than Salary related) (BUDGET)", "Revenue Grants (Other than Salary related) (Actual)",

                    # New columns for recurrent revenue totals
                    "Recurrent Revenue Total (BUDGET)", "Recurrent Revenue Total (Actual)",

                    "Capital Grants (BUDGET)", "Capital Grants (Actual)",
                    "Capital Loans (BUDGET)", "Capital Loans (Actual)",
                    "Sale of Capital Assets (BUDGET)", "Sale of Capital Assets (Actual)",

                    "Any other capital receipts (BUDGET)", "Any other capital receipts (Actual)"
                ]
                total_revenue_df = pd.DataFrame(columns=revenue_columns)

                # Adding new columns for recurrent expenditure totals to expenditure_columns
                expenditure_columns = [
                    "Local Authority",
                    "Personal Emoluments (BUDGET)", "Personal Emoluments (Actual)",
                    "Traveling Expenses (BUDGET)", "Traveling Expenses (Actual)",
                    "Supplies & Requisites (BUDGET)", "Supplies & Requisites (Actual)",
                    "Repairs & Maintenance of Capital Assets (BUDGET)", "Repairs & Maintenance of Capital Assets (Actual)",
                    "Transportation Communication & Utility Service (BUDGET)", "Transportation Communication & Utility Service (Actual)",
                    "Interest Payments, Dividends (BUDGET)", "Interest Payments, Dividends (Actual)",
                    "Grants Contributions & Subsidies (BUDGET)", "Grants Contributions & Subsidies (Actual)",
                    "Pensions, Retirement Benefits & Gratuities (BUDGET)", "Pensions, Retirement Benefits & Gratuities (Actual)",
                
                    # New columns for recurrent expenditure totals
                    "Recurrent Expenditure Total (BUDGET)", 
                    "Recurrent Expenditure Actual (This Month)",

                    "Capital Expenditure (BUDGET)", "Capital Expenditure (Actual)",
                    "Rehabilitation Fund (BUDGET)", "Rehabilitation Fund (Actual)",
                    "Loan Repayment (BUDGET)", "Loan Repayment (Actual)",
                    
                    "Any other capital expenditure (BUDGET)", "Any other capital expenditure (Actual)"
                ]
                total_expenditure_df = pd.DataFrame(columns=expenditure_columns)

                for local_authority_id, local_authority_name in zip(local_authority_ids, local_authority_names):
                    # Initialize revenue data
                    revenue_data = {col: 0 for col in revenue_columns}
                    revenue_data["Local Authority"] = local_authority_name

                    expenditure_data = {col: 0 for col in expenditure_columns}
                    expenditure_data["Local Authority"] = local_authority_name

                    # Fetch and populate annual and actual data for revenue
                    cursor.execute("""
                    SELECT r.name, SUM(abd.total_amount) AS annual_total
                    FROM revenues r
                    JOIN annual_budget_details abd ON r.id = abd.revenue_id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s
                    GROUP BY r.name
                    """, (local_authority_id, selected_year))
                    annual_budget_revenue_data = cursor.fetchall()
                    for revenue_name, annual_total in annual_budget_revenue_data:
                        if f"{revenue_name} (BUDGET)" in revenue_data:
                            revenue_data[f"{revenue_name} (BUDGET)"] = annual_total

                    months_in_query = ', '.join([str(i) for i in range(1, selected_month + 1)])
                    cursor.execute(f"""
                    SELECT r.name, SUM(abd.total_amount) AS actual_total
                    FROM revenues r
                    JOIN actual_budget_details abd ON r.id = abd.revenue_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN ({months_in_query})
                    GROUP BY r.name
                    """, (local_authority_id, selected_year))
                    actual_revenue_data = cursor.fetchall()
                    for revenue_name, actual_total in actual_revenue_data:
                        if f"{revenue_name} (Actual)" in revenue_data:
                            revenue_data[f"{revenue_name} (Actual)"] = actual_total

                    # Calculate Recurrent Revenue Totals
                    recurrent_budget_keys = [
                        "Rate & Taxes (BUDGET)", "Rent (BUDGET)", "License (BUDGET)", "Fees for Service (BUDGET)",
                        "Warrant Cost, Fine & Penalties (BUDGET)", "Other Revenue (BUDGET)",
                        "Revenue Grants (All Salary related) (BUDGET)", "Revenue Grants (Other than Salary related) (BUDGET)"
                    ]
                    recurrent_actual_keys = [
                        "Rate & Taxes (Actual)", "Rent (Actual)", "License (Actual)", "Fees for Service (Actual)",
                        "Warrant Cost, Fine & Penalties (Actual)", "Other Revenue (Actual)",
                        "Revenue Grants (All Salary related) (Actual)", "Revenue Grants (Other than Salary related) (Actual)"
                    ]

                    revenue_data["Recurrent Revenue Total (BUDGET)"] = sum(revenue_data[key] for key in recurrent_budget_keys)
                    revenue_data["Recurrent Revenue Total (Actual)"] = sum(revenue_data[key] for key in recurrent_actual_keys)

                    # Add the populated row to total_revenue_df
                    total_revenue_df = pd.concat([total_revenue_df, pd.DataFrame([revenue_data])], ignore_index=True)

                    # Fetch and populate annual and actual data for expenditure
                    cursor.execute("""
                    SELECT e.name, SUM(abd.total_amount) AS annual_total
                    FROM expenditures e
                    JOIN annual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s
                    GROUP BY e.name
                    """, (local_authority_id, selected_year))
                    annual_budget_expenditure_data = cursor.fetchall()
                    for expenditure_name, annual_total in annual_budget_expenditure_data:
                        if f"{expenditure_name} (BUDGET)" in expenditure_data:
                            expenditure_data[f"{expenditure_name} (BUDGET)"] = annual_total

                    cursor.execute(f"""
                    SELECT e.name, SUM(abd.total_amount) AS actual_total
                    FROM expenditures e
                    JOIN actual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN ({months_in_query})
                    GROUP BY e.name
                    """, (local_authority_id, selected_year))
                    actual_expenditure_data = cursor.fetchall()
                    for expenditure_name, actual_total in actual_expenditure_data:
                        if f"{expenditure_name} (Actual)" in expenditure_data:
                            expenditure_data[f"{expenditure_name} (Actual)"] = actual_total

                    # Calculate Recurrent Expenditure Totals
                    recurrent_budget_keys = [
                        "Personal Emoluments (BUDGET)", "Traveling Expenses (BUDGET)", "Supplies & Requisites (BUDGET)",
                        "Repairs & Maintenance of Capital Assets (BUDGET)", "Transportation Communication & Utility Service (BUDGET)",
                        "Interest Payments, Dividends (BUDGET)", "Grants Contributions & Subsidies (BUDGET)",
                        "Pensions, Retirement Benefits & Gratuities (BUDGET)"
                    ]
                    recurrent_actual_keys = [
                        "Personal Emoluments (Actual)", "Traveling Expenses (Actual)", "Supplies & Requisites (Actual)",
                        "Repairs & Maintenance of Capital Assets (Actual)", "Transportation Communication & Utility Service (Actual)",
                        "Interest Payments, Dividends (Actual)", "Grants Contributions & Subsidies (Actual)",
                        "Pensions, Retirement Benefits & Gratuities (Actual)"
                    ]

                    expenditure_data["Recurrent Expenditure Total (BUDGET)"] = sum(expenditure_data[key] for key in recurrent_budget_keys)
                    expenditure_data["Recurrent Expenditure Actual (This Month)"] = sum(expenditure_data[key] for key in recurrent_actual_keys)

                    # Add the populated row to total_expenditure_df
                    total_expenditure_df = pd.concat([total_expenditure_df, pd.DataFrame([expenditure_data])], ignore_index=True)

                # Display updated revenue and expenditure tables
                st.subheader("Revenue Table")
                st.dataframe(total_revenue_df)

                st.subheader("Expenditure Table")
                st.dataframe(total_expenditure_df)

    # Close the database connection
    cursor.close()
    db_connection.close()

    if st.button("Back"):
        navigate_to("LoGoMIS")

elif st.session_state.page == "Budget Status":
    
    # Establishing the connection to the database
    db_connection = connect_to_db()
    cursor = db_connection.cursor()

    # Fetch provinces
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    provinces_df = pd.DataFrame(provinces, columns=["province_id", "province_name"])
    province_names = provinces_df['province_name'].tolist()

    # Sidebar for selecting Province
    st.sidebar.write("### Select Options")
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

            # Sidebar for selecting Local Authority Type
            selected_local_authority_type = st.sidebar.selectbox("Select Local Authority Type", ["MC", "UC", "PS"])

            # Fetch local authorities for the selected type
            cursor.execute("""
            SELECT id, name 
            FROM local_authorities 
            WHERE district_id = %s AND type = %s
            """, (district_id, selected_local_authority_type))
            local_authorities = cursor.fetchall()
            local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])

            # Fetch years for all local authorities of the selected type
            local_authority_ids = local_authorities_df['local_authority_id'].tolist()
            cursor.execute("""
            SELECT DISTINCT year 
            FROM annual_budgets 
            WHERE local_authority_id IN (%s)
            """ % ','.join(map(str, local_authority_ids)))
            years = cursor.fetchall()
            years_df = pd.DataFrame(years, columns=["year"])
            year_list = years_df['year'].tolist()

            # Sidebar for selecting Year
            selected_year = st.sidebar.selectbox("Select a Year", year_list)
            if selected_year:
                # Initialize the output table columns
                output_columns = [
                    "Province", "District", "Local Authority",
                    "Recurrent Revenue Total (BUDGET)", "Non Recurrent Revenue Total (BUDGET)",
                    "Recurrent Expenditure Total (BUDGET)", "Non Recurrent Expenditure Total (BUDGET)"
                ]
                output_df = pd.DataFrame(columns=output_columns)

                # Iterate over each local authority
                for local_authority_id, local_authority_name in zip(local_authority_ids, local_authorities_df['local_authority_name']):
                    # Initialize a row for this local authority
                    row = {
                        "Province": selected_province,
                        "District": selected_district,
                        "Local Authority": local_authority_name,
                        "Recurrent Revenue Total (BUDGET)": 0,
                        "Non Recurrent Revenue Total (BUDGET)": 0,
                        "Recurrent Expenditure Total (BUDGET)": 0,
                        "Non Recurrent Expenditure Total (BUDGET)": 0
                    }

                    # Fetch Recurrent Revenue Total (BUDGET)
                    cursor.execute("""
                    SELECT SUM(abd.total_amount)
                    FROM annual_budget_details abd
                    JOIN revenues r ON abd.revenue_id = r.id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s 
                    AND r.type = 'Recurrent'
                    """, (local_authority_id, selected_year))
                    result = cursor.fetchone()
                    row["Recurrent Revenue Total (BUDGET)"] = result[0] if result[0] else 0

                    # Fetch Non Recurrent Revenue Total (BUDGET)
                    cursor.execute("""
                    SELECT SUM(abd.total_amount)
                    FROM annual_budget_details abd
                    JOIN revenues r ON abd.revenue_id = r.id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s 
                    AND r.type = 'Non Recurrent'
                    """, (local_authority_id, selected_year))
                    result = cursor.fetchone()
                    row["Non Recurrent Revenue Total (BUDGET)"] = result[0] if result[0] else 0

                    # Fetch Recurrent Expenditure Total (BUDGET)
                    cursor.execute("""
                    SELECT SUM(abd.total_amount)
                    FROM annual_budget_details abd
                    JOIN expenditures e ON abd.expenditure_id = e.id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s 
                    AND e.type = 'Recurrent'
                    """, (local_authority_id, selected_year))
                    result = cursor.fetchone()
                    row["Recurrent Expenditure Total (BUDGET)"] = result[0] if result[0] else 0

                    # Fetch Non Recurrent Expenditure Total (BUDGET)
                    cursor.execute("""
                    SELECT SUM(abd.total_amount)
                    FROM annual_budget_details abd
                    JOIN expenditures e ON abd.expenditure_id = e.id
                    JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s 
                    AND e.type = 'Non Recurrent'
                    """, (local_authority_id, selected_year))
                    result = cursor.fetchone()
                    row["Non Recurrent Expenditure Total (BUDGET)"] = result[0] if result[0] else 0

                    # Append the row to the DataFrame
                    output_df = pd.concat([output_df, pd.DataFrame([row])], ignore_index=True)

                # Display the output table
                st.write("### Budget Overview")
                st.dataframe(output_df)

    # Close the database connection
    cursor.close()
    db_connection.close()

    if st.button("Back"):
        navigate_to("LoGoMIS")

elif st.session_state.page == "perfect schema":
    
    # Database connection function
    def connect_to_db():
        return mysql.connector.connect(
            host="170.64.176.75",
            user="vaitheki",
            password="Abcd@878172",
            database="PERFECT20"
        )

    # Function to fetch all table names from the database
    def get_table_names():
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        conn.close()
        return [table[0] for table in tables]

    # Function to fetch table schema (column names and data types)
    def get_table_schema(table_name):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        schema = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(schema, columns=["Field", "Type", "Null", "Key", "Default", "Extra"])

    # Function to fetch data from a selected table
    def get_table_data(table_name):
        conn = connect_to_db()
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    # Streamlit UI
    def main():
        st.title("Database Table Viewer")

        # Get list of table names
        tables = get_table_names()
        
        # Create a select box for users to choose a table
        table_name = st.selectbox("Select a table", tables)
        
        if table_name:
            # Display the schema of the selected table
            st.subheader(f"Schema of {table_name}")
            table_schema = get_table_schema(table_name)
            st.dataframe(table_schema)
            
            # Display the selected table's content
            st.subheader(f"Data from {table_name}")
            table_data = get_table_data(table_name)
            st.dataframe(table_data)

    if __name__ == "__main__":
        main()

    if st.button("Back"):
        navigate_to("LoGoMIS")

elif st.session_state.page == "response perfect":
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
        
    if st.button("Back"):
        navigate_to("LoGoMIS")