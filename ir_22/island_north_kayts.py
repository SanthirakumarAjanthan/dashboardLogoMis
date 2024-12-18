import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Dictionary of URLs with descriptive location names (fixed "Naranthanai North" name)
urls = {
    "Analaitivu North": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7037&lang=en&action=view",
    "Analaitivu South": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7030&lang=en&action=view",
    "Eluvaitivu": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7036&lang=en&action=view",
    "Karampon": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7040&lang=en&action=view",
    "Karampon East": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7041&lang=en&action=view",
    "Karampon South East": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7042&lang=en&action=view",
    "Karampon West": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7043&lang=en&action=view",
    "Kayts": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7038&lang=en&action=view",
    "Naranthanai": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7032&lang=en&action=view",
    "Naranthanai North": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7044&lang=en&action=view",
    "Naranthanai North West": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7031&lang=en&action=view",
    "Naranthanai South": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7033&lang=en&action=view",
    "Paruthiyadappu": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7039&lang=en&action=view",
    "Puliyankoodal": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7035&lang=en&action=view",
    "Suruvil": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=132&gnd_id=7034&lang=en&action=view"
}

# Function to scrape data from a single URL
def scrape_data(url):
    # Send a request to the page
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        st.error(f"Failed to retrieve data from {url}.")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract data from the table
    data = []
    table = soup.find('table')  # Locate the data table

    if table:
        headers = [header.text.strip() for header in table.find_all('th')]
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cols = row.find_all('td')
            data.append([col.text.strip() for col in cols])
        return pd.DataFrame(data, columns=headers)
    else:
        st.warning(f"No data table found on the page for URL: {url}")
        return None

# Streamlit UI
st.title("Household Data Scraper")
st.write("Scraping data from each URL and saving each table as a CSV file.")

# Folder to save CSV files
save_folder = "Island_north_kayts"
os.makedirs(save_folder, exist_ok=True)

# Loop through each URL, scrape data, and save each DataFrame as a CSV file
for location_name, url in urls.items():
    st.write(f"### Data from {location_name}")
    data = scrape_data(url)
    if data is not None:
        st.dataframe(data)  # Display the DataFrame in Streamlit as a table

        # Clean up location name and save DataFrame as a CSV file
        safe_location_name = location_name.strip().replace(" ", "_").replace("\t", "").lower()
        csv_file_path = os.path.join(save_folder, f"{safe_location_name}_data.csv")
        data.to_csv(csv_file_path, index=False, encoding="utf-8")
        st.success(f"Data from {location_name} saved to {csv_file_path}")
    else:
        st.warning(f"No data available for {location_name}.")
