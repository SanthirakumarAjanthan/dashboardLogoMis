import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Function to initialize the Selenium WebDriver
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless Chrome
    service = Service("C:/webdriver/chromedriver.exe")  # Update path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to scrape data from the website
def scrape_data(zone, category, funcid, typeid):
    driver = get_driver()
    driver.get("https://www.edudept.np.gov.lk/reports/selectschooldetail.php")
    
    # Fill out the form
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.NAME, 'id')))
    driver.find_element(By.NAME, 'id').send_keys(zone)
    driver.find_element(By.NAME, 'categoryid').send_keys(category)
    driver.find_element(By.NAME, 'funcid').send_keys(funcid)
    driver.find_element(By.NAME, 'typeid').send_keys(typeid)
    
    # Click the submit button
    driver.find_element(By.XPATH, "//input[@type='button' and @value='View']").click()
    
    # Wait for the results to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
    
    # Parse the results
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table')
    if table:
        df = pd.read_html(str(table))[0]  # Convert HTML table to DataFrame
    else:
        df = pd.DataFrame()  # Empty DataFrame if no table is found
    
    driver.quit()
    return df

# Streamlit app
def main():
    st.title("School Details Scraper")
    
    # User inputs
    zone = st.selectbox("Select Zone", ["Province", "Jaffna", "Valikamam", "Vadamarachchi", "Thenmarachchi", "Islands", "Kilinochchi", "Mannar", "Madhu", "Vavuniya North", "Vavuniya South", "Mullativu", "Thunukkai"])
    category = st.selectbox("Select Category", ["", "Provincial", "National", "Private"])
    funcid = st.selectbox("Select Function", ["", "F", "TC"])
    typeid = st.selectbox("Select Type", ["", "1AB", "1C", "II", "III"])
    
    if st.button("Scrape Data"):
        with st.spinner("Scraping data..."):
            df = scrape_data(zone, category, funcid, typeid)
            if not df.empty:
                st.write(df)
                st.download_button(
                    label="Download Data",
                    data=df.to_csv(index=False),
                    file_name='school_details.csv',
                    mime='text/csv'
                )
            else:
                st.error("No data found.")

if __name__ == "__main__":
    main()
