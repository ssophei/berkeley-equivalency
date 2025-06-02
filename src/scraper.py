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

    courses = soup.find_all('div', class_='rowReceiving')
    for receiving_course in courses:
        receiving_course_number = receiving_course.find_next(class_='prefixCourseNumber')
        receiving_course_title = receiving_course.find_next(class_='courseTitle')
        sending = receiving_course.find_next_sibling(class_='rowSending') # gets the corresponding sending agreement
        try:
            articulation = sending.find('awc-articulation-sending').find('div', class_='view_sending__content')
        except: # if there is no course articulated, then this div will not exist 
            return None
        else:
            conjunction = articulation.find('awc-view-conjunction')

            if conjunction:
                conjunction_text = conjunction.find_next('div').text.strip()
                if conjunction_text == 'Or':
                    first_sending_course_number = sending.find_next(class_='prefixCourseNumber')
                    first_sending_course_title = sending.find_next(class_='courseTitle')
                    second_sending_course_number = conjunction.find_next(class_='prefixCourseNumber')
                    second_sending_course_title = conjunction.find_next(class_='courseTitle')
                    print(f'{receiving_course_number.text.strip()} {receiving_course_title.text.strip()}: ' 
                    f'{first_sending_course_number.text.strip()} {first_sending_course_title.text.strip()}, '
                    f'{second_sending_course_number.text.strip()} {second_sending_course_title.text.strip()}')
            else: 
                # agreement_content = articulation.find_all('div', recursive=False) # recursive=False checks for only immediate children in sending content
                sending_course_number = sending.find_next(class_='prefixCourseNumber')
                sending_course_title = sending.find_next(class_='courseTitle')
                print(f'{receiving_course_number.text.strip()} {receiving_course_title.text.strip()}: ' 
                f'{sending_course_number.text.strip()} {sending_course_title.text.strip()}')
                

if __name__ == '__main__':
    scrape()
