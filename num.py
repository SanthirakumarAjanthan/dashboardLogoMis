import streamlit as st
import mysql.connector
import pandas as pd

# Database connection function
def connect_to_db():
    return mysql.connector.connect(
        host="170.64.176.75",
        user="ajanthan",
        password="Abcd@9920",
        database="LA_ANALYSIS"
    )

# Fetch data functions
def fetch_provinces():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM provinces")
    provinces = cursor.fetchall()
    conn.close()
    return provinces

def fetch_districts(province_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM districts WHERE province_id = %s", (province_id,))
    districts = cursor.fetchall()
    conn.close()
    return districts

def fetch_years():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT year FROM actual_budgets")
    years = cursor.fetchall()
    conn.close()
    return [year[0] for year in years]

def fetch_revenue_data(district_id, year, month):
    conn = connect_to_db()
    cursor = conn.cursor()

    if month is not None:
        # If a specific month is selected, fetch actual budgets for that month
        query = """
            SELECT 
                la.name AS local_authority, 
                r.id AS revenue_id, 
                r.name AS revenue_name, 
                abd.total_amount AS annual_budget,
                ab.total_amount AS actual_budget
            FROM local_authorities la
            LEFT JOIN annual_budgets anb ON la.id = anb.local_authority_id
            LEFT JOIN annual_budget_details abd ON anb.id = abd.annual_budget_id
            LEFT JOIN revenues r ON abd.revenue_id = r.id
            LEFT JOIN actual_budgets acb ON la.id = acb.local_authority_id
            LEFT JOIN actual_budget_details ab ON acb.id = ab.actual_budget_id AND r.id = ab.revenue_id
            WHERE la.district_id = %s
            AND anb.year = %s
            AND acb.year = %s
            AND acb.month = %s
            AND r.id <= 10 
            GROUP BY la.name, r.id, r.name, abd.total_amount, ab.total_amount
            ORDER BY r.id ASC
        """
        cursor.execute(query, (district_id, year, year, month))
    else:
        # Fetch annual budget data
        query = """
            SELECT 
                la.name AS local_authority, 
                r.id AS revenue_id, 
                r.name AS revenue_name, 
                abd.total_amount AS annual_budget,
                SUM(ab.total_amount) AS actual_budget
            FROM local_authorities la
            LEFT JOIN annual_budgets anb ON la.id = anb.local_authority_id
            LEFT JOIN annual_budget_details abd ON anb.id = abd.annual_budget_id
            LEFT JOIN revenues r ON abd.revenue_id = r.id
            LEFT JOIN actual_budgets acb ON la.id = acb.local_authority_id
            LEFT JOIN actual_budget_details ab ON acb.id = ab.actual_budget_id AND r.id = ab.revenue_id
            WHERE la.district_id = %s
            AND anb.year = %s
            AND acb.year = %s
            AND r.id <= 10 
            GROUP BY la.name, r.id, r.name, abd.total_amount
            ORDER BY r.id ASC
        """
        cursor.execute(query, (district_id, year, year))
    
    revenue_data = cursor.fetchall()
    conn.close()
    return revenue_data

# Sidebar Layout for filters
st.sidebar.title("Filters")

# Dropdown for selecting province
provinces = fetch_provinces()
province_names = [province[1] for province in provinces]
selected_province = st.sidebar.selectbox("Select a Province", province_names)

# Get province ID
province_id = next(province[0] for province in provinces if province[1] == selected_province)

# Dropdown for selecting district
districts = fetch_districts(province_id)
district_names = [district[1] for district in districts]
selected_district = st.sidebar.selectbox("Select a District", district_names)

# Get district ID
district_id = next(district[0] for district in districts if district[1] == selected_district)

# Dropdown for selecting year
years = fetch_years()
selected_year = st.sidebar.selectbox("Select a Year", years)

# Dropdown for selecting month (0 - Annual Budget, 1 - January, ..., 12 - December)
month_options = ["Annual Budget", "January", "February", "March", "April", "May", 
                 "June", "July", "August", "September", "October", "November", "December"]
selected_month = st.sidebar.selectbox("Select a Month", month_options)

# Convert selected month to corresponding numerical value
month_mapping = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}
selected_month_value = month_mapping.get(selected_month, None)  # None if "Annual Budget"

# Fetch data for revenue based on user selections
revenue_data = fetch_revenue_data(district_id, selected_year, selected_month_value)

# Display revenue table if data exists
if revenue_data:
    st.subheader(f"Revenue Budget and Actual for {selected_year}/{selected_month}")

    # Restructure the table data
    revenue_local_authorities = [row[0] for row in revenue_data]
    revenue_ids = [row[1] for row in revenue_data]  # Include revenue IDs for sorting
    revenue_names = [row[2] for row in revenue_data]
    annual_budgets = [row[3] for row in revenue_data]
    actual_budgets = [row[4] for row in revenue_data]

    # Define the recurrent revenue types to be summed
    recurrent_revenue_types = [
        'Rate & Taxes', 'Rent', 'License', 'Fees for Service', 
        'Warrant Cost, Fine & Penalties', 'Other Revenue', 
        'Revenue Grants (All Salary related)', 
        'Revenue Grants (Other than Salary related)'
    ]

    # Filter out None values from revenue_names
    revenue_headers = sorted(set(filter(None, revenue_names)), key=lambda x: revenue_ids[revenue_names.index(x)])  # Sort by revenue ID

    # Find the index of the "Revenue Grants (Other than Salary related)" column
    index_after_grants = revenue_headers.index("Revenue Grants (Other than Salary related)") + 1

    # Create a dictionary for easy lookup of revenue data
    revenue_dict = {}
    for row in revenue_data:
        la, revenue_id, revenue_name, annual, actual = row
        if la not in revenue_dict:
            revenue_dict[la] = {}
        revenue_dict[la][revenue_name] = (annual, actual)

    # Create a DataFrame with the desired structure
    data = []
    for la in sorted(set(revenue_local_authorities)):
        row = [la]  # First column is the local authority name
        total_annual_recurrent = 0
        total_actual_recurrent = 0

        for revenue_name in revenue_headers:
            # Append annual and actual budget for each revenue name
            if revenue_name in revenue_dict[la]:
                annual, actual = revenue_dict[la][revenue_name]
                row.extend([annual, actual])  # Add annual and actual budget alternately
                # Sum up the recurrent revenue types, treating None as 0
                total_annual_recurrent += (annual if annual is not None else 0)
                total_actual_recurrent += (actual if actual is not None else 0)
            else:
                row.extend([None, None])  # No data for this revenue type

        # Insert recurrent totals after the "Revenue Grants (Other than Salary related)" actual
        row = row[:index_after_grants * 2] + [total_annual_recurrent, total_actual_recurrent] + row[index_after_grants * 2:]

        data.append(row)

    # Creating column headers with subheaders (Annual Budget, Actual Budget)
    columns = ['Local Authority']
    for revenue_name in revenue_headers:
        columns.extend([f"{revenue_name} Annual", f"{revenue_name} Actual"])

    # Insert Recurrent Revenue totals right after "Revenue Grants (Other than Salary related)"
    columns = columns[:index_after_grants * 2] + ['Recurrent Revenue Total Budget', 'Recurrent Revenue Total Actual'] + columns[index_after_grants * 2:]

    # Create the final DataFrame
    revenue_df = pd.DataFrame(data, columns=columns)

    # Add rows for the total revenue after "Revenue Grants (Other than Salary related)" actual
    total_row = ['Total']  # Row for total budget and actual
    for revenue_name in revenue_headers:
        if revenue_name in recurrent_revenue_types:
            # Total Annual, treating None as 0
            total_annual = sum((row[i] if row[i] is not None else 0) for row in data for i in range(1, len(row), 2) if revenue_names[i // 2] == revenue_name)  
            total_actual = sum((row[i + 1] if row[i + 1] is not None else 0) for row in data for i in range(1, len(row), 2) if revenue_names[i // 2] == revenue_name)  
            total_row.append(total_annual)  # Total Annual
            total_row.append(total_actual)   # Total Actual
        else:
            total_row.extend([None, None])  # No total for non-recurrent revenue types

    # Insert total row after the specified location
    data.append(total_row)  # Append the total row at the end

    # Adding the new headings "Revenue Total Budget" and "Revenue Total Actual"
    revenue_total_row = [None] * (len(columns) - 2) + ['Revenue Total Budget', 'Revenue Total Actual']
    data.append(revenue_total_row)  # Append the revenue totals row after the totals row

    # Update the DataFrame with total values
    revenue_df = pd.DataFrame(data, columns=columns)

    # Display the final DataFrame
    st.table(revenue_df)
else:
    st.subheader("No data found for the selected filters.")
