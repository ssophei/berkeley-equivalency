from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time

def scrape():
    url = ('https://assist.org/transfer/results?year=75&institution=79&agreement=58&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F58%2Fto%2F79%2FMajor%2Ffc50cced-05c2-43c7-7dd5-08dcb87d5deb')
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    courses = soup.find_all('div', class_='courseTitle')
    titles = [course_div.text.strip() for course_div in courses]
    print(titles)

if __name__ == '__main__':
    scrape()