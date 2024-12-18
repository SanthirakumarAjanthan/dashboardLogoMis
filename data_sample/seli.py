from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless Chrome
    # Set the path to your ChromeDriver
    service = Service("C:/webdriver")  # Update path here
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
