# Analisis Histogram dan Enhancement Citra Ijazah

Tugas Pengolahan Citra Digital. Program membaca 9 citra ijazah, mengubahnya ke grayscale
(Y = 0.299R + 0.587G + 0.114B), menampilkan histogram, mendiagnosis masalah tiap citra,
memilih metode enhancement yang sesuai, lalu menampilkan histogram hasil.

## Struktur
```
src/extract_images.py   # ekstrak 9 citra dari IJAZAH_PCD.pdf -> data/ijazah-1.png ... ijazah-9.png
src/enhance.py          # program utama (diagnosis, enhancement, histogram)
data/                   # citra ijazah-1 ... ijazah-9
results/                # hasil: ijazah-N_enhanced.png, hasil_histogram_ijazah-N.png,
                        #        semua_metode_ijazah-N.png, summary.csv
ANALISIS.md             # analisis teoritis histogram
requirements.txt
```

## Cara menjalankan
```bash
git clone <URL-REPO-ANDA>
cd <nama-repo>
python -m venv venv
venv\Scripts\activate            # Windows PowerShell. Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# 1) siapkan citra: pilih salah satu
python src/extract_images.py IJAZAH_PCD.pdf     # (a) ekstrak dari PDF
#    atau (b) taruh file asli bernama ijazah-1.jpg ... ijazah-9.jpg di folder data/

# 2) jalankan enhancement
python src/enhance.py                  # hasil utama
python src/enhance.py --all_methods    # + perbandingan 7 metode untuk tiap citra
```
Citra pada `data/` boleh `.png` atau `.jpg`, asalkan namanya `ijazah-<nomor>`.

## Cara kerja pemilihan metode
Fitur dihitung dari grayscale (noise diukur pada lebar 800 px karena ukuran asli tiap citra berbeda):

| Kondisi terdeteksi | Aturan | Metode |
|---|---|---|
| Terlalu gelap & kontras rendah | median intensitas < 200 | Gamma (γ=0,7) + contrast stretching |
| Noise | rata-rata selisih terhadap median filter > 2,1 | Median filter 3x3 |
| Kontras rendah | persentil-1 > 140 dan std < 20 | Contrast stretching (persentil 1-99) |
| Pencahayaan tidak merata | std median blok latar > 6 | CLAHE |
| Terlalu terang | median > 250 | Gamma (γ=1,5) |
| Normal / baik | selain di atas | Unsharp masking |

Metode lain (histogram equalization, Otsu) tersedia di `enhance.py` dan ikut dibandingkan lewat `--all_methods`.

## Hasil (`results/summary.csv`)
| Citra | Masalah terdeteksi | Metode | Std asli → hasil |
|---|---|---|---|
| ijazah-1 | Normal / baik | Unsharp masking | 31,8 → 42,3 |
| ijazah-2 | Kontras rendah | Contrast stretching | 17,4 → 42,1 |
| ijazah-3 | Normal / baik | Unsharp masking | 27,7 → 34,4 |
| ijazah-4 | Noise | Median filter | 28,7 → 23,3 |
| ijazah-5 | Normal / baik | Unsharp masking | 28,7 → 38,6 |
| ijazah-6 | Gelap & kontras rendah | Gamma + contrast stretching | 13,6 → 40,5 |
| ijazah-7 | Normal / baik | Unsharp masking | 28,4 → 38,8 |
| ijazah-8 | Normal / baik | Unsharp masking | 29,4 → 39,7 |
| ijazah-9 | Gelap & kontras rendah | Gamma + contrast stretching | 19,5 → 40,1 |

## Catatan penting
- **Urutan citra.** `ijazah-1` sampai `ijazah-9` di sini mengikuti urutan halaman `IJAZAH_PCD.pdf`. Jika urutan di laporan Anda berbeda, ganti nama file di `data/` agar sesuai.
- **Tidak semua kategori laporan terdeteksi.** Tabel laporan memuat 9 kategori (termasuk overexposed, uneven illumination, HE, Otsu untuk OCR). Pada 9 citra ini aturan otomatis hanya menemukan 4 kondisi. Jika dosen mengharuskan satu metode per baris tabel laporan, gunakan `--all_methods` dan pilih hasil yang sesuai, atau ubah fungsi `diagnose()`.
- Ambang aturan dipilih dari 9 citra ini saja, jadi perlu disesuaikan untuk citra lain.
- Ijazah memuat data pribadi: gunakan repositori **private**, atau tambahkan `data/` ke `.gitignore`.
