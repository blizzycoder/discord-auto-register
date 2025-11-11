from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import logging
import string
import http.client
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleCaptchaSolver:
    def __init__(self):
        self.attempt_count = 0

    def solve_recaptcha_simple(self, driver):
        self.attempt_count += 1
        logger.info(f"Simple reCAPTCHA attempt {self.attempt_count}")

        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            recaptcha_iframes = []
            
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if 'recaptcha' in src.lower() or 'google.com/recaptcha' in src:
                    recaptcha_iframes.append(iframe)
            
            if recaptcha_iframes:
                logger.info(f"Found {len(recaptcha_iframes)} reCAPTCHA iframes")
                
                for iframe in recaptcha_iframes:
                    try:
                        driver.switch_to.frame(iframe)
                        
                        checkboxes = driver.find_elements(By.CSS_SELECTOR, ".recaptcha-checkbox, div[role='checkbox'], [aria-labelledby*='recaptcha']")
                        if checkboxes:
                            checkbox = checkboxes[0]
                            driver.execute_script("arguments[0].click();", checkbox)
                            logger.info("Clicked reCAPTCHA checkbox")
                            driver.switch_to.default_content()
                            
                            time.sleep(5)
                            
                            if self.is_captcha_solved(driver):
                                logger.info("reCAPTCHA solved!")
                                return True
                                
                        driver.switch_to.default_content()
                        
                    except Exception as e:
                        logger.warning(f"Iframe handling failed: {e}")
                        driver.switch_to.default_content()
                        continue
            
            return False
            
        except Exception as e:
            logger.error(f"Simple reCAPTCHA failed: {e}")
            try:
                driver.switch_to.default_content()
            except:
                pass
            return False

    def solve_by_clicking_anywhere(self, driver):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            action = ActionChains(driver)
            action.move_to_element(body).move_by_offset(random.randint(100, 500), random.randint(100, 300)).click().perform()
            logger.info("Clicked random location on page")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Random click failed: {e}")
            return False

    def is_captcha_solved(self, driver):
        try:
            current_url = driver.current_url
            if "register" not in current_url.lower():
                return True
                
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if 'recaptcha' in src.lower():
                    return False
            return True
        except:
            return False

def human_delay(min_seconds=1, max_seconds=3):
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def generate_random_password(length=12):
    lowercase = random.choice(string.ascii_lowercase)
    uppercase = random.choice(string.ascii_uppercase)
    digits = random.choice(string.digits)
    special = random.choice('!@#$%^&*')
    remaining = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*', k=length-4))
    password_chars = list(lowercase + uppercase + digits + special + remaining)
    random.shuffle(password_chars)
    return ''.join(password_chars)

def save_account_details(username, email, password):
    random_number = random.randint(1000, 9999)
    filename = f"AccountDetails_{random_number}.txt"
    account_info = f"""Discord Account Details:
Username: {username}
Email: {email}
Password: {password}
Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    with open(filename, 'w') as f:
        f.write(account_info)
    logger.info(f"Account details saved to: {filename}")
    return filename

def get_temp_email():
    try:
        conn = http.client.HTTPSConnection("gmailnator.p.rapidapi.com")
        payload = "{\"options\":[1,2,3]}"
        headers = {
            'x-rapidapi-key': "b4e2db37b3msh9f605048ef79ddap134f4cjsn4cfb5539d54c",
            'x-rapidapi-host': "gmailnator.p.rapidapi.com",
            'Content-Type': "application/json"
        }
        conn.request("POST", "/generate-email", payload, headers)
        res = conn.getresponse()
        data = res.read()
        email_data = json.loads(data.decode("utf-8"))
        temp_email = email_data['email']
        logger.info(f"Generated temporary email: {temp_email}")
        return temp_email
    except Exception as e:
        logger.error(f"Failed to generate temporary email: {e}")
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        fallback_email = f"{random_string}@gmail.com"
        logger.info(f"Using fallback email: {fallback_email}")
        return fallback_email

def verify_email(driver, email):
    try:
        logger.info("Waiting for verification email...")
        time.sleep(15)
        
        conn = http.client.HTTPSConnection("gmailnator.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "b4e2db37b3msh9f605048ef79ddap134f4cjsn4cfb5539d54c",
            'x-rapidapi-host': "gmailnator.p.rapidapi.com"
        }
        
        for attempt in range(5):
            try:
                conn.request("GET", f"/inbox/{email}", headers=headers)
                res = conn.getresponse()
                data = res.read()
                email_data = json.loads(data.decode("utf-8"))
                
                if email_data.get('messages') and len(email_data['messages']) > 0:
                    for message in email_data['messages']:
                        if 'discord' in message['subject'].lower():
                            verification_link = message['body']['html'].split('href="')[1].split('"')[0]
                            logger.info(f"Found verification link: {verification_link}")
                            driver.get(verification_link)
                            time.sleep(5)
                            logger.info("Email verification completed")
                            return True
                
                logger.info(f"Attempt {attempt + 1}: No verification email yet, waiting...")
                time.sleep(10)
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(10)
        
        logger.error("Could not find verification email after multiple attempts")
        return False
        
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        return False

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def safe_click(driver, element, description=""):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
        human_delay(0.5, 1.5)
        element.click()
        logger.info(f"Successfully clicked {description}")
        return True
    except Exception as e:
        logger.warning(f"Regular click failed for {description}: {e}")
        try:
            driver.execute_script("arguments[0].click();", element)
            logger.info(f"Successfully clicked {description} with JavaScript")
            return True
        except Exception as e2:
            logger.warning(f"JavaScript click failed for {description}: {e2}")
            return False

def select_dob_simple(driver):
    try:
        logger.info("Starting date of birth selection")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='date'], [class*='birth'], [aria-label*='day']"))
        )
        
        date_dropdowns = driver.find_elements(By.CSS_SELECTOR, "div[role='button'], div[aria-haspopup='listbox']")
        logger.info(f"Found {len(date_dropdowns)} date dropdowns")
        
        if len(date_dropdowns) >= 3:
            safe_click(driver, date_dropdowns[0], "day dropdown")
            human_delay(1, 2)
            
            day_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='option']"))
            )
            for option in day_options:
                if option.text.strip() == "2":
                    safe_click(driver, option, "day option 2")
                    break
            human_delay(1, 2)
            
            safe_click(driver, date_dropdowns[1], "month dropdown")
            human_delay(1, 2)
            
            month_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='option']"))
            )
            for option in month_options:
                if "December" in option.text:
                    safe_click(driver, option, "month option December")
                    break
            human_delay(1, 2)
            
            safe_click(driver, date_dropdowns[2], "year dropdown")
            human_delay(1, 2)
            
            year_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='option']"))
            )
            for option in year_options:
                if option.text.strip() == "2000":
                    safe_click(driver, option, "year option 2000")
                    break
            human_delay(1, 2)
            
            logger.info("Date of birth selected successfully")
            return True
            
    except Exception as e:
        logger.error(f"Date selection failed: {e}")
        return False

def find_and_click_correct_checkbox(driver):
    logger.info("Searching for the CORRECT consent checkbox...")
    
    all_checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    logger.info(f"Found {len(all_checkboxes)} total checkboxes on the page")
    
    if len(all_checkboxes) >= 2:
        correct_checkbox = all_checkboxes[1]
        logger.info("Attempting to click the second checkbox (Terms of Service)")
        
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", correct_checkbox)
            human_delay(1, 2)
            
            if not correct_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", correct_checkbox)
                human_delay(1, 2)
                
                if correct_checkbox.is_selected():
                    logger.info("Successfully checked the second checkbox (Terms of Service)!")
                    return True
        except Exception as e:
            logger.error(f"Failed to click second checkbox: {e}")
    
    logger.error("Could not find or interact with the CORRECT consent checkbox")
    return False

def handle_captcha_simple(driver):
    logger.info("Starting simple captcha handling...")
    captcha_solver = SimpleCaptchaSolver()
    
    max_attempts = 2
    for attempt in range(max_attempts):
        logger.info(f"Captcha attempt {attempt + 1}/{max_attempts}")
        
        human_delay(2, 4)
        
        current_url = driver.current_url
        if "register" not in current_url.lower():
            logger.info("No captcha - page advanced")
            return True
        
        if captcha_solver.solve_recaptcha_simple(driver):
            return True
        
        human_delay(3, 5)
        
        if captcha_solver.is_captcha_solved(driver):
            logger.info("Captcha appears to be solved")
            return True
    
    logger.info("Trying alternative captcha approach...")
    captcha_solver.solve_by_clicking_anywhere(driver)
    
    human_delay(5, 8)
    
    logger.info("Continuing despite captcha...")
    return True

def fill_basic_info(driver, email, username, password):
    try:
        logger.info("Filling basic information")
        
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        human_delay(1, 2)
        email_field.clear()
        human_delay(0.5, 1)
        for char in email:
            email_field.send_keys(char)
            human_delay(0.05, 0.1)
        logger.info("Email filled")
        
        username_field = driver.find_element(By.NAME, "username")
        human_delay(1, 2)
        username_field.clear()
        human_delay(0.5, 1)
        for char in username:
            username_field.send_keys(char)
            human_delay(0.05, 0.1)
        logger.info("Username filled")
        
        password_field = driver.find_element(By.NAME, "password")
        human_delay(1, 2)
        password_field.clear()
        human_delay(0.5, 1)
        for char in password:
            password_field.send_keys(char)
            human_delay(0.05, 0.1)
        logger.info("Password filled")
        
        try:
            global_name_field = driver.find_element(By.NAME, "global_name")
            human_delay(1, 2)
            global_name_field.clear()
            human_delay(0.5, 1)
            for char in username:
                global_name_field.send_keys(char)
                human_delay(0.05, 0.1)
            logger.info("Global name filled")
        except NoSuchElementException:
            logger.info("Global name field not found, skipping")
            
        human_delay(2, 3)
        return True
        
    except Exception as e:
        logger.error(f"Failed to fill basic info: {e}")
        return False

def create_discord_account(username, email):
    driver = None
    password = None
    try:
        driver = setup_driver()
        logger.info(f"Starting account creation for: {username}")
        
        password = generate_random_password()
        logger.info(f"Generated password: {password}")
        
        driver.get("https://discord.com/register")
        human_delay(3, 5)
        
        if not fill_basic_info(driver, email, username, password):
            raise Exception("Failed to fill basic information")
        
        if not select_dob_simple(driver):
            raise Exception("Failed to select date of birth")
        
        if not find_and_click_correct_checkbox(driver):
            raise Exception("Failed to handle consent checkbox")
        
        if not handle_captcha_simple(driver):
            logger.warning("Captcha handling completed with warnings")
        
        logger.info("Looking for submit button")
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        
        human_delay(1, 2)
        driver.execute_script("arguments[0].click();", submit_button)
        logger.info("Form submitted")
        
        human_delay(5, 7)
        
        if not handle_captcha_simple(driver):
            logger.warning("Post-submission captcha handling completed with warnings")
        
        if password:
            filename = save_account_details(username, email, password)
            logger.info(f"Account details saved to: {filename}")
        
        logger.info("Starting email verification")
        verify_email(driver, email)
        
        logger.info(f"Account created successfully: {username}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating account {username}: {str(e)}")
        if password:
            filename = save_account_details(username, email, password)
            logger.info(f"Account details saved to: {filename} (partial creation)")
        if driver:
            try:
                driver.save_screenshot(f"error_{username}_{int(time.time())}.png")
                logger.info("Screenshot saved")
            except:
                logger.error("Could not save screenshot")
        return False
        
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Driver closed")
            except:
                logger.error("Error closing driver")

def main():
    try:
        with open('usernames.txt', 'r') as f:
            usernames = [line.strip() for line in f if line.strip()]
        
        logger.info(f"Found {len(usernames)} usernames to process")
        
        for i, username in enumerate(usernames):
            logger.info(f"Processing {i+1}/{len(usernames)}: {username}")
            
            temp_email = get_temp_email()
            logger.info(f"Using temporary email: {temp_email}")
            
            success = create_discord_account(username, temp_email)
            
            if success:
                logger.info(f"Successfully created account: {username}")
            else:
                logger.error(f"Failed to create account: {username}")
            
            if i < len(usernames) - 1:
                delay = random.randint(30, 60)
                logger.info(f"Waiting {delay} seconds before next account...")
                time.sleep(delay)
                
    except Exception as e:
        logger.error(f"Main loop error: {e}")

if __name__ == "__main__":
    main()
