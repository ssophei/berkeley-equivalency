from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import time

def scrape():
    url: str = 'https://assist.org/transfer/results?year=75&institution=79&agreement=58&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F58%2Fto%2F79%2FMajor%2Ffc50cced-05c2-43c7-7dd5-08dcb87d5deb'
    
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    courses = soup.find_all('div', class_='courseLine')
    for course in courses:
        course_number = course.find_next(class_='prefixCourseNumber')
        course_title = course.find_next(class_='courseTitle')
        if course.find_parent(class_='rowReceiving'):
            print(f'Receiving - {course_number.text.strip()}: {course_title.text.strip()}')
        else: 
            print(f'Sending - {course_number.text.strip()}: {course_title.text.strip()}')

if __name__ == '__main__':
    scrape()
