from playwright.async_api import async_playwright
import json
import asyncio

def unwrap_nested_json(data):
    """
    Recursively unwraps nested JSON strings within a Python dictionary or list.
    """
    if isinstance(data, dict):
        return {k: unwrap_nested_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [unwrap_nested_json(elem) for elem in data]
    elif isinstance(data, str):
        try:
            # Attempt to parse the string as JSON
            parsed_data = json.loads(data)
            # If successful, recursively unwrap the newly parsed data
            return unwrap_nested_json(parsed_data)
        except json.JSONDecodeError:
            # If it's not valid JSON, just return the string as is
            return data
    else:
        # For other data types (int, float, bool, None), return as is
        return data

async def intercept(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        json_found = asyncio.Event()

        async def handle_response(response):
            if 'Agreements?Key=' in response.url:
                json_data = await response.json()
                parsed_data = unwrap_nested_json(json_data)
                with open('ivc-berkeley-ds.json', 'w', encoding='utf-8') as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=4)
                json_found.set()

        page.on('response', handle_response)
        await page.goto(url, wait_until='networkidle')

        await asyncio.wait_for(json_found.wait(), timeout=10)
        await browser.close()

if __name__ == '__main__':
    url: str = 'https://assist.org/transfer/results?year=75&institution=124&agreement=79&agreementType=to&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FMajor%2F648bdbf3-f87d-4a4e-7e0b-08dcb87d5deb'
    asyncio.run(intercept(url))