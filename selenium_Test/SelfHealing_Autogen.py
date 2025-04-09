import os
import re
import subprocess
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from browser_use import Agent as BrowserAgent
from langchain_openai import ChatOpenAI
from autogen_core.models import UserMessage
from autogen_core.tools import FunctionTool

# Load environment variables
load_dotenv()

# --- Model Client ---
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    seed=42
)

# --- Tool Functions ---
async def run_selenium_test() -> str:
    """Run Selenium test and return logs."""
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

async def extract_failed_locators(log_text: str) -> list:
    """Extract failed locator information from test logs."""
    pattern = r"Error: Element (.*?) not found - \((.*?), (.*?)\)"
    return [
        {"element_name": e.strip(), "by": b.strip(), "locator": l.strip()}
        for e, b, l in re.findall(pattern, log_text)
    ]

async def update_test_script(old_locator: str, new_locator: str) -> str:
    """Update the test script with new locator."""
    path = "/Users/saisiddharthvemuri/Desktop/selenium_Test/updated_code.py"
    try:
        with open(path, "r") as f:
            code = f.read()
        updated_code = re.sub(re.escape(old_locator), new_locator, code)
        with open(path, "w") as f:
            f.write(updated_code)
        return "Script updated successfully."
    except Exception as e:
        return f"Script update failed: {str(e)}"

async def suggest_new_locator(element_name: str, html_content: str) -> str:
    """Suggest a new locator using LLM and DOM."""
    prompt = (
        f"You're a QA expert. The locator for '{element_name}' is broken. "
        f"Here is a snippet of the HTML:\n{html_content[:2000]}\n"
        f"Return a corrected locator in Python tuple format (By.XPATH, '//path'). "
        f"Handle edge cases like moved content, duplicate elements, popups, and developer inconsistency."
    )
    response = await model_client.create([UserMessage(content=prompt, source="user")])
    return response.content.strip()

async def fetch_dom_from_browser(url: str) -> str:
    """Use browser-use to fetch the page's DOM."""
    agent = BrowserAgent(
        task=f"Go to {url} and return the DOM.",
        llm=ChatOpenAI(model="gpt-4o")
    )
    result = await agent.run()
    return str(result)

# Register tools
from autogen_core.tools import FunctionTool

run_selenium_test_tool = FunctionTool(
    func=run_selenium_test,
    name="run_selenium_test",
    description="Runs the Selenium test script and returns logs"
)

extract_failed_locators_tool = FunctionTool(
    func=extract_failed_locators,
    name="extract_failed_locators",
    description="Extracts broken locator info from logs"
)

update_test_script_tool = FunctionTool(
    func=update_test_script,
    name="update_test_script",
    description="Replaces old locator with new one in test script"
)

suggest_new_locator_tool = FunctionTool(
    func=suggest_new_locator,
    name="suggest_new_locator",
    description="Suggests a new locator using LLM"
)

fetch_dom_from_browser_tool = FunctionTool(
    func=fetch_dom_from_browser,
    name="fetch_dom_from_browser",
    description="Fetches page DOM using browser-use"
)

# --- Agents ---
manager = AssistantAgent(
    name="Manager",
    system_message="""
        You are the project manager and coordinator.
        Oversee the testing flow: run the test, extract failures, verify via browser, get suggestions,
        and update the script. Handle all cases like changed navbar indices, moved content,
        popups blocking clicks, content changes, and duplicate locators from different developers.
        All work must happen without human input.
    """,
    model_client=model_client
)

auto_tester = AssistantAgent(
    name="AutoFixer",
    system_message="""
        You are a multi-skilled automation agent. You:
        - Run Selenium tests
        - Parse logs for broken locators
        - Get browser DOM if needed
        - Call LLM for fixed selectors
        - Update scripts
        Use available tools to solve all test failures automatically.
    """,
    model_client=model_client,
    tools=[run_selenium_test_tool, extract_failed_locators_tool, suggest_new_locator_tool, update_test_script_tool, fetch_dom_from_browser_tool]
)

browser_verifier = AssistantAgent(
    name="BrowserAgent",
    system_message="""
        You are a verification agent. If a selector seems broken, double-check
        by browsing the site using browser-use and extracting the DOM.
    """,
    model_client=model_client
)

# --- Group Chat Setup ---
groupchat = RoundRobinGroupChat(
    participants=[manager, auto_tester, browser_verifier],
    termination_condition=MaxMessageTermination(20)
)

# --- Start the Flow ---
import asyncio

async def main():
    await groupchat.run(task="Begin the automated Selenium test and healing process on http://127.0.0.1:5500/pfizerForAll.html")

if __name__ == "__main__":
    asyncio.run(main())
