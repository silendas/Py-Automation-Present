# Py-Automation-Present

Script Python untuk otomatisasi absensi online UNBIN menggunakan GitHub Actions.

## Cara Setup

1. Fork repository ini

2. Atur GitHub Secrets
   - Buka Settings > Secrets and variables > Actions
   - Tambahkan secrets berikut:
   ```
   UNBIN_USERNAME_1: username_anda
   UNBIN_PASSWORD_1: password_anda
   ```
   - Untuk multiple akun, tambahkan dengan nomor berikutnya (contoh: UNBIN_USERNAME_2, dst)

## Jadwal Absensi

Program akan berjalan otomatis pada jadwal:
- Jadwal 1: 09:25-09:35 WIB
- Jadwal 2: 12:25-12:35 WIB
- Jadwal 3: 13:25-13:35 WIB

## Fitur

- Otomatis absen sesuai jadwal via GitHub Actions
- Support multiple akun
- Screenshot hasil absensi
- Logging lengkap
- Mode test untuk verifikasi setup

## Catatan
- Pastikan credentials yang dimasukkan benar
- Cek tab Actions untuk melihat status absensi
- Log dan screenshot tersimpan di artifacts setiap run

## Disclaimer
Program ini dibuat untuk tujuan pembelajaran.