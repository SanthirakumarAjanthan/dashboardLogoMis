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
