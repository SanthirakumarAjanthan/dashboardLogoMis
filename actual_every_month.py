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
                    "Annual": 0, "January": 1, "February": 2, "March": 3, "April": 4,
                    "May": 5, "June": 6, "July": 7, "August": 8,
                    "September": 9, "October": 10, "November": 11, "December": 12
                }

                # Sidebar for selecting Month
                selected_month_name = st.sidebar.selectbox("Select a Month", list(month_mapping.keys()))
                selected_month = month_mapping[selected_month_name]

                revenue_columns = ["Revenue Name", "Total Amount"]
                expenditure_columns = ["Expenditure Name", "Total Amount"]

                if selected_month == 0:
                    # Fetch sum of total_amount for all months (Jan to Dec) for revenue IDs 1 to 33
                    query_revenue = """
                    SELECT r.name, SUM(abd.total_amount) AS total_amount
                    FROM revenues r
                    JOIN actual_budget_details abd ON r.id = abd.revenue_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
                    AND r.id BETWEEN 1 AND 33
                    GROUP BY r.name
                    """
                    cursor.execute(query_revenue, (local_authority_id, selected_year))
                    all_revenue_data = cursor.fetchall()
                    all_revenue_df = pd.DataFrame(all_revenue_data, columns=revenue_columns)
                    
                    # Fetch Expenditure Details for the whole year
                    query_expenditure = """
                    SELECT e.name, SUM(abd.total_amount) AS total_amount
                    FROM expenditures e
                    JOIN actual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
                    GROUP BY e.name
                    """
                    cursor.execute(query_expenditure, (local_authority_id, selected_year))
                    expenditure_data = cursor.fetchall()
                    expenditure_df = pd.DataFrame(expenditure_data, columns=expenditure_columns)

                    st.subheader("Total Actual Budget (January to December) - Revenues 1 to 33")
                    st.dataframe(all_revenue_df)
                    st.dataframe(expenditure_df)
                else:
                    # Fetch total_amount for the selected month for revenue IDs 1 to 33
                    query_revenue = """
                    SELECT r.name, abd.total_amount
                    FROM revenues r
                    JOIN actual_budget_details abd ON r.id = abd.revenue_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month = %s
                    AND r.id BETWEEN 1 AND 33
                    """
                    cursor.execute(query_revenue, (local_authority_id, selected_year, selected_month))
                    all_revenue_data = cursor.fetchall()
                    all_revenue_df = pd.DataFrame(all_revenue_data, columns=revenue_columns)

                    # Fetch Expenditure Details for the selected month
                    query_expenditure = """
                    SELECT e.name, abd.total_amount
                    FROM expenditures e
                    JOIN actual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month = %s
                    """
                    cursor.execute(query_expenditure, (local_authority_id, selected_year, selected_month))
                    expenditure_data = cursor.fetchall()
                    expenditure_df = pd.DataFrame(expenditure_data, columns=expenditure_columns)

                    st.subheader(f"Revenue Details for {selected_month_name} {selected_year} - Revenues 1 to 33")
                    st.dataframe(all_revenue_df)
                    st.subheader(f"Expenditure Details for {selected_month_name} {selected_year}")
                    st.dataframe(expenditure_df)

# Close the database connection
cursor.close()
db_connection.close()
