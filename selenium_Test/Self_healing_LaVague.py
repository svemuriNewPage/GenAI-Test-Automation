from lavague.contexts.openai import OpenaiContext
from lavague.drivers.selenium import SeleniumDriver
from lavague.core import ActionEngine, WorldModel
from lavague.core.agents import WebAgent
from lavague.core.token_counter import TokenCounter
import nltk
import os

nltk.download("punkt")
nltk.download("stopwords")

# Constants
URL = "https://www.pfizerforall.com/"
FEATURE_FILE_PATH = "/Users/saisiddharthvemuri/Desktop/selenium_Test/pfizerForAll.feature"

# GPT-4o-mini context
context = OpenaiContext(llm="gpt-4o", mm_llm="gpt-4o")

# Setup driver and components
selenium_driver = SeleniumDriver(headless=False)
action_engine = ActionEngine.from_context(context=context, driver=selenium_driver)
world_model = WorldModel.from_context(context)
token_counter = TokenCounter(log=True)

# WebAgent setup
agent = WebAgent(
    world_model=world_model,
    action_engine=action_engine,
    token_counter=token_counter,
    n_steps=50,  # allow more steps to visit more pages
    clean_screenshot_folder=True
)

# Objective for recursive site exploration and gherkin generation
OBJECTIVE =  """
You are a test automation agent. Your job is to explore the current page, identify key UI elements such as navbar, search box, popup, content sections, duplicate elements etc., and return a plain text Gherkin feature file.
Return all the gherklin scenarios you can find by crawling through the website, only then return the gherkin script.
NOTE: If you do not find next Engine, creatively think of one in the context and baed on that select next engine.
Use only this format and beautification to be written into the feature file strictly (no markdown, no explanations):

Feature: Cart

  Scenario: Add and remove a single product from cart
    Given the user is on the homepage
    When the user clicks on "Accepter" to accept cookies
    And the user enters "Zero to One" into the search bar and press Enter
    And the user clicks on the first product in the search results
    And the user clicks on the "Ajouter au panier" button
    And the confirmation message is displayed
    And the user clicks on "Aller au panier" under "Passer la commande"
    And the user clicks on "Supprimer" from the cart page
    Then the cart should be empty

...

Do not say "Here is the file" or use any formatting like triple backticks or a numbered list. Just return the full feature file content once all the components are explored.
"""



# Start task
agent.get(URL)
result = agent.run(OBJECTIVE, display=True)

# Save only Gherkin to feature file
with open(FEATURE_FILE_PATH, "w") as file:
    file.write(result.output)

print(f"Gherkin script saved to: {FEATURE_FILE_PATH}")
# from lavague.contexts.openai import OpenaiContext
# from lavague.drivers.selenium import SeleniumDriver
# from lavague.core import ActionEngine, WorldModel
# from lavague.core.agents import WebAgent
# from lavague.core.token_counter import TokenCounter
# import nltk
# import os

# nltk.download("punkt")
# nltk.download("stopwords")

# # Constants
# URL = "https://www.pfizerforall.com/"
# FEATURE_FILE_PATH = "/Users/saisiddharthvemuri/Desktop/selenium_Test/pfizerForAll.feature"

# # GPT-4o-mini context
# context = OpenaiContext(llm="gpt-4o-mini", mm_llm="gpt-4o-mini")

# # Setup driver and components
# selenium_driver = SeleniumDriver(headless=False)
# action_engine = ActionEngine.from_context(context=context, driver=selenium_driver)
# world_model = WorldModel.from_context(context)
# token_counter = TokenCounter(log=True)

# # WebAgent setup
# agent = WebAgent(
#     world_model=world_model,
#     action_engine=action_engine,
#     token_counter=token_counter,
#     n_steps=50,  # allow more steps to visit more pages
#     clean_screenshot_folder=True
# )

# # Objective for recursive site exploration and gherkin generation
# OBJECTIVE = """
# You are a test automation assistant. Open the homepage once, and then recursively crawl through all navigable internal links on the site. For each unique page:

# - Analyze and extract testable elements (navbars, search boxes, popups, dynamic content, duplicated UI elements, etc.)
# - Identify any broken or outdated locators. If found, correct them using the surrounding context.
# - Generate cleanly indented Gherkin test cases in the Given-When-Then format for each functionality observed.
# - Output only the Gherkin script in plain text format (no markdown, no code blocks, no extra text).
# - Combine all test cases across all visited pages into a single feature file.

# Use this format:

# Feature: [Auto-generated test title]

#   Scenario: [Description of a test case]
#     Given ...
#     When ...
#     Then ...

# Only return the cumulative Gherkin script for the whole site.
# """

# # # Start task
# # agent.get(URL)
# # result = agent.run(OBJECTIVE, display=True)

# # # Save only Gherkin to feature file
# # with open(FEATURE_FILE_PATH, "w") as file:
# #     file.write(result.output)

# # print(f"Gherkin script saved to: {FEATURE_FILE_PATH}")

# # Start task
# agent.get(URL)
# result = agent.run_step(OBJECTIVE)

# # Save only Gherkin to feature file
# with open(FEATURE_FILE_PATH, "w") as file:
#     file.write(result.output)

# print(f"Gherkin script saved to: {FEATURE_FILE_PATH}")
