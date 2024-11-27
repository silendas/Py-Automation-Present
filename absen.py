from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
from datetime import datetime
import pytz
import logging
import argparse
import json

def get_jakarta_time():
    return datetime.now(pytz.timezone('Asia/Jakarta'))

def is_absen_time(test_mode=False):
    now = get_jakarta_time()
    logger = setup_logging()
    logger.info(f"Checking time: {now.strftime('%Y-%m-%d %H:%M:%S')} WIB")
    
    if test_mode:
        logger.info("Running in TEST mode")
        return "test_mode"
        
    hour = now.hour
    minute = now.minute
    
    logger.info(f"Current hour: {hour}, minute: {minute}")
    
    # Jadwal 1: 09:30-10:00
    if hour == 9 and minute >= 30 or hour == 10 and minute == 0:
        logger.info("Matched Jadwal 1 (09:30-10:00)")
        return "jadwal_1"
    # Jadwal 2: 12:30-13:00
    elif hour == 12 and minute >= 30 or hour == 13 and minute == 0:
        logger.info("Matched Jadwal 2 (12:30-13:00)")
        return "jadwal_2"
    # Jadwal 3: 13:30-14:00
    elif hour == 13 and minute >= 30 or hour == 14 and minute == 0:
        logger.info("Matched Jadwal 3 (13:30-14:00)")
        return "jadwal_3"
    else:
        logger.info("No schedule matched")
        return None

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

# Setup logging
def setup_logging():
    # Buat folder absen/log jika belum ada
    log_dir = os.path.join('absen', 'log')
    os.makedirs(log_dir, exist_ok=True)
    
    # Format nama file log dengan tanggal
    log_filename = os.path.join(log_dir, f"absensi_{get_jakarta_time().strftime('%Y-%m-%d')}.log")
    
    # Konfigurasi logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def verify_absen_success(driver, logger):
    try:
        # Cek halaman setelah login
        page_source = driver.page_source.lower()
        
        # Cek jika sudah absen hari ini
        already_absen_indicators = [
            "anda sudah melakukan absensi",
            "sudah absen",
            "absensi berhasil"
        ]
        
        for indicator in already_absen_indicators:
            if indicator in page_source:
                logger.info(f"Sudah absen hari ini (terdeteksi: '{indicator}')")
                return True
        
        # Jika belum absen, cek proses absen berhasil
        success_indicators = [
            "berhasil",
            "logout"
        ]
        
        found_indicators = [ind for ind in success_indicators if ind in page_source]
        if found_indicators:
            logger.info(f"Indikator sukses ditemukan: {', '.join(found_indicators)}")
            
            # Ambil screenshot sebagai bukti
            screenshot_dir = os.path.join('absen', 'log', 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = get_jakarta_time().strftime('%Y-%m-%d_%H-%M-%S')
            screenshot_path = os.path.join(screenshot_dir, f'absen_{timestamp}.png')
            driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot disimpan: {screenshot_path}")
            
            return True
        else:
            logger.error("Verifikasi Gagal: Tidak menemukan indikator keberhasilan")
            return False
            
    except Exception as e:
        logger.error(f"Error saat verifikasi: {str(e)}")
        return False

def login_dan_absen(test_mode=False, username=None, password=None):
    logger = setup_logging()
    jadwal = is_absen_time(test_mode)
    if not jadwal and not test_mode:
        logger.warning("Bukan waktu absen!")
        return False
        
    driver = None
    try:
        waktu = get_jakarta_time()
        logger.info(f"=================== MULAI PROSES ABSEN ===================")
        logger.info(f"Memulai proses absen untuk user: {username}")
        logger.info(f"Waktu: {waktu.strftime('%Y-%m-%d %H:%M:%S')} WIB")
        
        if not username or not password:
            logger.error("Error: Credentials tidak ditemukan!")
            return False
            
        driver = setup_driver()
        logger.info("Browser Chrome berhasil diinisialisasi")
        
        logger.info("Mengakses halaman absensi...")
        driver.get("https://akademik.unbin.ac.id/absensi/")
        
        logger.info("Menunggu element username muncul...")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "userid"))
        )
        password_field = driver.find_element(By.NAME, "pin")
        
        logger.info("Mengisi credentials...")
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        logger.info("Mencoba login...")
        driver.find_element(By.NAME, "login").click()
        
        logger.info("Menunggu proses login...")
        time.sleep(5)
        
        # Verifikasi keberhasilan
        if verify_absen_success(driver, logger):
            waktu_selesai = get_jakarta_time()
            logger.info(f"Login dan Absen {jadwal} BERHASIL pada {waktu_selesai.strftime('%H:%M:%S')} WIB!")
            logger.info("=================== PROSES SELESAI ===================\n")
            return True
        else:
            logger.error(f"Login dan Absen {jadwal} GAGAL!")
            logger.error("=================== PROSES GAGAL ===================\n")
            return False
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error("=================== PROSES ERROR ===================\n")
        return False
    finally:
        if driver:
            driver.quit()
            logger.info("Browser ditutup")

def process_all_accounts(test_mode=False):
    logger = setup_logging()
    results = []
    
    # Ambil credentials dari environment variables untuk backward compatibility
    env_username = os.getenv('UNBIN_USERNAME')
    env_password = os.getenv('UNBIN_PASSWORD')
    
    if env_username and env_password:
        logger.info("Processing account from environment variables")
        success = login_dan_absen(test_mode, env_username, env_password)
        results.append({"username": env_username, "success": success})
    
    # Proses accounts dari JSON
    accounts_file = os.path.join('config', 'accounts.json')
    if os.path.exists(accounts_file):
        try:
            with open(accounts_file) as f:
                accounts = json.load(f)
                
            for account in accounts.get('accounts', []):
                username = account.get('username')
                password = account.get('password')
                
                if username and password:
                    logger.info(f"Processing account: {username}")
                    success = login_dan_absen(test_mode, username, password)
                    results.append({"username": username, "success": success})
                    
        except Exception as e:
            logger.error(f"Error reading accounts file: {str(e)}")
    
    # Log summary
    logger.info("\n=== SUMMARY ===")
    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        logger.info(f"Account {result['username']}: {status}")
    
    return all(r["success"] for r in results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Jalankan dalam mode test")
    args = parser.parse_args()
    
    process_all_accounts(test_mode=args.test)