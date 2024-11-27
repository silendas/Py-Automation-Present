# Py-Automation-Present

Script Python sederhana untuk otomatisasi absensi online.

## Persiapan
- Python 3.7+
- Chrome Browser
- ChromeDriver (sesuai versi Chrome)

## Instalasi
1. Install library yang dibutuhkan:
```
pip install selenium
pip install webdriver_manager
```

2. Atur konfigurasi di `config.json`:
```json
{
    "username": "your_username",
    "password": "your_password",
    "url": "https://url-absensi-anda.com",
    "schedule": {
        "masuk": "07:00",
        "pulang": "16:00"
    }
}
```

3. Jalankan program:
```
python main.py
```

## Catatan
- Pastikan internet stabil
- Program akan berjalan otomatis sesuai jadwal yang diatur
- Gunakan dengan bijak

## Disclaimer
Program ini dibuat untuk tujuan pembelajaran.