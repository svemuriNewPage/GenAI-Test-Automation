import asyncio
from playwright.async_api import async_playwright

LOG_FILE = "/Users/saisiddharthvemuri/Desktop/selenium_Test/test_log.txt"
URL = "http://127.0.0.1:5500/pfizerForAll.html"

test_cases = {
    "search_box": {"locator_type": "css", "value": ".header__search"},
    "menu_links": {"locator_type": "css", "value": ".nav-link"},
    "contact_us": {"locator_type": "text", "value": "Contact Us"}
}

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL)
        await page.wait_for_timeout(2000)

        with open(LOG_FILE, "w") as log_file:
            for element_name, locator in test_cases.items():
                try:
                    if locator["locator_type"] == "css":
                        element = await page.wait_for_selector(locator["value"], timeout=3000)
                    elif locator["locator_type"] == "text":
                        element = await page.get_by_text(locator["value"])

                    log_file.write(f"Found {element_name}: {locator}\n")
                    print(f"Found {element_name}: {locator}\n")

                    if element_name in ["username_field", "search_box"]:
                        await element.fill("testuser")
                    elif element_name == "password_field":
                        await element.fill("testpassword")
                    elif element_name in ["login_button", "submit_button", "contact_us"]:
                        await element.click()
                    elif element_name == "menu_links":
                        links = await page.query_selector_all(locator["value"])
                        for link in links[:3]:
                            await link.click()
                            await page.wait_for_timeout(1000)

                except Exception as e:
                    log_file.write(f"Error: Element {element_name} not found - {locator}\nException: {e}\n")
                    print(f"Error: Element {element_name} not found - {locator}\nException: {e}\n")

        await browser.close()

asyncio.run(run_test())
