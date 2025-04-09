import subprocess
import re
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- Model Client Config (v0.4 style) ---
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),  # Load from environment (recommended)
    temperature=0,
    seed=42
)

# --- Agents (v0.4 style) ---
manager = AssistantAgent(
    name="Manager",
    system_message="You are the top-level task manager and coordinator.",
    model_client=model_client
)

test_executor = AssistantAgent(
    name="TestExecutor",
    system_message="You run Selenium tests and detect broken locators.",
    model_client=model_client
)

ai_fixer = AssistantAgent(
    name="AIFixer",
    system_message="You analyze HTML and suggest correct locators.",
    model_client=model_client
)

script_updater = AssistantAgent(
    name="ScriptUpdater",
    system_message="You update Selenium test scripts with fixed locators.",
    model_client=model_client
)

# --- Helper Functions ---
def run_selenium_test():
    try:
        result = subprocess.run(
            ["python", "/Users/saisiddharthvemuri/Desktop/selenium_Test/Selenium_Test.py"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return f"Error running test script: {str(e)}"

def extract_failed_locator(log_text: str):
    failures = []
    pattern = r"Error: Element (.*?) not found - \((.*?)\, (.*?)\)"
    for match in re.finditer(pattern, log_text):
        element_name, by_type, locator = match.groups()
        failures.append({
            "element_name": element_name.strip(),
            "by": by_type.strip(),
            "locator": locator.strip()
        })
    return failures

async def get_ai_suggested_locator(element_name: str, html_content: str) -> str:
    # Use the model client to ask for a better locator suggestion
    from autogen_core.models import UserMessage
    prompt = (
        f"You are an expert QA automation engineer.\n"
        f"Here is a snippet of HTML:\n\n{html_content[:1500]}...\n\n"
        f"What is a better locator for the element called '{element_name}'?\n"
        f"Respond only in Python tuple format like (By.XPATH, '//your/path')."
    )
    response = await model_client.create([UserMessage(content=prompt, source="user")])
    return response.content.strip()

def update_selenium_test_script(old_locator, new_locator):
    script_path = "/Users/saisiddharthvemuri/Desktop/selenium_Test/updated_code.py"
    try:
        with open(script_path, "r") as file:
            code = file.read()

        pattern = re.escape(old_locator)
        updated_code = re.sub(pattern, new_locator, code)

        with open(script_path, "w") as file:
            file.write(updated_code)
        return "Script updated successfully."
    except Exception as e:
        return f"Failed to update script: {str(e)}"

# --- Main Execution Flow (async) ---
import asyncio

async def main():
    log_text = run_selenium_test()
    print("Test Log:\n", log_text)

    failed_locators = extract_failed_locator(log_text)
    print("Failed Locators:\n", failed_locators)

    with open("/Users/saisiddharthvemuri/Desktop/selenium_Test/pfizerForAll.html", "r") as html_file:
        html_content = html_file.read()

    for failure in failed_locators:
        element_name = failure["element_name"]
        old_locator = failure["locator"]

        print(f"\nFixing '{element_name}'...")
        new_locator = await get_ai_suggested_locator(element_name, html_content)
        print(f"Suggested: {new_locator}")

        result = update_selenium_test_script(old_locator, new_locator)
        print(f"Update Result: {result}")

    await model_client.close()

# Run it
asyncio.run(main())
