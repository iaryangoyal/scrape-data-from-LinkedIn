import pandas as pd
# df = pd.read_csv('company.csv')
# print(df.head(5))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import numpy as np
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


#login in linkedin
driver=webdriver.Chrome()
wait = WebDriverWait(driver, 30)
driver.get("https://linkedin.com/")
wait.until(EC.presence_of_element_located((By.ID, "session_key"))).send_keys('attendanceantino@gmail.com')
driver.find_element(By.ID, "session_password").send_keys('Antinoattendance@123')
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
print("Login Successfully")
# time.sleep(8) #give some
list_jobs = {}
job_opening = []
company_name = []
location_of_company = []
date_of_post = []

def find_jobs (soup):   
        jobs = soup.find_all('div',{'class':'job-card-container'})
        job_role = []
        company = []
        location = []
        date = []
        for i in jobs:
            try:
                job_role.append(i.find('a',{'class': 'disabled ember-view job-card-container__link job-card-list__title job-card-list__title--link'}).text.strip())
            except:
                job_role.append(np.nan)
            try:
                company.append(i.find('span',{'class':'job-card-container__primary-description'}).text.strip())
            except:
                company.append(np.nan)
            try:
                location.append(i.find('li',{'class':'job-card-container__metadata-item'}).text.strip())
            except:
                location.append(np.nan)
            try:
                date.append(i.find('time')['datetime'])
            except:
                date.append(np.nan)       
        d = {'job_role':job_role, 'company':company, 'location':location, 'date':date}
        df = pd.DataFrame(d)
        return df

def slow_scroll():
    scroll_iterations = 10  # Adjust the number of scroll iterations as needed
    scroll_increment = 500  # Adjust the scroll height increment as needed
    for _ in range(scroll_iterations):
        driver.execute_script(f"window.document.getElementsByClassName('jobs-search-results-list')[0].scrollBy(0, {scroll_increment});")
        time.sleep(.5) 

def update_data():
    global combined_df
    src = driver.page_source
    soup = BeautifulSoup(src, 'html.parser')
    soup.prettify()

    df = find_jobs(soup)
    dff = df.fillna('N/A')
    data = dff.values.tolist()
    print("Data", data)
    for i in data:
        job_opening.append(i[0])
        company_name.append(i[1])
        location_of_company.append(i[2])
        date_of_post.append(i[3])
def search_and_extract_data(client, combined_df):
    if client == 0: 
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "search-global-typeahead"))).click() # searching
        driver.find_element(By.XPATH, "//input[@placeholder='Search']").send_keys(clients[0],Keys.ENTER) #value type
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-pressed='false'][normalize-space()='Jobs']"))).click() # Filter for job
        wait.until(EC.element_to_be_clickable((By.ID, "searchFilter_timePostedRange"))).click() # Datetime Filter
        wait.until(EC.element_to_be_clickable((By.XPATH, "//section[1]//div[1]//section[1]//div[1]//div[1]//div[1]//ul[1]//li[3]//div[1]//div[1]//div[1]//div[1]//div[1]//form[1]//fieldset[1]//div[1]//ul[1]//li[3]//label[1]//p[1]//span[1]"))).click()  #Week
        wait.until(EC.element_to_be_clickable((By.XPATH, "//section[1]/div[1]/section[1]/div[1]/div[1]/div[1]/ul[1]/li[3]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/fieldset[1]/div[2]/button[2]"))).click() #Submit
        slow_scroll()
        update_data()

        try:
            for i in range(2, 4):
                page_button_xpath = f"//button[@aria-label='Page {i}']"
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, page_button_xpath))).click()
                slow_scroll()
                update_data()

        except Exception as e:
            print("Pagination error:", str(e))

    else:
        driver.find_element(By.CLASS_NAME, "jobs-search-box__keyboard-text-input").send_keys(clients[client],Keys.ENTER)
        slow_scroll()
        update_data()

        try:
            for i in range(2, 4):
                page_button_xpath = f"//button[@aria-label='Page {i}']"
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, page_button_xpath))).click()
                slow_scroll()
                update_data()
                
        except Exception as e:
            print("Pagination error:", str(e))
   
# Extraction of clients' names from sheet 1
# clients = import_data.col_values(1)
clients1 = pd.read_csv('company.csv')
clients = clients1['Company Name'].to_list()
combined_df = pd.DataFrame()
timeout = 1


for client in range(0,len(clients)):
    combined_df = search_and_extract_data(client, combined_df)
    driver.find_element(By.CLASS_NAME, "jobs-search-box__keyboard-text-input").clear() #To clear

print(job_opening)

list_jobs = {"Job Role" : job_opening, "company Name" : company_name, "location" : location_of_company, "date" : date_of_post}


df = pd.DataFrame(list_jobs)


df.to_csv('file1.csv')