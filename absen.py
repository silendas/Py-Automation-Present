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

def get_jakarta_time():
    return datetime.now(pytz.timezone('Asia/Jakarta'))

def is_absen_time(test_mode=False):
    if test_mode:
        return "test_mode"
        
    now = get_jakarta_time()
    hour = now.hour
    minute = now.minute
    
    # Jadwal 1: 09:30 (toleransi 5 menit)
    if hour == 9 and 28 <= minute <= 32:
        return "jadwal_1"
    # Jadwal 2: 13:30 (toleransi 5 menit)
    elif hour == 13 and 28 <= minute <= 32:
        return "jadwal_2"
    else:
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
        if "logout" not in driver.page_source.lower():
            logger.error("Verifikasi Gagal: Tidak menemukan tombol logout")
            return False
            
        # Cek text yang menandakan absen berhasil
        page_source = driver.page_source.lower()
        success_indicators = [
            "berhasil",
            "sudah absen",
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

def login_dan_absen(test_mode=False):
    logger = setup_logging()
    jadwal = is_absen_time(test_mode)
    
    if not jadwal and not test_mode:
        logger.warning("Bukan waktu absen!")
        return False
        
    driver = None
    try:
        waktu = get_jakarta_time()
        logger.info(f"=================== MULAI PROSES ABSEN ===================")
        logger.info(f"Mode: {'TEST' if test_mode else 'NORMAL'}")
        logger.info(f"Memulai proses absen pada {waktu.strftime('%Y-%m-%d %H:%M:%S')} WIB")
        
        username = os.getenv('UNBIN_USERNAME')
        password = os.getenv('UNBIN_PASSWORD')
        
        if not username or not password:
            logger.error("Error: Credentials tidak ditemukan!")
            return False
            
        logger.info(f"Login dengan username: {username}")
        
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Jalankan dalam mode test")
    args = parser.parse_args()
    
    login_dan_absen(test_mode=args.test)