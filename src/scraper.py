from typing import Any

import bs4
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


def ensure_bs4_tag(tag: Any) -> bs4.element.Tag:
    """
    Validates that the input is a BeautifulSoup Tag.
    Mainly for type checking and ensuring the input is a valid BeautifulSoup Tag.
    ### Args:
        tag (Any): The input to validate.
    ### Returns:
        bs4.element.Tag: The input if it is a BeautifulSoup Tag.
    ### Raises:
        TypeError: If the input is not a BeautifulSoup Tag.
    """
    if isinstance(tag, bs4.element.Tag):
        return tag
    else:
        raise TypeError(f"Expected a BeautifulSoup Tag, got {type(tag)} instead.")

class Scraper:
    def __init__(self, url, receiving_instution_name, sending_institution_name): # TODO: could remove this url varible
        self.url = url
        self.receiving_instution_name = receiving_instution_name
        self.sending_institution_name = sending_institution_name
    
    def get_major_from_aggreement(self, soup: bs4.BeautifulSoup) -> str:
        """
        Extract the major name from an agreement page's title.
        
        This method parses the title text of a BeautifulSoup object to extract
        the major name. It expects the title format to be:
        "YYYY-YYYY <major_name>, <additional_info>"
        
        The method finds the major name between the year (first 9 characters)
        and the first comma in the title.
        
        Args:
            soup (bs4.BeautifulSoup): BeautifulSoup object containing the parsed HTML with a title element.
        
        Returns:
            str: The extracted major name, stripped of leading/trailing whitespace.
        
        Raises:
            ValueError: If no comma is found in the title text, if the title is missing, or if any other extraction error occurs.
        
        Example:
            If title text is "2024-2025 Computer Science, B.A. Agreement"
            Returns: "Computer Science"
        """
        try:
            title_text = soup.title.text.strip() # type: ignore : saved by try ignore
            comma_pos = title_text.find(',')
            if comma_pos == -1:
                raise ValueError("No comma found in title text to extract major.")
            year_cutoff = 9 # position where the year ends (first 5 characters ex: 2024-2025)
            major = title_text[year_cutoff:comma_pos:].strip()
            return major
        except Exception as e:
            raise ValueError(f"Failed to extract major from title text: {e}") from e

    def clean_units(self, units: str) -> float:
        """
        ### Description:
            Remove the 'unit' suffix and convert to float.
        ### Args:
            units (str): The units string to clean, e.g., "4.00units" or "3.0 unit".
        ### Returns:
            float: The cleaned units as a float, e.g., 4.0 or 3.0.
        ### Raises:
            ValueError: If the units string is not in a valid format.
        """
        removed_suffix = units.replace('units', '').replace('unit', '').strip()
        try:
            return float(removed_suffix)
        except ValueError as e:
            print(f"Error converting units to float: {e}")
            raise

    def clean_full_course(self, course: str) -> dict[str, str]:
        """
        ### Description:
            Clean the course string to extract the subject and number.
        ### Args:
            course (str): The full course string, e.g., "CS 101".
        ### Returns:
            dict: A dictionary with 'subject' and 'number' keys.
        """
        parts = course.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid course format: {course}")
        return {
            'subject': parts[0],
            'number': ' '.join(parts[1:])
        }
    def process_course_line(self, courseLine: bs4.element.Tag):
        try:
            # can safeley ignore types as its caught by the try except block
            course = courseLine.find('div', class_='prefixCourseNumber').text.strip() # type: ignore
            title = courseLine.find('div', class_='courseTitle').text.strip() # type: ignore
            units = courseLine.find('div', class_='courseUnits').text.strip() # type: ignore
            course_subject = self.clean_full_course(course)["subject"]
            course_number = self.clean_full_course(course)["number"]
            return {
                'type': 'course',
                'subject': course_subject,
                'number': course_number,
                'title': title,
                'units': self.clean_units(units)
            }
        except AttributeError as e:
            print(f"Error processing course line: {e}")
            raise
    
    def handle_bracket(self, bracket: bs4.element.Tag):
        """
        ### Description:
            Handle the bracket element and extract its text.
        ### Args:
            bracket (bs4.element.Tag): The bracket element to process.
        ### Returns:
            str: The cleaned text from the bracket.
        """
        assert isinstance(bracket, bs4.element.Tag), "Expected a BeautifulSoup Tag"
        assert bracket.name == 'div', "Expected a div element"
        assert 'bracketWrapper' in (bracket.get('class') or []), "Expected a bracket class"
        
        bracket_content = ensure_bs4_tag(bracket.find('div', class_='bracketContent'))
        
        # make sure we only have ands
        cojunctions = bracket_content.find_all('awc-view-conjunction')
        if len(cojunctions) == 0:
            raise ValueError("No conjunctions found in bracket content")
        for conjunction in cojunctions:
            if conjunction.text.strip() != 'And':
                raise ValueError(f"Unexpected conjunction: {conjunction.text.strip()} in bracket")
        
        course_lines = bracket_content.find_all('div', class_='courseLine')
        if not course_lines:
            raise ValueError("No course lines found in bracket content")
        courses = []
        for course_line in course_lines:
            course_line = ensure_bs4_tag(course_line)
            course = self.process_course_line(course_line)
            if course:
                courses.append(course)
        
        return {
            "type": "CourseGroup",
            "courseConjunction": "And",
            "items": courses
        }
    
    def count_ands_in_bracket(self, bracket: bs4.element.Tag) -> int:
        """
        ### Description:
            Count the number of 'And' conjunctions in a bracket element.
        ### Args:
            bracket (bs4.element.Tag): The bracket element to process.
        ### Returns:
            int: The count of 'And' conjunctions in the bracket.
        """
        assert isinstance(bracket, bs4.element.Tag), "Expected a BeautifulSoup Tag"
        assert bracket.name == 'div', "Expected a div element"
        assert 'bracketWrapper' in bracket.get('class', []), "Expected a bracket class" #type: ignore : again [] saves us
    
        return len(bracket.find_all(lambda tag: tag.name == 'awc-view-conjunction' and tag.text.strip() == 'And'))

    def handle_main_block(self, mainBlock: bs4.element.Tag) -> dict:
        """
        ### Description:
            Handle the main block element and extract its text.
        ### Args:
            mainBlock (bs4.element.Tag): The main block element to process.
        ### Returns:
            dict: A dictionary with the type and text of the main block.
        """
        assert isinstance(mainBlock, bs4.element.Tag), "Expected a BeautifulSoup Tag"
        assert mainBlock.name == 'div', "Expected a div element"
        assert mainBlock.find(class_="courseLine") is not None, "Expected a courseLine class in mainBlock" 
        
        if (mainBlock.find('div', class_='bracketWrapper') is not None):
            # handle bracket
            brackets = mainBlock.find_all('div', class_='bracketWrapper')
            and_conjuncted_courses = []
            for bracket in brackets:
                bracket = ensure_bs4_tag(bracket)
                courses_in_bracket = self.handle_bracket(bracket)
                and_conjuncted_courses.append(courses_in_bracket)
                
            # now check that and count in brackets is equal to total and count
            total_and_conjunctions = len(mainBlock.find_all(
                lambda tag: tag.name == 'awc-view-conjunction' and tag.text.strip() == 'And'
            ))
            bracket_and_conjunctions = sum(self.count_ands_in_bracket(ensure_bs4_tag(bracket)) for bracket in brackets)
            if total_and_conjunctions != bracket_and_conjunctions: # our assumption that all ands are in a bracket is wrong
                raise ValueError(
                    f"Mismatch in 'And' conjunction counts: {total_and_conjunctions} found, but only {bracket_and_conjunctions} in brackets."
                )
            
            # now check the other `awc-view-conjunction` tags are "Or" otherwise we have an undocumented case and need manual inspection
            non_and_or_conjunctions = mainBlock.find_all(
                lambda tag: tag.name == 'awc-view-conjunction' and (tag.text.strip() != 'And' and tag.text.strip() != 'Or')
            )
            
            if non_and_or_conjunctions:
                raise ValueError(f"Unexpected conjunctions found: {[conj.text.strip() for conj in non_and_or_conjunctions]}")
            
            # lets add one more protective check 
            all_conjunctions = mainBlock.find_all('awc-view-conjunction')
            or_conjunctions = mainBlock.find_all(
                lambda tag: tag.name == 'awc-view-conjunction' and tag.text.strip() == 'Or'
            ) # use text to filer instead of classes since we wont know if classes stay consistent outside our observed data of "and" and "or"
            
            if len(all_conjunctions) != len(or_conjunctions) + total_and_conjunctions:
                print(f"All conjunctions: {len(all_conjunctions)}, Or conjunctions: {len(or_conjunctions)}, Brackets: {len(brackets)}")
                raise ValueError("Mismatch in conjunction counts: some brackets may not be handled correctly.")
            
            if len(or_conjunctions) == 0:
                # if no or conjunctions, we can return and course directly
                assert len(and_conjuncted_courses) == 1, "Expected exactly one course group when no 'Or' conjunctions are present"
                return and_conjuncted_courses[0]
            else:
                # if there are or conjunctions, we need to return a group of courses
                return {
                    "type": "CourseGroup",
                    "courseConjunction": "Or",
                    "items": and_conjuncted_courses
                }
            
        else:
            # for now only support one courseLine
            courseLine = mainBlock.find('div', class_='courseLine')
            if courseLine:
                course_data = self.process_course_line(courseLine) # type: ignore
                return course_data
            else:
                raise ValueError("No courseLine found.")

    # handle a rowReceiving
    def handle_rowReceiving(self, rowReceiving: bs4.element.Tag):
        assert rowReceiving.name == 'div' and 'rowReceiving' in (rowReceiving.get('class') or []), f"Expected a 'div' with class 'rowReceiving', got {rowReceiving.name} with classes {rowReceiving.get('class', [])}" # type: ignore
        try:
            return self.handle_main_block(rowReceiving) 
        except ValueError as e:
            if str(e) == "No courseLine found.":
                raise ValueError("No courseLine found in rowReceiving.") from e
            else:
                raise

    def handle_rowSending(self, rowSending: bs4.element.Tag):
        assert rowSending.name == 'div' and 'rowSending' in (rowSending.get('class') or []), f"Expected a 'div' with class 'rowSending', got {rowSending.name} with classes {rowSending.get('class', [])}" # type: ignore
        # print(f"Row sending content: {rowSending.prettify()}")
        try:
            mainContent = ensure_bs4_tag(rowSending.find('div', class_='view_sending__content'))
        except TypeError:
            if "No Course Articulated" in rowSending.text:
                return {
                    "type": "NotArticulated",
                }
        except Exception as e:
            raise ValueError({"message": "No main content found in rowSending.", "data": rowSending.prettify()}) from e # add some proper data types later for passing errors up # TODO
        try:
            return self.handle_main_block(mainContent)
        except ValueError as e:
            if str(e) == "No courseLine found.":
                raise ValueError("No courseLine found in rowSending.") from e
            else:
                raise
    
    def process_artic_row(self, row: bs4.element.Tag):
        try:
            receiving_html = row.find('div', class_='rowReceiving')  # type: ignore
            receiving_course = self.handle_rowReceiving(receiving_html) # type: ignore
        except Exception as e:
            print(f"Error processing receiving course: {e}")
            raise ValueError("Failed to process receiving classes in articRow") from e
        try:
            sending_html = row.find('div', class_='rowSending')  # type: ignore
            sending_course = self.handle_rowSending(sending_html) # type: ignore
        except Exception as e:
            print(f"Error processing sending course: {e}")
            raise ValueError("Failed to process sending classes in articRow.") from e
        
        return {
            "receiving": receiving_course,
            "sending": sending_course
        }
    
    def process_page(self, soup: bs4.BeautifulSoup):
        """
        # NOT COMPLETED: need to adapt to spec        
        ### Description:
            Process the entire page and extract all receiving and sending courses.
        ### Args:
            soup (BeautifulSoup): The BeautifulSoup object containing the page content.
        ### Returns:
            list: A list of dictionaries containing receiving and sending courses.
        """
        name = self.get_major_from_aggreement(soup)
        articRows = soup.find_all('div', class_='articRow')
        articulations = []
        
        for row in articRows:
            try:
                row = ensure_bs4_tag(row)
                processed_row = self.process_artic_row(row)
                articulations.append(processed_row)
            except ValueError as e:
                print(f"Skipping row due to error: {e}")
                raise
        
        return {
            "type": "Articulation Agreement", # only thing supported for now
            "name": name,
            "receivingInstitution": self.receiving_instution_name,
            "sendingInstitution": self.sending_institution_name,
            "articulations": articulations
        }
        

async def scrape_url(url: str, receiving_institution_name: str, sending_institution_name: str) -> dict:
    """
    ### Description:
        Scrape the given URL and return the processed data.
    ### Args:
        url (str): The URL to scrape.
        receiving_institution_name (str): The name of the receiving institution.
        sending_institution_name (str): The name of the sending institution.
    ### Returns:
        dict: The processed data from the scraped page.
    """
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_selector('.articRow') # wait until at least one articRow is loaded
        
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')
        # print(f"Content: \n {soup.prettify()}")
        scraper = Scraper(url, receiving_institution_name, sending_institution_name)
        try:
            data = scraper.process_page(soup)
            return data
        except ValueError as e:
            print(f"Error processing page: {e}")
            raise
    
if __name__ == "__main__":
    import asyncio
    url = "https://assist.org/transfer/results?year=75&institution=79&agreement=113&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F113%2Fto%2F79%2FMajor%2F607b828c-8ba3-411b-7de1-08dcb87d5deb"
    receiving_institution_name = "Receiving Institution"
    sending_institution_name = "Sending Institution"
    
    try:
        data = asyncio.run(scrape_url(url, receiving_institution_name, sending_institution_name))
        print(data)
    except Exception as e:
        print(f"An error occurred: {e}")