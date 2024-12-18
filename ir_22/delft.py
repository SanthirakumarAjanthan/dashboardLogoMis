import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Dictionary of URLs with descriptive location names
urls = {
    "Delft Centre": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=145&gnd_id=7205&lang=en&action=view",
    "Delft Centre East": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=145&gnd_id=7206&lang=en&action=view",
    "Delft Centre West": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=145&gnd_id=7204&lang=en&action=view",
    "Delft East": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=145&gnd_id=7207&lang=en&action=view",
    "Delft West": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=145&gnd_id=7203&lang=en&action=view",
    "Delft South": "https://iwms.wbb.gov.lk/household/list?province_id=4&district_id=10&division_id=145&gnd_id=7208&lang=en&action=view"
}

def scrape_data(url):
    
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to retrieve data from {url}.")
        return None

    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    
    data = []
    table = soup.find('table')  

    if table:
        headers = [header.text.strip() for header in table.find_all('th')]
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cols = row.find_all('td')
            data.append([col.text.strip() for col in cols])
        return pd.DataFrame(data, columns=headers)
    else:
        st.warning(f"No data table found on the page for URL: {url}")
        return None


st.title("Household Data Scraper")
st.write("Scraping data from each URL and saving each table as a CSV file.")


save_folder = "Delft"
os.makedirs(save_folder, exist_ok=True)

for location_name, url in urls.items():
    st.write(f"### Data from {location_name}")
    data = scrape_data(url)
    if data is not None:
        st.dataframe(data)  # Display the DataFrame in Streamlit as a table

        # Save DataFrame as a CSV file with location name in the file name
        csv_file_path = os.path.join(save_folder, f"{location_name.replace(' ', '_').lower()}_data.csv")
        data.to_csv(csv_file_path, index=False, encoding="utf-8")
        st.success(f"Data from {location_name} saved to {csv_file_path}")
    else:
        st.warning(f"No data available for {location_name}.")
