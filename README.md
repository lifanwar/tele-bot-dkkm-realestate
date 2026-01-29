# DKKM Telegram Bot – Ringkasan

## Fungsi
Bot Telegram untuk:
- Cari gedung terdekat dari lokasi user.
- Lihat detail gedung + daftar unit.
- Lihat detail unit + status (available/blacklist).
- Navigasi: back ke gedung, back ke hasil, pencarian baru.

## Alur Singkat
1. User kirim lokasi → bot simpan `lat/long` → tampil pilihan radius.
2. User pilih radius → bot panggil API `Radius` → tampil daftar gedung + tombol.
3. User pilih gedung → API `Gedung` → detail gedung + daftar unit + tombol unit.
4. User pilih unit → API `Unit` → detail unit + tombol:
   - `Back` (ke gedung),
   - `Back to Awal` (ke hasil gedung),
   - `Pencarian Baru`.

## Struktur File (inti)
- `config.py` → token, API base URL, API key, daftar radius.
- `main.py` → start bot + `callback_router`.
- `flows/handle_location.py` → terima lokasi + search nearby.
- `flows/get_gedung.py` → detail gedung + back ke hasil.
- `flows/get_detail_unit.py` → detail unit + back ke gedung/awal.

## Callback Pattern
- `radius_{angka}` → cari gedung terdekat.
- `gedung_{uuid}` → detail gedung.
- `unit_{uuid}` → detail unit.
- `back_results` → kembali ke daftar gedung.
- `back_gedung` → kembali ke detail gedung.
- `search_again` → pilih radius baru.

## Konfigurasi (.env)
- `TELEGRAM_TOKEN`
- `API_BASE_URL`
- `API_KEY`