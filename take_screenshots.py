import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'regex_nfa_dfa_converter', 'screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def setup_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1400,1050')
    driver = webdriver.Chrome(options=options)
    return driver

def capture():
    driver = setup_driver()
    try:
        print("Opening http://localhost:8501 ...")
        driver.get('http://localhost:8501')
        
        # Wait for inputs to appear
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
        )
        time.sleep(3)
        print("Page loaded successfully.")

        # 1. Capture App Home
        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, 'app_home.png'))
        print("Captured app_home.png")

        # 2. Click Convert & Analyze
        btn = driver.find_element(By.XPATH, "//button[contains(., 'Convert')]")
        btn.click()
        time.sleep(4)
        print("Clicked Convert & Analyze button.")

        # 3. Capture Regex input area
        input_elem = driver.find_element(By.XPATH, "//input[@type='text']")
        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, 'regex_input.png'))
        print("Captured regex_input.png")

        # 4. Capture NFA table (scroll to NFA section)
        tables = driver.find_elements(By.CSS_SELECTOR, "[data-testid='stDataFrame']")
        if len(tables) >= 1:
            tables[0].screenshot(os.path.join(SCREENSHOT_DIR, 'nfa_table.png'))
            print("Captured nfa_table.png")

        # 5. Capture DFA table
        if len(tables) >= 2:
            tables[1].screenshot(os.path.join(SCREENSHOT_DIR, 'dfa_table.png'))
            print("Captured dfa_table.png")

        # 6. Capture Accepted String
        accept_boxes = driver.find_elements(By.CSS_SELECTOR, ".result-accepted")
        if accept_boxes:
            accept_boxes[0].screenshot(os.path.join(SCREENSHOT_DIR, 'string_accepted.png'))
            print("Captured string_accepted.png")

        # 7. Test string rejection ("aba")
        inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        if len(inputs) >= 2:
            test_input = inputs[1]
            test_input.send_keys(Keys.CONTROL + "a")
            test_input.send_keys("aba")
            test_input.send_keys(Keys.ENTER)
            time.sleep(2)
            btn = driver.find_element(By.XPATH, "//button[contains(., 'Convert')]")
            btn.click()
            time.sleep(3)
            
            reject_boxes = driver.find_elements(By.CSS_SELECTOR, ".result-rejected")
            if reject_boxes:
                reject_boxes[0].screenshot(os.path.join(SCREENSHOT_DIR, 'string_rejected.png'))
                print("Captured string_rejected.png")
            else:
                driver.save_screenshot(os.path.join(SCREENSHOT_DIR, 'string_rejected.png'))
                print("Saved fallback page screenshot for string_rejected.png")

        # 8. Test invalid regex "(a|"
        inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        if len(inputs) >= 1:
            regex_input = inputs[0]
            regex_input.send_keys(Keys.CONTROL + "a")
            regex_input.send_keys(Keys.BACKSPACE)
            regex_input.send_keys("(a|")
            btn = driver.find_element(By.XPATH, "//button[contains(., 'Convert')]")
            btn.click()
            time.sleep(3)

            error_boxes = driver.find_elements(By.CSS_SELECTOR, ".result-error")
            if error_boxes:
                error_boxes[0].screenshot(os.path.join(SCREENSHOT_DIR, 'error_handling.png'))
                print("Captured error_handling.png")

        print("All screenshots captured successfully!")

    finally:
        driver.quit()

if __name__ == '__main__':
    capture()
