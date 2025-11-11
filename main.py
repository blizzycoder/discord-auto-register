from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import logging
import string
import http.client
import json
import webbrowser
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_random_password(length=12):
    """Generate a strong random password"""
    
    lowercase = random.choice(string.ascii_lowercase)
    uppercase = random.choice(string.ascii_uppercase)
    digits = random.choice(string.digits)
    special = random.choice('!@#$%^&*')
    
  
    remaining = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*', k=length-4))
    

    password_chars = list(lowercase + uppercase + digits + special + remaining)
    random.shuffle(password_chars)
    
    return ''.join(password_chars)

def save_account_details(username, email, password):
    """Save account details to a text file with random number"""
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
    """Generate a temporary email using Gmailnator API"""
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
    """Verify email by checking inbox and clicking verification link"""
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
    """Setup Chrome driver with options to prevent crashes"""
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
    """Safely click an element with multiple fallback methods"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
        time.sleep(0.5)
        element.click()
        logger.info(f"Successfully clicked {description} with regular click")
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
    """Select date of birth"""
    try:
        logger.info("Starting date of birth selection")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='date'], [class*='birth'], [aria-label*='day']"))
        )
        
        date_dropdowns = driver.find_elements(By.CSS_SELECTOR, "div[role='button'], div[aria-haspopup='listbox']")
        logger.info(f"Found {len(date_dropdowns)} date dropdowns")
        
        if len(date_dropdowns) >= 3:
          
            safe_click(driver, date_dropdowns[0], "day dropdown")
            time.sleep(1)
            
            day_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='option']"))
            )
            for option in day_options:
                if option.text.strip() == "2":
                    safe_click(driver, option, "day option 2")
                    break
            time.sleep(1)
            
         
            safe_click(driver, date_dropdowns[1], "month dropdown")
            time.sleep(1)
            
            month_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='option']"))
            )
            for option in month_options:
                if "December" in option.text:
                    safe_click(driver, option, "month option December")
                    break
            time.sleep(1)
            
          
            safe_click(driver, date_dropdowns[2], "year dropdown")
            time.sleep(1)
            
            year_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='option']"))
            )
            for option in year_options:
                if option.text.strip() == "2004":
                    safe_click(driver, option, "year option 2004")
                    break
            time.sleep(1)
            
            logger.info("Date of birth selected successfully")
            return True
            
    except Exception as e:
        logger.error(f"Date selection failed: {e}")
        return False

def find_and_click_correct_checkbox(driver):
    """Find and click the CORRECT consent checkbox (Terms of Service)"""
    logger.info("Searching for the CORRECT consent checkbox...")
    

    logger.info("Strategy 1: Looking for checkbox near Terms of Service text")
    
    terms_texts = [
        "I have read and agree to Discord's Terms of Service",
        "Terms of Service",
        "Privacy Policy",
        "I agree to",
        "I have read and agree"
    ]
    
    for text in terms_texts:
        try:
            elements_with_text = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            logger.info(f"Found {len(elements_with_text)} elements with text: '{text}'")
            
            for element in elements_with_text:
                try:
                    nearby_checkboxes = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]/ancestor::*//input[@type='checkbox'] | //input[@type='checkbox'][preceding::*[contains(text(), '{text}')]] | //input[@type='checkbox'][following::*[contains(text(), '{text}')]]")
                    
                    for checkbox in nearby_checkboxes:
                        if checkbox.is_displayed() and checkbox.is_enabled():
                            logger.info(f"Found checkbox near '{text}', attempting to click")
                            
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                            time.sleep(1)
                            
                            if not checkbox.is_selected():
                                driver.execute_script("arguments[0].click();", checkbox)
                                time.sleep(1)
                                
                                if checkbox.is_selected():
                                    logger.info("Successfully checked the CORRECT consent checkbox!")
                                    return True
                            else:
                                logger.info("Correct checkbox was already checked")
                                return True
                except Exception as e:
                    logger.warning(f"Error with nearby checkbox for text '{text}': {e}")
        except Exception as e:
            logger.warning(f"Error searching for text '{text}': {e}")

    logger.info("Strategy 2: Targeting the second checkbox on the page")
    all_checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    logger.info(f"Found {len(all_checkboxes)} total checkboxes on the page")
    
    if len(all_checkboxes) >= 2:
        correct_checkbox = all_checkboxes[1]
        logger.info("Attempting to click the second checkbox (Terms of Service)")
        
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", correct_checkbox)
            time.sleep(1)
            
            if not correct_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", correct_checkbox)
                time.sleep(1)
                
                if correct_checkbox.is_selected():
                    logger.info("Successfully checked the second checkbox (Terms of Service)!")
                    return True
        except Exception as e:
            logger.error(f"Failed to click second checkbox: {e}")
    
    logger.error("Could not find or interact with the CORRECT consent checkbox")
    return False

def detect_and_handle_captcha(driver):
    """Detect and handle various types of captchas"""
    logger.info("Checking for captcha...")
    
    driver.save_screenshot("before_captcha.png")
    logger.info("Saved screenshot: before_captcha.png")
    
    captcha_indicators = [
        "captcha",
        "hcaptcha",
        "recaptcha",
        "verify you are human",
        "i'm not a robot",
        "security check",
        "challenge"
    ]
    
    page_text = driver.page_source.lower()
    for indicator in captcha_indicators:
        if indicator in page_text:
            logger.info(f"Found captcha indicator: {indicator}")
            break
    
    captcha_selectors = [
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        "div[class*='captcha']",
        "div[class*='recaptcha']",
        "div[class*='hcaptcha']",
        "div.g-recaptcha",
        "div.h-captcha"
    ]
    
    captcha_found = False
    for selector in captcha_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                logger.info(f"Found captcha element with selector: {selector}")
                captcha_found = True
                break
        except:
            continue
    
    if captcha_found:
        logger.info("Captcha detected! Starting handling process...")
        return handle_captcha_manual(driver)
    
    logger.info("No captcha detected")
    return True

def handle_captcha_manual(driver):
    """Handle captcha by waiting for manual intervention"""
    logger.info("=== CAPTCHA DETECTED ===")
    logger.info("Manual intervention required!")
    logger.info("Please solve the captcha manually in the browser window")
    logger.info("The script will wait for you to complete it...")
    
    driver.save_screenshot("captcha_detected.png")
    logger.info("Saved captcha screenshot: captcha_detected.png")
    
    input("After solving the captcha, press Enter to continue...")
    
    try:
        time.sleep(3)
        current_url = driver.current_url
        if "register" not in current_url.lower():
            logger.info("Successfully passed captcha! Page moved forward.")
            return True
        else:
            logger.info("Still on registration page, checking if captcha is gone...")
            captcha_still_present = False
            for selector in ["iframe[src*='recaptcha']", "iframe[src*='hcaptcha']", "div.g-recaptcha"]:
                try:
                    if driver.find_elements(By.CSS_SELECTOR, selector):
                        captcha_still_present = True
                        break
                except:
                    continue
            
            if not captcha_still_present:
                logger.info("Captcha appears to be solved!")
                return True
            else:
                logger.warning("Captcha might still be present. Trying to continue anyway...")
                return True
                
    except Exception as e:
        logger.error(f"Error checking captcha status: {e}")
        return False

def fill_basic_info(driver, email, username, password):
    """Fill in the basic registration information"""
    try:
        logger.info("Filling basic information")
        

        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_field.clear()
        email_field.send_keys(email)
        logger.info("Email filled")
        
    
        username_field = driver.find_element(By.NAME, "username")
        username_field.clear()
        username_field.send_keys(username)
        logger.info("Username filled")
        
  
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        logger.info("Password filled")
        
     
        try:
            global_name_field = driver.find_element(By.NAME, "global_name")
            global_name_field.clear()
            global_name_field.send_keys(username)
            logger.info("Global name filled")
        except NoSuchElementException:
            logger.info("Global name field not found, skipping")
            
        time.sleep(2)
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
        time.sleep(3)
        
    
        if not fill_basic_info(driver, email, username, password):
            raise Exception("Failed to fill basic information")
        

        if not select_dob_simple(driver):
            raise Exception("Failed to select date of birth")
        
      
        if not find_and_click_correct_checkbox(driver):
            raise Exception("Failed to handle consent checkbox")
        
 
        if not detect_and_handle_captcha(driver):
            logger.warning("Captcha handling may have failed, but continuing...")
 
        logger.info("Looking for submit button")
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        
        driver.execute_script("arguments[0].click();", submit_button)
        logger.info("Form submitted")
        
  
        time.sleep(5)
        if not detect_and_handle_captcha(driver):
            logger.warning("Captcha appeared after submission")
        

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
                delay = random.randint(15, 45)
                logger.info(f"Waiting {delay} seconds before next account...")
                time.sleep(delay)
                
    except Exception as e:
        logger.error(f"Main loop error: {e}")

if __name__ == "__main__":
    main()