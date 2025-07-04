from scraper import scrape_url
import pytest
import json


@pytest.fixture
def return_json_for_de_anze_to_berk_aero():
    with open("tests/data/expected_data.json", "r") as file:
        data = json.load(file)
    return data["de_anze_to_berk_aero"]

@pytest.mark.asyncio
async def test_full_scraper_on_de_anze_to_berk_aero(
    return_json_for_de_anze_to_berk_aero
):
    url = "https://assist.org/transfer/results?year=75&institution=79&agreement=113&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F113%2Fto%2F79%2FMajor%2F607b828c-8ba3-411b-7de1-08dcb87d5deb"
    receiving_institution = "University of California, Berkeley"
    sending_institution = "De Anza College"

        
    
    expected = return_json_for_de_anze_to_berk_aero
    actual = await scrape_url(url, receiving_institution, sending_institution) 
    
    assert actual == expected, f"Expected: {json.dumps(expected, indent=2)}, \n \n but got: {json.dumps(actual, indent=2)}"