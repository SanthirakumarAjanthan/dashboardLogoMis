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
                    "Annual Budget": 0, "January": 1, "February": 2, "March": 3, "April": 4,
                    "May": 5, "June": 6, "July": 7, "August": 8,
                    "September": 9, "October": 10, "November": 11, "December": 12
                }

                # Sidebar for selecting Month
                selected_month_name = st.sidebar.selectbox("Select a Month", list(month_mapping.keys()))
                selected_month = month_mapping[selected_month_name]

                # Create dynamic column names based on the selected month
                month_names = list(month_mapping.keys())[1:13]  # For all months (January to December)
                revenue_columns = ["Revenue Name"] + [f"{month} Total Amount" for month in month_names] + ["Sum Total Amount"]
                expenditure_columns = ["Expenditure Name"] + [f"{month} Total Amount" for month in month_names] + ["Sum Total Amount"]

                if selected_month == 0:  # Annual Budget case
                    # Fetch the total amounts for all months (January to December)
                    month_cases = ', '.join([f"SUM(CASE WHEN ab.month = {i} THEN abd.total_amount ELSE 0 END) AS {list(month_mapping.keys())[i]}_total"
                                             for i in range(1, 13)])

                    query_revenue = f"""
                    SELECT r.name, {month_cases}, SUM(abd.total_amount) AS sum_total
                    FROM revenues r
                    JOIN actual_budget_details abd ON r.id = abd.revenue_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
                    GROUP BY r.name
                    """
                    cursor.execute(query_revenue, (local_authority_id, selected_year))
                    all_revenue_data = cursor.fetchall()
                    all_revenue_df = pd.DataFrame(all_revenue_data, columns=revenue_columns)

                    query_expenditure = f"""
                    SELECT e.name, {month_cases}, SUM(abd.total_amount) AS sum_total
                    FROM expenditures e
                    JOIN actual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
                    GROUP BY e.name
                    """
                    cursor.execute(query_expenditure, (local_authority_id, selected_year))
                    expenditure_data = cursor.fetchall()
                    expenditure_df = pd.DataFrame(expenditure_data, columns=expenditure_columns)

                    st.subheader(f"Revenue and Expenditure Details for Annual Budget {selected_year}")
                    st.dataframe(all_revenue_df)
                    st.dataframe(expenditure_df)

                else:
                    # Generate dynamic query for the selected month and previous months
                    months_in_query = ', '.join([str(i) for i in range(1, selected_month + 1)])
                    month_cases = ', '.join([f"SUM(CASE WHEN ab.month = {i} THEN abd.total_amount ELSE 0 END) AS {list(month_mapping.keys())[i]}_total"
                                             for i in range(1, selected_month + 1)])

                    query_revenue = f"""
                    SELECT r.name, {month_cases}, SUM(abd.total_amount) AS sum_total
                    FROM revenues r
                    JOIN actual_budget_details abd ON r.id = abd.revenue_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN ({months_in_query})
                    GROUP BY r.name
                    """
                    cursor.execute(query_revenue, (local_authority_id, selected_year))
                    all_revenue_data = cursor.fetchall()
                    all_revenue_df = pd.DataFrame(all_revenue_data, columns=["Revenue Name"] + [f"{list(month_mapping.keys())[i]} Total Amount" for i in range(1, selected_month + 1)] + ["Sum Total Amount"])

                    query_expenditure = f"""
                    SELECT e.name, {month_cases}, SUM(abd.total_amount) AS sum_total
                    FROM expenditures e
                    JOIN actual_budget_details abd ON e.id = abd.expenditure_id
                    JOIN actual_budgets ab ON abd.actual_budget_id = ab.id
                    WHERE ab.local_authority_id = %s AND ab.year = %s AND ab.month IN ({months_in_query})
                    GROUP BY e.name
                    """
                    cursor.execute(query_expenditure, (local_authority_id, selected_year))
                    expenditure_data = cursor.fetchall()
                    expenditure_df = pd.DataFrame(expenditure_data, columns=["Expenditure Name"] + [f"{list(month_mapping.keys())[i]} Total Amount" for i in range(1, selected_month + 1)] + ["Sum Total Amount"])

                    st.subheader(f"Revenue Details for {selected_month_name} {selected_year}")
                    st.dataframe(all_revenue_df)
                    st.subheader(f"Expenditure Details for {selected_month_name} {selected_year}")
                    st.dataframe(expenditure_df)

# Close the database connection
cursor.close()
db_connection.close()
