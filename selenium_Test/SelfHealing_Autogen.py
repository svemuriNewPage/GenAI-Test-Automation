import os
import re
import subprocess
import asyncio
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from browser_use import Agent as BrowserAgent
from langchain_openai import ChatOpenAI
from autogen_core.models import UserMessage
from autogen_core.tools import FunctionTool

# === ENV SETUP ===
load_dotenv()

model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    seed=42
)

# === TOOL FUNCTIONS ===

TEST_SCRIPT_PATH = "/Users/saisiddharthvemuri/Desktop/selenium_Test/Pfizer_playWright.mts"
UPDATED_SCRIPT_PATH = TEST_SCRIPT_PATH.replace(".mts", ".updated.mts")

async def run_playwright_test() -> str:
    """Runs the Playwright test and returns logs."""
    try:
        result = subprocess.run(["npx", "tsx", TEST_SCRIPT_PATH], capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running script: {str(e)}"

async def extract_failed_locators(log_text: str) -> list:
    """Extract failed elements based on custom failure output in the Playwright test."""
    pattern = r"❌ Navigate to: (.+?) - (.+)"
    return [{"element_name": match[0], "error": match[1]} for match in re.findall(pattern, log_text)]

async def fetch_dom_from_browser(url: str) -> str:
    """Fetch entire DOM using BrowserAgent."""
    agent = BrowserAgent(
        task=f"Visit {url} and return the complete DOM as string.",
        llm=ChatOpenAI(model="gpt-4o")
    )
    # return await agent.run()
    result = await agent.run()
    return result[-1].content if result else ""


async def suggest_new_locator(element_name: str, page_source: str) -> str:
    """Ask the model to fix the broken locator using DOM."""
    prompt = f"""
You are a helpful agent. The Playwright test failed for element '{element_name}'.

Here is a DOM snippet from the page:
-------------------
{page_source[:2000]}
-------------------

Suggest a better locator to replace `page.locator("text={element_name}")`.
Prefer:
- page.locator('role=') or
- page.locator('[aria-label=]') or
- page.locator('[data-testid=]')

Give me only the fixed Playwright selector code like:
page.locator('[aria-label="xyz"]')
"""
    response = await model_client.create([UserMessage(content=prompt, source="user")])
    return response.content.strip()

async def update_test_script(old_text: str, new_code: str) -> str:
    try:
        with open(TEST_SCRIPT_PATH, "r") as file:
            content = file.read()

        if f'locator("text={old_text}")' not in content:
            return f"Locator for text={old_text} not found in script."

        # Replace all instances
        updated = re.sub(rf'locator\(["\']text={re.escape(old_text)}["\']\)', new_code, content)

        with open(UPDATED_SCRIPT_PATH, "w") as file:
            file.write(updated)

        return f"✅ Updated script saved to: {UPDATED_SCRIPT_PATH}"
    except Exception as e:
        return f"❌ Script update failed: {str(e)}"

# === REGISTER TOOLS ===
run_playwright_test_tool = FunctionTool(run_playwright_test, name="run_playwright_test", description="Run Playwright test script")
extract_failed_locators_tool = FunctionTool(extract_failed_locators, name="extract_failed_locators", description="Extract broken locators from logs")
fetch_dom_tool = FunctionTool(fetch_dom_from_browser, name="fetch_dom_from_browser", description="Get full DOM from browser")
suggest_locator_tool = FunctionTool(suggest_new_locator, name="suggest_new_locator", description="Suggest new locator from DOM and label")
update_script_tool = FunctionTool(update_test_script, name="update_test_script", description="Update Playwright .mts script")

# === AUTOFIXER AGENT ===
auto_fixer = AssistantAgent(
    name="AutoFixer",
    system_message="""
You are a smart Playwright script repair bot.
You run the test, extract failed cases, inspect the page, and patch the script with new locators.
""",
    model_client=model_client,
    tools=[
        run_playwright_test_tool,
        extract_failed_locators_tool,
        fetch_dom_tool,
        suggest_locator_tool,
        update_script_tool
    ]
)

# === FLOW ===
async def main():
    # Step 1: Run test
    logs = await run_playwright_test()
    print("[LOGS] Script executed.")

    # Step 2: Extract failures
    failures = await extract_failed_locators(logs)
    print(f"[FAILURES FOUND] {len(failures)}")

    # Step 3: For each failure, inspect and patch
    for fail in failures:
        element_text = fail["element_name"]
        print(f"\n🔧 Fixing locator for: {element_text}")

        dom = await fetch_dom_from_browser("https://www.pfizerforall.com/")
        new_code = await suggest_new_locator(element_text, dom)
        print(f"🧠 Suggested Fix: {new_code}")

        patch = await update_test_script(element_text, new_code)
        print(patch)

    print("\n✅ Healing complete.")

asyncio.run(main())
