from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import pandas as pd
import openpyxl

driver = webdriver.Chrome()
driver.get("https://pfm.smartcitylk.org/wp-admin/admin.php?page=pfmDashboard")

username_field = driver.find_element(By.NAME, "log")
password_field = driver.find_element(By.NAME, "pwd")

username_field.send_keys("nationaluser1@gmail.com")
password_field.send_keys("nationaluser1@gmail.com")

login_button = driver.find_element(By.ID, "wp-submit")
login_button.click()

wait = WebDriverWait(driver, 10)
#driver = webdriver.Chrome()
driver.get("https://pfm.smartcitylk.org/wp-admin/admin.php?page=pfmDashboard")

local_select_element = wait.until(EC.presence_of_element_located((By.NAME, "accYear")))
la_select = Select(local_select_element)
la_select.select_by_visible_text("2022")

change_button2 = driver.find_element(By.CLASS_NAME, "btn btn-primary")
change_button2.click()
   