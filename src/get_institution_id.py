from typing import List
import httpx
import os
import json

# This script fetches institution IDs from the Assist.org API and saves them to a JSON file.

def get_ids() -> List[dict]:
    url = "https://assist.org/api/institutions"
    response = httpx.get(url)
    if response.status_code == 200:
        # write the data to a file in data/institutions.json, this file will be created if it does not exist
        filename = 'data/institutions.json'
        # ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open('data/institutions.json', 'w') as file:
            file.write(response.text)
        print("Institution IDs saved to data/institutions.json")
        return response.json()
    else:
        print(f"Failed to retrieve institution IDs. Status code: {response.status_code}")
        raise Exception(f"Failed to retrieve institution IDs. Status code: {response.status_code}")

def get_institutions_with_agreements(school_id: int) -> List[dict]:
    """
    Function taken and modified from Jacob T Binghams pdfgrabber.py `get_agreements` function.
    
    Args:
        school_id (int): The ID of the institution to fetch agreements for.
    Returns:
        List[dict]: A list of dictionaries containing institution IDs and their corresponding years.
        
        Example:
            [{'id': 123, 'year': 2023}, {'id': 456, 'year': 2024}]
    Raises:
        Exception: If the API request fails or returns an unexpected status code.
    
    """
    response = httpx.get(f'https://assist.org/api/institutions/{school_id}/agreements')
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve agreements. Status code: {response.status_code}")
    
    data = response.json()
    agreement_list = []
    for agreement in list(data):
        if agreement['isCommunityCollege']:
            school_id = agreement['institutionParentId']
            year = agreement['sendingYearIds'][-1]
            curr = {'id': school_id, 'year': year}
            agreement_list.append(curr)
    print('list of agreements found!')
    return agreement_list

if __name__ == '__main__':
    get_ids()
