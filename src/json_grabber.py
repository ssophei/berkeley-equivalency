import os
from playwright.async_api import async_playwright
import json
import asyncio
import json
from typing import Any, Union

def unwrap_nested_json(data: Any) -> dict | list:
    """
    Recursively unwraps nested JSON strings within a Python dictionary or list.
    Only returns a dict or list at the top level.
    """

    def _unwrap(val: Any) -> Any:
        if isinstance(val, dict):
            return {k: _unwrap(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [_unwrap(elem) for elem in val]
        elif isinstance(val, str):
            try:
                parsed = json.loads(val)
                return _unwrap(parsed)
            except json.JSONDecodeError:
                return val
        else:
            return val

    unwrapped = _unwrap(data)

    # Only allow top-level return of dict or list for consistency
    if isinstance(unwrapped, (dict, list)):
        return unwrapped
    else:
        raise TypeError("Top-level data must unwrap to a dict or list")

async def intercept(url) -> dict:
    match_substring = 'Agreements?Key='
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Wait for the specific network response while navigating to the page.
        async with page.expect_response(lambda r: match_substring in r.url, timeout=10000) as response_info:
            await page.goto(url, wait_until='networkidle')

        response = await response_info.value
        json_data = await response.json()

        parsed_data = unwrap_nested_json(json_data)
        assert isinstance(parsed_data, dict)  # type: ignore

        await browser.close()
        print(json.dumps(parsed_data, indent=4))
        
        # print for testing
        # filename = 'data/assist_data.json'
        # os.makedirs(os.path.dirname(filename), exist_ok=True)
        # with open(filename, 'w') as f:
        #     json.dump(parsed_data, f, indent=4)
        # print(f"Data saved to {filename}")

        return parsed_data

if __name__ == '__main__':
    url: str = 'https://assist.org/transfer/results?year=75&institution=124&agreement=79&agreementType=to&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FMajor%2F648bdbf3-f87d-4a4e-7e0b-08dcb87d5deb'
    result = asyncio.run(intercept(url))
    print(result)