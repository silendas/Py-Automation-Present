from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
from datetime import datetime
import pytz

def get_jakarta_time():
    return datetime.now(pytz.timezone('Asia/Jakarta'))

def is_absen_time():
    now = get_jakarta_time()
    hour = now.hour
    minute = now.minute
    
    # Jadwal 1: 09:28-09:31
    if hour == 9 and 28 <= minute <= 31:
        return "jadwal_1"
    # Jadwal 2: 13:28-13:31
    elif hour == 13 and 28 <= minute <= 31:
        return "jadwal_2"
    else:
        return None

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def login_dan_absen():
    jadwal = is_absen_time()
    if not jadwal:
        print("Bukan waktu absen!")
        return False
        
    driver = None
    try:
        waktu = get_jakarta_time()
        print(f"Memulai proses absen {jadwal} pada {waktu.strftime('%H:%M:%S')} WIB")
        
        username = os.getenv('UNBIN_USERNAME')
        password = os.getenv('UNBIN_PASSWORD')
        
        if not username or not password:
            print("Error: Credentials tidak ditemukan!")
            return False
            
        print(f"Login dengan username: {username}")
        
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
            waktu_selesai = get_jakarta_time()
            print(f"Login dan Absen {jadwal} BERHASIL pada {waktu_selesai.strftime('%H:%M:%S')} WIB!")
            return True
        else:
            print(f"Login dan Absen {jadwal} GAGAL!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    login_dan_absen()