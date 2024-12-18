import pandas as pd
import streamlit as st
import mysql.connector


# Function to connect to the database
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )


# Establish database connection
db_connection = connect_to_db()
cursor = db_connection.cursor()

# Fetch provinces
cursor.execute("SELECT id, name FROM provinces")
provinces = cursor.fetchall()
provinces_df = pd.DataFrame(provinces, columns=["province_id", "province_name"])
province_names = provinces_df['province_name'].tolist()

# Streamlit UI
st.write("### Budget Status")
selected_province = st.sidebar.selectbox("Select a Province", province_names)

if selected_province:
    province_id = int(provinces_df[provinces_df['province_name'] == selected_province]['province_id'].values[0])

    # Fetch districts
    cursor.execute("SELECT id, name FROM districts WHERE province_id = %s", (province_id,))
    districts = cursor.fetchall()
    districts_df = pd.DataFrame(districts, columns=["district_id", "district_name"])
    district_names = districts_df['district_name'].tolist()

    selected_district = st.sidebar.selectbox("Select a District", district_names)
    if selected_district:
        district_id = int(districts_df[districts_df['district_name'] == selected_district]['district_id'].values[0])

        # Fetch all local authorities (no type filtering)
        cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s", (district_id,))
        local_authorities = cursor.fetchall()
        local_authorities_df = pd.DataFrame(local_authorities, columns=["local_authority_id", "local_authority_name"])

        local_authority_ids = local_authorities_df['local_authority_id'].tolist()
        local_authority_names = local_authorities_df['local_authority_name'].tolist()

        # Year selection
        cursor.execute("SELECT DISTINCT year FROM actual_budgets WHERE local_authority_id IN (%s)" %
                       ','.join(map(str, local_authority_ids)))
        years = cursor.fetchall()
        years_df = pd.DataFrame(years, columns=["year"])
        year_list = years_df['year'].tolist()

        selected_year = st.sidebar.selectbox("Select a Year", year_list)
        if selected_year:

            # Month selection
            month_mapping = {
                "ANNUAL": 0, "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }


            # Create an empty dataframe for combined data
            combined_columns = [
                "Province", "District", "Local Authority",
                "Recurrent Revenue Total (BUDGET)", "Non Recurrent Revenue Total (BUDGET)",
                "Recurrent Expenditure Total (BUDGET)", "Non Recurrent Expenditure Total (BUDGET)",
                "Total Recurrent (Revenue - Expenditure)", "Total (Revenue - Expenditure)"
            ]
            combined_df = pd.DataFrame(columns=combined_columns)

            for local_authority_id, local_authority_name in zip(local_authority_ids, local_authority_names):
                # Initialize data
                combined_data = {
                    "Province": selected_province,
                    "District": selected_district,
                    "Local Authority": local_authority_name,
                    "Recurrent Revenue Total (BUDGET)": 0,
                    "Non Recurrent Revenue Total (BUDGET)": 0,
                    "Recurrent Expenditure Total (BUDGET)": 0,
                    "Non Recurrent Expenditure Total (BUDGET)": 0,
                    "Total Recurrent (Revenue - Expenditure)": 0,
                    "Total (Revenue - Expenditure)": 0
                }

                # Fetch revenue data
                cursor.execute(""" 
                SELECT r.name, SUM(abd.total_amount) AS annual_total
                FROM revenues r
                JOIN annual_budget_details abd ON r.id = abd.revenue_id
                JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                WHERE ab.local_authority_id = %s AND ab.year = %s
                GROUP BY r.name
                """, (local_authority_id, selected_year))
                revenue_data = cursor.fetchall()

                for revenue_name, annual_total in revenue_data:
                    if revenue_name in [
                        "Rate & Taxes", "Rent", "License", "Fees for Service",
                        "Warrant Cost, Fine & Penalties", "Other Revenue",
                        "Revenue Grants (All Salary related)", "Revenue Grants (Other than Salary related)"
                    ]:
                        combined_data["Recurrent Revenue Total (BUDGET)"] += annual_total
                    elif revenue_name in [
                        "Capital Grants", "Capital Loans", "Sale of Capital Assets", "Any other capital receipts"
                    ]:
                        combined_data["Non Recurrent Revenue Total (BUDGET)"] += annual_total

                # Fetch expenditure data
                cursor.execute(""" 
                SELECT e.name, SUM(abd.total_amount) AS annual_total
                FROM expenditures e
                JOIN annual_budget_details abd ON e.id = abd.expenditure_id
                JOIN annual_budgets ab ON abd.annual_budget_id = ab.id
                WHERE ab.local_authority_id = %s AND ab.year = %s
                GROUP BY e.name
                """, (local_authority_id, selected_year))
                expenditure_data = cursor.fetchall()

                for expenditure_name, annual_total in expenditure_data:
                    if expenditure_name in [
                        "Personal Emoluments", "Traveling Expenses", "Supplies & Requisites",
                        "Repairs & Maintenance of Capital Assets",
                        "Transportation Communication & Utility Service",
                        "Interest Payments, Dividends", "Grants Contributions & Subsidies",
                        "Pensions, Retirement Benefits & Gratuities"
                    ]:
                        combined_data["Recurrent Expenditure Total (BUDGET)"] += annual_total
                    elif expenditure_name in [
                        "Capital Expenditure", "Rehabilitation Fund", "Loan Repayment",
                        "Any other capital expenditure"
                    ]:
                        combined_data["Non Recurrent Expenditure Total (BUDGET)"] += annual_total

                # Calculate the new columns: Total Recurrent and Total (Revenue - Expenditure)
                combined_data["Total Recurrent (Revenue - Expenditure)"] = (
                    combined_data["Recurrent Revenue Total (BUDGET)"] - combined_data["Recurrent Expenditure Total (BUDGET)"]
                )
                combined_data["Total (Revenue - Expenditure)"] = (
                    combined_data["Recurrent Revenue Total (BUDGET)"] + combined_data["Non Recurrent Revenue Total (BUDGET)"]
                    - combined_data["Recurrent Expenditure Total (BUDGET)"] - combined_data["Non Recurrent Expenditure Total (BUDGET)"]
                )

                # Append to combined dataframe using pd.concat
                combined_df = pd.concat([combined_df, pd.DataFrame([combined_data])], ignore_index=True)

            # Display the final table
            st.write("### Combined Revenue and Expenditure Data")
            st.dataframe(combined_df)

# Close the database connection
cursor.close()
db_connection.close()
