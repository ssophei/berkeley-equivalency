import bs4
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio


from typing import Any

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
    def __init__(self, url, receiving_instution_name, sending_instution_name):
        self.url = url
        self.receiving_instution_name = receiving_instution_name
        self.sending_instution_name = sending_instution_name

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
            raise ValueError(f"Invalid units format: {units}")

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
    def process_courseLine(self, courseLine: bs4.element.Tag):
        try:
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
            return None
    
    # handle a rowReceiving
    def handle_rowReceiving(self, rowReceiving: bs4.element.Tag):
        assert rowReceiving.name == 'div' and 'rowReceiving' in rowReceiving.get('class', []), f"Expected a 'div' with class 'rowReceiving', got {rowReceiving.name} with classes {rowReceiving.get('class', [])}" # type: ignore [] in .get protects us
        
        # for now only support one courseLine
        courseLine = ensure_bs4_tag(rowReceiving.find('div', class_='courseLine'))
        if courseLine:
            course_data = self.process_courseLine(courseLine)
            return course_data
        else:
            print("No courseLine found in rowReceiving.")
            raise ValueError("No courseLine found in rowReceiving.")
    
    def handle_rowSending(self, rowSending: bs4.element.Tag):
        assert rowSending.name == 'div' and 'rowSending' in rowSending.get('class', []), f"Expected a 'div' with class 'rowSending', got {rowSending.name} with classes {rowSending.get('class', [])}" # type: ignore [] in .get protects us
        
        mainContent = ensure_bs4_tag(rowSending.find('div', class_='view_sending__content'))
        
        # for now only support one courseLine
        courseLine = ensure_bs4_tag(mainContent.find('div', class_='courseLine'))
        if courseLine:
            course_data = self.process_courseLine(courseLine)
            return course_data
        else:
            print("No courseLine found in rowSending.")
            raise ValueError("No courseLine found in rowSending.")
    
    def process_artic_row(self, row: bs4.element.Tag):
        try:
            receiving_html = row.find('div', class_='rowReceiving')  # type: ignore
            receiving_course = self.handle_rowReceiving(receiving_html) # type: ignore
            sending_html = row.find('div', class_='rowSending')  # type: ignore
            sending_course = self.handle_rowSending(sending_html) # type: ignore
        except Exception as e:
            print(f"Error processing receiving course: {e}")
            raise ValueError("Failed to process articRow.")
        
        return {
            "receiving": receiving_course,
            "sending": sending_course
        }