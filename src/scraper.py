from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def scrape():
    url: str = 'https://assist.org/transfer/results?year=75&institution=79&agreement=124&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FMajor%2F23d79a84-d16c-4b58-7dee-08dcb87d5deb'
    
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # courses = soup.find_all('div', class_='courseLine')
    # for course in courses:
    #     course_number = course.find_next(class_='prefixCourseNumber')
    #     course_title = course.find_next(class_='courseTitle')
    #     if course.find_parent(class_='rowReceiving'):
    #         print(f'Receiving - {course_number.text.strip()}: {course_title.text.strip()}')
    #     else: 
    #         print(f'Sending - {course_number.text.strip()}: {course_title.text.strip()}')


    courses = soup.find_all('div', class_='rowReceiving')
    for receiving_course in courses:
        receiving_course_number = receiving_course.find_next(class_='prefixCourseNumber')
        receiving_course_title = receiving_course.find_next(class_='courseTitle')
        sending = receiving_course.find_next_sibling(class_='rowSending') # gets the corresponding sending agreement
        if sending.find('p'): # occurs when no course is articulated
            print(f'{receiving_course_number.text.strip()} {receiving_course_title.text.strip()}: {sending.text.strip()}')
        else: 
            articulation = sending.find('awc-articulation-sending').find('div', class_='view_sending__content')
            agreement_content = articulation.find_all('div', recursive=False)
            # print(agreement_content)
            if len(agreement_content) == 1:
                sending_course_number = sending.find_next(class_='prefixCourseNumber')
                sending_course_title = sending.find_next(class_='courseTitle')
                print(f'{receiving_course_number.text.strip()} {receiving_course_title.text.strip()}: {sending_course_number.text.strip()} {sending_course_title.text.strip()}')
                

if __name__ == '__main__':
    scrape()
