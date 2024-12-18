import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Configure the WebDriver to automatically use the correct driver
@st.cache_resource
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for Streamlit sharing compatibility

    # Use Service to provide the path to the chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

driver = create_driver()

# URL to scrape
url = "https://iwms.wbb.gov.lk/household/list"
driver.get(url)

# Wait for the page to load using WebDriverWait
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "provinceID")))
    st.write("Page loaded successfully")
except Exception as e:
    st.error(f"Error loading page: {e}")

# Extract dropdown values (e.g., Province, District, Division, GN Division)
def get_dropdown_options():
    dropdown_data = {}

    try:
        # Province dropdown
        province_dropdown = Select(driver.find_element(By.ID, "provinceID"))
        province_options = [option.text for option in province_dropdown.options]
        dropdown_data['Province'] = province_options

        # Initialize empty dropdowns
        dropdown_data['District'] = []
        dropdown_data['Division'] = []
        dropdown_data['GN Division'] = []

    except Exception as e:
        st.error(f"Error fetching dropdown options: {e}")

    return dropdown_data

dropdown_data = get_dropdown_options()

# Display Province dropdown
province = st.selectbox("Select Province", dropdown_data['Province'])

# Update District dropdown based on the selected Province
if province:
    try:
        # Fetch and select districts based on the selected province
        Select(driver.find_element(By.ID, "provinceID")).select_by_visible_text(province)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "districtID")))
        district_dropdown = Select(driver.find_element(By.ID, "districtID"))
        district_options = [option.text for option in district_dropdown.options]
        dropdown_data['District'] = district_options
    except Exception as e:
        st.error(f"Error fetching districts: {e}")

district = st.selectbox("Select District", dropdown_data['District'])

# Update Divisional Secretariat Division dropdown based on the selected District
if district:
    try:
        # Fetch and select divisions based on the selected district
        Select(driver.find_element(By.ID, "districtID")).select_by_visible_text(district)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "divisionID")))
        division_dropdown = Select(driver.find_element(By.ID, "divisionID"))
        division_options = [option.text for option in division_dropdown.options]
        dropdown_data['Division'] = division_options
    except Exception as e:
        st.error(f"Error fetching divisions: {e}")

division = st.selectbox("Select Division", dropdown_data['Division'])

# Update GN Division dropdown based on the selected Divisional Secretariat Division
if division:
    try:
        # Fetch and select GN divisions based on the selected division
        Select(driver.find_element(By.ID, "divisionID")).select_by_visible_text(division)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gndID")))
        gn_dropdown = Select(driver.find_element(By.ID, "gndID"))
        gn_options = [option.text for option in gn_dropdown.options]
        dropdown_data['GN Division'] = gn_options
    except Exception as e:
        st.error(f"Error fetching GN divisions: {e}")

gn_division = st.selectbox("Select GN Division", dropdown_data['GN Division'])

# Trigger search on the website based on selections
if st.button("Fetch Data"):
    try:
        # Select values in the dropdowns
        Select(driver.find_element(By.ID, "provinceID")).select_by_visible_text(province)
        Select(driver.find_element(By.ID, "districtID")).select_by_visible_text(district)
        Select(driver.find_element(By.ID, "divisionID")).select_by_visible_text(division)
        Select(driver.find_element(By.ID, "gndID")).select_by_visible_text(gn_division)

        # Click the "View Registry" button
        view_button = driver.find_element(By.XPATH, "//button[@name='action'][@value='view']")
        view_button.click()

        # Wait for the table to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr")))

        # Scrape table data
        table_rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
        data = []
        for row in table_rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            data.append([col.text for col in cols])

        # Convert data to a DataFrame and display
        columns = ["No", "GN", "Household Reference Number", "Applicant's Name", "Address", "Bank Account Status"]
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df)

    except Exception as e:
        st.error(f"Error fetching table data: {e}")

# Close the driver at the end
driver.quit()
