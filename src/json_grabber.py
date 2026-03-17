import os
from playwright.async_api import async_playwright
import json
import asyncio
from typing import Any

SEM = asyncio.Semaphore(3)

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
        async with page.expect_response(lambda r: match_substring in r.url, timeout=20000) as response_info:
            await page.goto(url, wait_until='domcontentloaded')

        response = await response_info.value
        json_data = await response.json()

        parsed_data = unwrap_nested_json(json_data)
        assert isinstance(parsed_data, dict)  # type: ignore

        await browser.close()
        print(json.dumps(parsed_data, indent=4))
        
        return parsed_data

async def main():
    with open("data/urls.json") as f:
        urls = json.load(f)

    i = 1
    start = 0
    urls = urls[start:]
    for url in urls:
        data = await intercept(url)
        filename = f"data/articulations/assist_data_{i}"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Agreement saved to {filename}")
        i += 1

if __name__ == "__main__":
    asyncio.run(main())