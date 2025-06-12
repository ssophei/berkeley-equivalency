from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio
import re


async def scrape():
    url = 'https://assist.org/transfer/results?year=75&institution=79&agreement=124&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FMajor%2F23d79a84-d16c-4b58-7dee-08dcb87d5deb'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_selector('.rowReceiving')

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        courses = soup.find_all('div', class_='rowReceiving')
        for receiving_course in courses:
            receiving_course_num = receiving_course.find_next(class_='prefixCourseNumber')
            receiving_course_title = receiving_course.find_next(class_='courseTitle')
            sending = receiving_course.find_next_sibling(class_='rowSending')
            try:
                articulation = sending.find('awc-articulation-sending').find('div', class_='view_sending__content')
            except:
                return None
            else:
                conjunction = articulation.find('awc-view-conjunction')
                first_sending_num = sending.find_next(class_='prefixCourseNumber')
                first_sending_title = sending.find_next(class_='courseTitle')

                if conjunction:
                    if len(articulation.find_all('awc-view-conjunction')) > 1:
                        print('complex conjunction detected')
                    conjunction_text = conjunction.find_next('div').text.strip()
                    second_sending_num = conjunction.find_next(class_='prefixCourseNumber')
                    second_sending_title = conjunction.find_next(class_='courseTitle')
                    if conjunction_text == 'Or':
                        print(f'{receiving_course_num.text.strip()} {receiving_course_title.text.strip()}: '
                              f'{first_sending_num.text.strip()} {first_sending_title.text.strip()}, '
                              f'{second_sending_num.text.strip()} {second_sending_title.text.strip()}')
                    else:
                        print(f'{receiving_course_num.text.strip()} {receiving_course_title.text.strip()}: '
                              f'{first_sending_num.text.strip()} {first_sending_title.text.strip()}/'
                              f'{second_sending_num.text.strip()} {second_sending_title.text.strip()}')
                else:
                    print(f'{receiving_course_num.text.strip()} {receiving_course_title.text.strip()}: '
                          f'{first_sending_num.text.strip()} {first_sending_title.text.strip()}')

        await browser.close()

async def scrape_breadth():
    url = 'https://assist.org/transfer/results?year=75&institution=27&agreement=79&agreementType=to&viewAgreementsOptions=true&view=agreement&viewBy=breadth&viewSendingAgreements=false&viewByKey=75%2F27%2Fto%2F79%2FGeneralEducation%2F915fecb2-816c-4291-7e0f-08dcb87d5deb'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_selector('.rowReceiving')

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        breadths = soup.find_all('div', class_='rowReceiving')
        for breadth in breadths:
            # content = breadth.select_one('div.requirementOrGEArea > div.content').find('div', class_='content')
            if breadth.find('div', class_='requirementOrGEArea') is None:
                receiving_breadth__course_num = breadth.find_next(class_='prefixCourseNumber').text.strip()
                receiving_breadth__course_title = breadth.find_next(class_='courseTitle').text.strip()
                print(f'{receiving_breadth__course_num}: {receiving_breadth__course_title}')
            else:
                content = breadth.find('div', class_='content')                
                breadth_code = content.find('div', class_='geAreaCode').text.strip()
                breadth_name = content.find('div', class_='courseTitle').text.strip()
                breadth_name = re.split('-', breadth_name)[-1]
                print(f'{breadth_code}: {breadth_name}')

            # sending = receiving_course.find_next_sibling(class_='rowSending')
            # try:
            #     articulation = sending.find('awc-articulation-sending').find('div', class_='view_sending__content')
            # except:
            #     return None
            # else:
            #     conjunction = articulation.find('awc-view-conjunction')
            #     first_sending_num = sending.find_next(class_='prefixCourseNumber')
            #     first_sending_title = sending.find_next(class_='courseTitle')

            #     if conjunction:
            #         if len(articulation.find_all('awc-view-conjunction')) > 1:
            #             print('complex conjunction detected')
            #         conjunction_text = conjunction.find_next('div').text.strip()
            #         second_sending_num = conjunction.find_next(class_='prefixCourseNumber')
            #         second_sending_title = conjunction.find_next(class_='courseTitle')
            #         if conjunction_text == 'Or':
            #             print(f'{receiving_course_num.text.strip()} {receiving_course_title.text.strip()}: '
            #                   f'{first_sending_num.text.strip()} {first_sending_title.text.strip()}, '
            #                   f'{second_sending_num.text.strip()} {second_sending_title.text.strip()}')
            #         else:
            #             print(f'{receiving_course_num.text.strip()} {receiving_course_title.text.strip()}: '
            #                   f'{first_sending_num.text.strip()} {first_sending_title.text.strip()}/'
            #                   f'{second_sending_num.text.strip()} {second_sending_title.text.strip()}')
            #     else:
            #         print(f'{receiving_course_num.text.strip()} {receiving_course_title.text.strip()}: '
            #               f'{first_sending_num.text.strip()} {first_sending_title.text.strip()}')

        await browser.close()

if __name__ == '__main__':
    asyncio.run(scrape_breadth())