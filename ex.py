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

def fetch_local_authorities(district_id, la_type):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM local_authorities WHERE district_id = %s AND type = %s", (district_id, la_type))
    local_authorities = cursor.fetchall()
    conn.close()
    return local_authorities

def fetch_years():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT year FROM actual_budgets")
    years = cursor.fetchall()
    conn.close()
    return [year[0] for year in years]

def fetch_months(year):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT month FROM actual_budgets WHERE year = %s", (year,))
    months = cursor.fetchall()
    conn.close()
    return [month[0] for month in months]

# Fetch expenditure data filtered by expenditure ID <= 11
def fetch_expenditure_data(district_id, la_type, year, month):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT la.name AS local_authority, e.id AS expenditure_id, e.name AS expenditure_name, 
               abd.total_amount AS annual_budget, ab.total_amount AS actual_budget
        FROM local_authorities la
        LEFT JOIN annual_budgets anb ON la.id = anb.local_authority_id
        LEFT JOIN annual_budget_details abd ON anb.id = abd.annual_budget_id
        LEFT JOIN expenditures e ON abd.expenditure_id = e.id
        LEFT JOIN actual_budgets acb ON la.id = acb.local_authority_id
        LEFT JOIN actual_budget_details ab ON acb.id = ab.actual_budget_id AND e.id = ab.expenditure_id
        WHERE la.district_id = %s
        AND la.type = %s
        AND anb.year = %s
        AND acb.year = %s
        AND acb.month = %s
        AND e.id <= 11  -- Only include expenditures with id <= 11
        ORDER BY e.id ASC  -- Sort by expenditure ID
    """

    cursor.execute(query, (district_id, la_type, year, year, month))
    expenditure_data = cursor.fetchall()
    conn.close()
    return expenditure_data

# Calculate non-recurrent expenditures
def calculate_non_recurrent(expenditure_data):
    total_budget = 0
    total_actual = 0
    non_recurrent_expenditure_types = ['Capital Expenditure', 'Rehabilitation Fund', 'Loan Repayment']
    
    for row in expenditure_data:
        expenditure_name = row[2]
        annual_budget = row[3] if row[3] is not None else 0
        actual_budget = row[4] if row[4] is not None else 0
        
        if expenditure_name in non_recurrent_expenditure_types:
            total_budget += annual_budget
            total_actual += actual_budget
    
    return total_budget, total_actual

# Calculate recurrent expenditures
def calculate_recurrent(expenditure_data):
    total_budget = 0
    total_actual = 0
    recurrent_expenditure_types = [
        'Personal Emoluments', 
        'Traveling Expenses', 
        'Supplies & Requisites', 
        'Repairs & Maintenance of Capital Assets', 
        'Transportation Communication & Utility Service', 
        'Interest Payments', 
        'Dividends', 
        'Grants Contributions & Subsidies', 
        'Pensions', 
        'Retirement Benefits & Gratuities'
    ]
    
    for row in expenditure_data:
        expenditure_name = row[2]
        annual_budget = row[3] if row[3] is not None else 0
        actual_budget = row[4] if row[4] is not None else 0
        
        if expenditure_name in recurrent_expenditure_types:
            total_budget += annual_budget
            total_actual += actual_budget
    
    return total_budget, total_actual

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

# Dropdown for selecting local authority type
la_type = st.sidebar.selectbox("Select Local Authority Type", ["MC", "UC", "PS"])

# Dropdown for selecting year
years = fetch_years()
selected_year = st.sidebar.selectbox("Select a Year", years)

# Dropdown for selecting month (0 - Annual Budget, 1 - January, ..., 12 - December)
month_options = ["Annual Budget", "January", "February", "March", "April", "May", 
                 "June", "July", "August", "September", "October", "November", "December"]
selected_month_index = st.sidebar.selectbox("Select a Month", list(range(len(month_options))), format_func=lambda x: month_options[x])

# Determine the month number (0-12)
if selected_month_index == 0:
    selected_month = None  # For Annual Budget, set month to None or handle accordingly
else:
    selected_month = selected_month_index  # Month as per the selection (1-12)

# Fetching expenditure data based on selected local authority type
expenditure_data = fetch_expenditure_data(district_id, la_type, selected_year, selected_month)

# Display expenditure table if data exists
if expenditure_data:
    st.subheader(f"Expenditure Budget and Actual for {la_type} - {selected_year}/{month_options[selected_month_index]}")

    # Restructure the table data
    expenditure_local_authorities = [row[0] for row in expenditure_data]
    expenditure_ids = [row[1] for row in expenditure_data]  # Include expenditure IDs for sorting
    expenditure_names = [row[2] for row in expenditure_data]
    annual_budgets = [row[3] for row in expenditure_data]
    actual_budgets = [row[4] for row in expenditure_data]

    # Filter out None values from expenditure_names
    expenditure_headers = sorted(set(filter(None, expenditure_names)), key=lambda x: expenditure_ids[expenditure_names.index(x)])  # Sort by expenditure ID

    # Create a dictionary for easy lookup of expenditure data
    expenditure_dict = {}
    for row in expenditure_data:
        la, expenditure_id, expenditure_name, annual, actual = row
        if la not in expenditure_dict:
            expenditure_dict[la] = {}
        expenditure_dict[la][expenditure_name] = (annual, actual)

    # Create a DataFrame with the desired structure
    data = []
    for la in sorted(set(expenditure_local_authorities)):
        row = [la]  # First column is the local authority name

        for expenditure_name in expenditure_headers:
            # Append annual and actual budget for each expenditure name
            if expenditure_name in expenditure_dict[la]:
                annual, actual = expenditure_dict[la][expenditure_name]
                row.extend([annual, actual])
            else:
                row.extend([None, None])  # No data for this expenditure type

        # Calculate recurrent expenditure totals
        recurrent_budget, recurrent_actual = calculate_recurrent(expenditure_data)
        
        # Insert recurrent totals after the 17th column, which corresponds to "Pensions, Retirement Benefits & Gratuities (Actual Budget)"
        row.insert(17, recurrent_actual)
        row.insert(17, recurrent_budget)

        # Calculate non-recurrent expenditure totals
        non_recurrent_budget, non_recurrent_actual = calculate_non_recurrent(expenditure_data)
        row.extend([non_recurrent_budget, non_recurrent_actual])  # Add non-recurrent totals to the row

        data.append(row)

    # Creating column headers with subheaders (Annual Budget, Actual Budget)
    columns = ['Local Authority']
    
    for expenditure_name in expenditure_headers:
        columns.extend([f'{expenditure_name} (Annual Budget)', f'{expenditure_name} (Actual Budget)'])

    # Adding new columns for Non-recurrent Expenditure
    columns.insert(17, 'Recurrent Expenditure Actual Budget')
    columns.insert(17, 'Recurrent Expenditure Total Budget')
    columns.extend(['Non-recurrent Expenditure Total Budget', 'Non-recurrent Expenditure Actual Budget'])

    expenditure_df = pd.DataFrame(data, columns=columns)

    # Display the Expenditure DataFrame
    st.table(expenditure_df)
else:
    st.write("No expenditure data available for the selected filters.")