from playwright.async_api import async_playwright
import json
import asyncio

async def intercept(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        json_found = asyncio.Event()

        async def handle_response(response):
            if 'Agreements?Key=' in response.url:
                json_data = await response.json()
                for key in ['templateAssets', 'articulations']:
                    json_data['result'][key] = json.loads(json_data['result'][key])
                print(json.dumps(json_data, indent=2))
                with open('ivc-berkeley-ds.json', 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)
                json_found.set()

        page.on('response', handle_response)
        await page.goto(url, wait_until='networkidle')

        await asyncio.wait_for(json_found.wait(), timeout=10)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(intercept('https://assist.org/transfer/results?year=75&institution=124&agreement=79&agreementType=to&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FMajor%2F648bdbf3-f87d-4a4e-7e0b-08dcb87d5deb'))