import json
from urllib.parse import quote
from typing import List, Dict, Any


def load_institutions(json_data: str) -> List[Dict[str, Any]]:
    """
    Load and parse the institutions JSON data.
    
    Args:
        json_data: JSON string containing institution data
        
    Returns:
        List of institution dictionaries
    """
    return json.loads(json_data)


def filter_community_colleges(institutions: List[Dict[str, Any]]) -> List[int]:
    """
    Extract IDs of all community colleges from the institutions list.
    
    Args:
        institutions: List of institution dictionaries
        
    Returns:
        List of community college IDs
    """
    return [inst['id'] for inst in institutions if inst.get('isCommunityCollege', False)]


def filter_universities(institutions: List[Dict[str, Any]]) -> List[int]:
    """
    Extract IDs of all universities (CSU and UC) from the institutions list.
    
    Args:
        institutions: List of institution dictionaries
        
    Returns:
        List of university IDs (non-community colleges)
    """
    return [inst['id'] for inst in institutions if not inst.get('isCommunityCollege', False)]


def generate_assist_url(year: int, ccc_id: int, dest_id: int) -> str:
    """
    Generate a single ASSIST.org articulation agreement URL.
    
    Args:
        year: Academic year identifier
        ccc_id: Community college ID (sending institution)
        dest_id: Destination university ID (CSU or UC)
        
    Returns:
        Complete ASSIST.org URL
    """
    view_by_key = f"{year}/{ccc_id}/to/{dest_id}/AllMajors"
    encoded_view_by_key = quote(view_by_key, safe='')
    
    url = (
        f"https://assist.org/transfer/results?"
        f"year={year}&"
        f"institution={ccc_id}&"
        f"agreement={dest_id}&"
        f"agreementType=to&"
        f"viewAgreementsOptions=true&"
        f"view=agreement&"
        f"viewBy=major&"
        f"viewSendingAgreements=false&"
        f"viewByKey={encoded_view_by_key}"
    )
    
    return url


def generate_all_assist_urls(institutions_json: str, year: int = 75) -> List[str]:
    """
    Generate all possible ASSIST.org URLs from CCCs to CSU/UC institutions.
    
    Args:
        institutions_json: JSON string containing institution data
        year: Academic year identifier (default: 75)
        
    Returns:
        List of all possible ASSIST.org URLs
    """
    institutions = load_institutions(institutions_json)
    ccc_ids = filter_community_colleges(institutions)
    university_ids = filter_universities(institutions)
    
    urls = []
    for ccc_id in ccc_ids:
        for dest_id in university_ids:
            url = generate_assist_url(year, ccc_id, dest_id)
            urls.append(url)
    
    return urls


def main():
    """Main function to demonstrate the URL generation."""
    # Read the JSON data from the provided document
    with open('data/institutions.json', 'r') as f:
        institutions_json = f.read()
    
    # Generate all URLs
    urls = generate_all_assist_urls(institutions_json)
    
    # Print statistics
    institutions = load_institutions(institutions_json)
    ccc_count = len(filter_community_colleges(institutions))
    university_count = len(filter_universities(institutions))
    
    print(f"Generated {len(urls)} ASSIST.org URLs")
    print(f"From {ccc_count} Community Colleges to {university_count} Universities")
    print(f"Expected total: {ccc_count * university_count}")
    
    # Print first few URLs as examples
    print("\nFirst 5 URLs:")
    for i, url in enumerate(urls[:5]):
        print(f"{i+1}. {url}")
    
    return urls


if __name__ == "__main__":
    main()