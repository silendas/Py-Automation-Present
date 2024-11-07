from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
from datetime import datetime
import pytz

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def login_dan_absen():
    driver = None
    try:
        username = os.getenv('UNBIN_USERNAME')
        password = os.getenv('UNBIN_PASSWORD')
        
        driver = setup_driver()
        driver.get("https://akademik.unbin.ac.id/absensi/")
        
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "userid"))
        )
        password_field = driver.find_element(By.NAME, "pin")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        driver.find_element(By.NAME, "login").click()
        
        time.sleep(5)
        
        if "logout" in driver.page_source.lower():
            print("Login dan Absen BERHASIL!")
            return True
        else:
            print("Login GAGAL!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    login_dan_absen()