import pandas as pd
import streamlit as st
import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

# Establishing the connection to the database
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