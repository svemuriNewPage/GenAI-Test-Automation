import openai
import re
import subprocess
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SELENIUM_TEST_SCRIPT = "/Users/saisiddharthvemuri/Desktop/selenium_Test/Selenium_Test.py"
LOG_FILE = "/Users/saisiddharthvemuri/Desktop/selenium_Test/test_log.txt"

def run_selenium_test():
    result = subprocess.run(["python", SELENIUM_TEST_SCRIPT], capture_output=True, text=True)
    output = result.stdout + result.stderr
    # with open(LOG_FILE, "w") as log_file:
    #     log_file.write(output)
    return output

def extract_failed_locator():
    with open(LOG_FILE, "r") as file:
        log_output = file.read()
    match = re.search(r"Element (\w+) not found - \(('.*?'), ('.*?')\)", log_output)
    if match:
        print(f'Matched: {match.groups()}')
        element_name, locator_type, locator_value = match.groups()
        return element_name, locator_type, locator_value
    return None, None, None

def get_ai_suggested_locator(element_name, page_source):
    prompt = f"""
    You are a helpful agent. You are supposed to assist with the errors in selenium testing performed.
    The following is the HTML of a webpage where the Selenium locator '{element_name}' failed.
    Rewrite the selenium script given below with the proper locator. if the selenium script is wrong with no locator found after trying,
    let the user know that there is no locator and update the selenium script accordingly by removing that specific test case.
    Also, use 'By' locator strategies in your selenium script when choosing locator.

    {page_source}

    Selenium Script used: {SELENIUM_TEST_SCRIPT}

    Give me just the selenium script as output.
    """

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=500
    )

    with open('AI-response.txt', 'w') as f:
        f.write(response.choices[0].message.content)

    ai_suggested_locator = response.choices[0].message.content.strip()
    match = re.search(r"(By\.\w+),\s*\"([^\"]+)\"",  ai_suggested_locator)
    if match:
        print(f'Found fixes: {match.groups()}')
        strategy, value = match.groups()
        return strategy, value
    return None, None

def update_selenium_test_script(old_locator, new_locator):
    try:
        with open(SELENIUM_TEST_SCRIPT, "r") as file:
            script_content = file.read()
        print(old_locator, new_locator)
        updated_script = script_content.replace(str(old_locator), str(new_locator))
        # with open(SELENIUM_TEST_SCRIPT, "w") as file:
        #     file.write(updated_script)
        with open("/Users/saisiddharthvemuri/Desktop/selenium_Test/updated_code.py", "w") as file:
            file.write(updated_script) 
        print(f"Script updated: {old_locator} → {new_locator}")
    except Exception as e:
        print(f"Failed to update script: {e}")

log_output = run_selenium_test()

if log_output:
    element_name, locator_type, locator_value = extract_failed_locator()
    if element_name and locator_type and locator_value:
        print(f"Broken locator found: {locator_type} = {locator_value}")

        with open("/Users/saisiddharthvemuri/Desktop/selenium_Test/Pfizer_Website.html", "r") as file:
            page_source = file.read()

        new_strategy, new_value = get_ai_suggested_locator(element_name, page_source)

        if new_strategy and new_value:
            print(f"AI suggests using: {new_strategy} = {new_value}")
            update_selenium_test_script((locator_type, locator_value), (new_strategy, new_value))
        else:
            print("AI failed to suggest a new locator.")
    else:
        print("No broken locators detected.")
