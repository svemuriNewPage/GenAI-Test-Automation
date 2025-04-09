# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# import time

# LOCATOR_STRATEGIES = [
#     (By.ID, "submit-btn"),
#     (By.NAME, "submit"),
#     (By.CLASS_NAME, "btn-primary"),
#     (By.XPATH, "//button[contains(text(), 'Submit')]"),
#     (By.CSS_SELECTOR, "button[type='submit']"),
# ]

# def find_element_with_healing(driver, strategies):
#     """Try different locators if primary fails (self-healing mechanism)."""
#     for strategy, value in strategies:
#         try:
#             element = driver.find_element(strategy, value)
#             print(f"Element found using {strategy}: {value}")
#             return element
#         except:
#             continue
#     print("Element not found using any strategy.")
#     return None

# driver = webdriver.Chrome()

# driver.get("http://127.0.0.1:5500/Pfizer_Website.html")
# time.sleep(2)

# button = find_element_with_healing(driver, LOCATOR_STRATEGIES)

# if button:
#     button.click()
#     print("Button clicked successfully!")
# else:
#     print("Failed to find button.")

# driver.quit()
