import pandas as pd
import streamlit as st
import mysql.connector

def connect_to_db():
    # Replace with your actual database connection details
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

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
                    "Actual Budget": 0, "January": 1, "February": 2, "March": 3, "April": 4,
                    "May": 5, "June": 6, "July": 7, "August": 8,
                    "September": 9, "October": 10, "November": 11, "December": 12
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

                    st.subheader("Total Actual Budget")
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
