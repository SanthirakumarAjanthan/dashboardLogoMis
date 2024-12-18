from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up WebDriver
driver = webdriver.Chrome()  # Or use `webdriver.Firefox()` if you prefer Firefox
url = "https://iwms.wbb.gov.lk/household/list"
driver.get(url)

# Apply Province Filter (Northern Province)
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "provinceID")))
province_select = Select(driver.find_element(By.ID, "provinceID"))
province_select.select_by_visible_text("Northern")

# Apply District Filter (Jaffna District)
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "districtID")))
district_select = Select(driver.find_element(By.ID, "districtID"))
district_select.select_by_visible_text("Jaffna")

# Apply Divisional Secretariat Filter (Jaffna Division)
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "divisionID")))
division_select = Select(driver.find_element(By.ID, "divisionID"))
division_select.select_by_visible_text("Jaffna")

# Click "View Registry" button to filter results
view_button = driver.find_element(By.XPATH, "//button[@name='action' and @value='view']")
view_button.click()

# Wait for results to load
time.sleep(5)  # Adjust this based on your internet speed or use WebDriverWait for dynamic loading

# Parse the results with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.find("table")  # Adjust according to the actual table element
rows = table.find_all("tr")

# Extract headers
headers = [header.text.strip() for header in rows[0].find_all("th")]
print(headers)

# Extract row data
for row in rows[1:]:  # Skipping the header row
    data = [td.text.strip() for td in row.find_all("td")]
    print(data)

# Close WebDriver
driver.quit()
