from typing import Any

import bs4


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
    def __init__(self, url, receiving_instution_name, sending_institution_name):
        self.url = url
        self.receiving_instution_name = receiving_instution_name
        self.sending_institution_name = sending_institution_name

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
            "courses": courses
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
                    "courses": and_conjuncted_courses
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
        
        mainContent = ensure_bs4_tag(rowSending.find('div', class_='view_sending__content'))
        if not mainContent:
            raise ValueError("No main content found in rowSending.")
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
            raise ValueError("Failed to process articRow.") from e
        try:
            sending_html = row.find('div', class_='rowSending')  # type: ignore
            sending_course = self.handle_rowSending(sending_html) # type: ignore
        except Exception as e:
            print(f"Error processing sending course: {e}")
            raise ValueError("Failed to process articRow.") from e
        
        return {
            "receiving": receiving_course,
            "sending": sending_course
        }
    
    def process_page(self, soup: bs4.BeautifulSoup): # THIS FUNCTION PROABLY CONTAINS ERRORS DO NOT USE
        """
        # NOT COMPLETED: need to adaprt to spec
        ### Description:
            Process the entire page and extract all receiving and sending courses.
        ### Args:
            soup (BeautifulSoup): The BeautifulSoup object containing the page content.
        ### Returns:
            list: A list of dictionaries containing receiving and sending courses.
        """
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
            # TODO: Missing major
            "type": "Articulation Agreement", # only thing supported for now
            "receivingInstitution": self.receiving_instution_name,
            "sendingInstitution": self.sending_institution_name,
            "articulations": articulations
        }