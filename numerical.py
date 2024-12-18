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

def fetch_months(year):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT month FROM actual_budgets WHERE year = %s", (year,))
    months = cursor.fetchall()
    conn.close()
    return [month[0] for month in months]

# Fetch revenue data sorted by revenue ID and limited to id <= 10
def fetch_revenue_data(district_id, la_type, year, month):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
        SELECT la.name AS local_authority, r.id AS revenue_id, r.name AS revenue_name, abd.total_amount AS annual_budget, ab.total_amount AS actual_budget
        FROM local_authorities la
        LEFT JOIN annual_budgets anb ON la.id = anb.local_authority_id
        LEFT JOIN annual_budget_details abd ON anb.id = abd.annual_budget_id
        LEFT JOIN revenues r ON abd.revenue_id = r.id
        LEFT JOIN actual_budgets acb ON la.id = acb.local_authority_id
        LEFT JOIN actual_budget_details ab ON acb.id = ab.actual_budget_id AND r.id = ab.revenue_id
        WHERE la.district_id = %s
        AND la.type = %s
        AND anb.year = %s
        AND acb.year = %s
        AND acb.month = %s
        AND r.id <= 10  -- Only include revenues with id <= 10
        ORDER BY r.id ASC  -- Sort by revenue ID
    """

    cursor.execute(query, (district_id, la_type, year, year, month))
    revenue_data = cursor.fetchall()
    conn.close()
    return revenue_data
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
month_options = ["Annual", "January", "February", "March", "April", "May", 
                 "June", "July", "August", "September", "October", "November", "December"]
selected_month = st.sidebar.selectbox("Select a Month", month_options)

# Convert selected month to corresponding numerical value
month_mapping = {
    "Annual":0,
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

# Fetching revenue data based on selected filters
revenue_data = fetch_revenue_data(district_id, la_type, selected_year, selected_month_value)

# Fetching expenditure data based on selected local authority type
expenditure_data = fetch_expenditure_data(district_id, la_type, selected_year, selected_month_value)


# Display revenue table if data exists
if revenue_data:
    st.subheader(f"Revenue Budget and Actual for {la_type} - {selected_year}/{selected_month_value}")

    # Restructure the table data
    revenue_local_authorities = [row[0] for row in revenue_data]
    revenue_ids = [row[1] for row in revenue_data]  # Include revenue IDs for sorting
    revenue_names = [row[2] for row in revenue_data]
    annual_budgets = [row[3] for row in revenue_data]
    actual_budgets = [row[4] for row in revenue_data]

    # Filter out None values from revenue_names
    revenue_headers = sorted(set(filter(None, revenue_names)), key=lambda x: revenue_ids[revenue_names.index(x)])  # Sort by revenue ID

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
        total_revenue_budget = 0  # Initialize total revenue budget
        total_actual_budget = 0  # Initialize total actual budget
        actual_budget_sum = 0  # Initialize total actual budget for this month
        capital_grants_budget = 0  # Initialize total Capital Grants (Annual)
        capital_loans_budget = 0  # Initialize total Capital Loans (Annual)
        capital_grants_actual = 0  # Initialize total Capital Grants (Actual)
        capital_loans_actual = 0  # Initialize total Capital Loans (Actual)

        for revenue_name in revenue_headers:
            # Append annual and actual budget for each revenue name
            if revenue_name in revenue_dict[la]:
                annual, actual = revenue_dict[la][revenue_name]
                total_revenue_budget += annual if annual else 0  # Summing up annual budgets
                total_actual_budget += actual if actual else 0  # Summing up actual budgets
                actual_budget_sum += actual if actual else 0  # Sum of actual budget for this month
                row.extend([annual, actual])

                # Capture totals for Capital Grants and Loans
                if revenue_name == 'Capital Grants':
                    capital_grants_budget = annual if annual else 0
                    capital_grants_actual = actual if actual else 0
                elif revenue_name == 'Capital Loans':
                    capital_loans_budget = annual if annual else 0
                    capital_loans_actual = actual if actual else 0
            else:
                row.extend([None, None])  # No data for this revenue type

        # Calculate Non Recurrent Budget
        non_recurrent_budget = capital_grants_budget + capital_loans_budget
        row.append(non_recurrent_budget)  # Append Non Recurrent Budget

        # Calculate Non Recurrent Actual for this month
        non_recurrent_actual = capital_grants_actual + capital_loans_actual
        row.append(non_recurrent_actual)  # Append Non Recurrent Actual for this month

        # Insert total revenue budget and actual budget before 'Capital Grants'
        if 'Capital Grants' in revenue_headers:
            capital_grants_index = revenue_headers.index('Capital Grants') * 2 + 1  # Multiply by 2 because each revenue has two columns (Annual & Actual)
            row.insert(capital_grants_index, total_revenue_budget)  # Insert the total revenue budget before Capital Grants
            row.insert(capital_grants_index + 1, actual_budget_sum)  # Insert total actual budget this month before Capital Grants
        else:
            row.insert(1, total_revenue_budget)  # Default to inserting after Local Authority if Capital Grants not found
            row.insert(2, actual_budget_sum)  # Default to inserting total actual budget this month after total revenue budget

        data.append(row)

    # Creating column headers with subheaders (Annual Budget, Actual Budget)
    columns = ['Local Authority']
    for revenue_name in revenue_headers:
        if revenue_name == 'Capital Grants':
            columns.append('Total Revenue Budget')  # Insert the Total Revenue Budget before Capital Grants
            columns.append('Total Actual Budget This Month')  # Insert the Total Actual Budget column
        columns.extend([f'{revenue_name} (Annual Budget)', f'{revenue_name} (Actual Budget)'])

    # Insert Non Recurrent Budget and Non Recurrent Actual at the end
    columns.append('Non Recurrent Budget')
    columns.append('Non Recurrent Actual This Month')

    # Create the DataFrame with the updated columns and data
    df = pd.DataFrame(data, columns=columns)
   # Apply styles to color the columns
    def style_specific_columns(x):
        light_blue = 'background-color: lightblue'
        brown = 'background-color: #A52A2A'  # Brown color
        df_styled = pd.DataFrame('', index=x.index, columns=x.columns)
       
        if 'Total Revenue Budget' in df.columns:
            df_styled['Total Revenue Budget'] = light_blue
        if 'Total Actual Budget This Month' in df.columns:
            df_styled['Total Actual Budget This Month'] = light_blue
        if 'Non Recurrent Budget' in df.columns:
            df_styled['Non Recurrent Budget'] = light_blue
        if 'Non Recurrent Actual This Month' in df.columns:
            df_styled['Non Recurrent Actual This Month'] = light_blue
       
        # Apply brown background to all Actual Budget columns
        for col in df.columns:
            if "(Actual Budget)" in col:
                df_styled[col] = 'background-color: burlywood'
               
       
        return df_styled

    st.write(df.style.apply(style_specific_columns, axis=None))  # Display the styled DataFrame
else:
    st.warning("No revenue data available for the selected filters.")

# Display expenditure table if data exists
if expenditure_data:
    st.subheader(f"Expenditure Budget and Actual for {la_type} - {selected_year}/{selected_month}")

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

    # Apply styles to color the specific columns
    styled_df = expenditure_df.style

    # Apply blue color to specific recurrent and non-recurrent columns
    styled_df = styled_df.applymap(
        lambda val: 'background-color: lightblue',
        subset=['Recurrent Expenditure Total Budget',
                'Recurrent Expenditure Actual Budget',
                'Non-recurrent Expenditure Total Budget',
                'Non-recurrent Expenditure Actual Budget']
    )

    # Apply brown color to all columns with "Actual Budget" in the header
    actual_budget_columns = [col for col in columns if "(Actual Budget)" in col]
    styled_df = styled_df.applymap(
        lambda val: 'background-color: burlywood',  # Burlywood is a shade of brown
        subset=actual_budget_columns
    )

    # Display the styled DataFrame
    st.dataframe(styled_df)
else:
    st.write("No expenditure data available for the selected filters.")