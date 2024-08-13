import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

browser_options = Options()
browser_options.add_argument("--headless")  
browser_options.add_argument("--no-sandbox")
browser_options.add_argument("--disable-dev-shm-usage")


driver_path = 'C:/Program Files/chromedriver-win64/chromedriver.exe'
service_instance = Service(driver_path)
browser = webdriver.Chrome(service=service_instance, options=browser_options)


webpages = [
    "https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_TPR=r86400&f_C=1586&position=1&pageNum=0"
]


def parse_date_posted(date_text):

    current_date = datetime.now()
    date_text = date_text.lower()
    if 'today' in date_text:
        return current_date.strftime("%d-%m-%Y")
    elif 'week' in date_text:
        try:
            days_ago = int(date_text.split(' ')[0])
            return (current_date - timedelta(days=days_ago)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    elif 'month' in date_text:
        try:
            months_ago = int(date_text.split(' ')[0])
            return (current_date - timedelta(days=months_ago * 30)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    elif 'day' in date_text:
        try:
            days_ago = int(date_text.split(' ')[0])
            return (current_date - timedelta(days=days_ago)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    return None

def get_job_info(job_item):
    
    job_info = {}

    try:
        company = job_item.find("h4", class_="base-search-card__subtitle").find("a").get_text(strip=True)
    except AttributeError:
        company = None
    job_info["company"] = company

    try:
        title = job_item.find("h3", class_="base-search-card__title").get_text(strip=True)
    except AttributeError:
        title = None
    job_info["job_title"] = title

    try:
        job_id = job_item.find("a", {"data-tracking-control-name": "public_jobs_jserp-result_search-card"})["href"].split("/")[-2]
    except (AttributeError, IndexError):
        job_id = None
    job_info["linkedin_job_id"] = job_id

    try:
        job_location = job_item.find("span", class_="job-search-card__location").get_text(strip=True)
    except AttributeError:
        job_location = None
    job_info["location"] = job_location

    try:
        posted_text = job_item.find("time", class_="job-search-card__listdate--new").get_text(strip=True)
        posted_date = parse_date_posted(posted_text)
    except AttributeError:
        posted_text = None
        posted_date = None
    job_info["posted_on"] = posted_text
    job_info["posted_date"] = posted_date

   
    job_type = None  

    job_info["employment_type"] = job_type

   
    level_of_seniority = None  

    job_info["seniority_level"] = level_of_seniority

    return job_info

def fetch_jobs(website):
   
    browser.get(website)
    time.sleep(5) 
    
    page_soup = BeautifulSoup(browser.page_source, 'html.parser')
    job_items = page_soup.find_all("div", {"class": "job-search-card"})

    job_list = []
    for job_item in job_items:
        job_info = get_job_info(job_item)
        if job_info:
            job_list.append(job_info)

    return job_list


collected_jobs = []
for website in webpages:
    jobs = fetch_jobs(website)
    collected_jobs.extend(jobs)


with open('jobs_data.json', 'w') as file_json:
    json.dump(collected_jobs, file_json, indent=4)


dataframe = pd.DataFrame(collected_jobs)
dataframe.to_csv('jobs_data.csv', index=False)


browser.quit()

print("Scraping completed. Data saved to jobs_data.json and jobs_data.csv.")
