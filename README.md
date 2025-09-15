# Scraping Lokasi Indonesia

Proyek ini adalah tool scraping lokasi wilayah di Indonesia (provinsi, kabupaten/kota, kecamatan, kelurahan/desa) dari website [nomor.net](https://m.nomor.net/_kodepos.php?_i=kode-wilayah) menggunakan **Python**, **Selenium**, dan **BeautifulSoup**. Tool ini memiliki antarmuka CLI interaktif di terminal dan hasil scraping dapat diekspor ke file **JSON**.

## Fitur

- Scraping data lokasi (provinsi, kabupaten/kota, kecamatan, kelurahan/desa) dari https://m.nomor.net/_kodepos.php?_i=kode-wilayah
- Menggunakan Selenium untuk navigasi dinamis & BeautifulSoup untuk parsing HTML
- CLI interaktif di terminal (memilih provinsi, kabupaten, dsb)
- Ekspor hasil scraping ke **file JSON**

## Instalasi

1. **Klon repositori ini:**
   ```bash
   git clone https://github.com/nurkhaliqfm/Sraping-Lokasi-Indonesia.git
   cd Sraping-Lokasi-Indonesia
   ```

2. **(Opsional) Buat virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Jika belum ada, buat file `requirements.txt`:
   ```
   selenium
   beautifulsoup4
   tabulate
   tqdm
   ```

4. **Siapkan Web Driver:**
   - Download [ChromeDriver](https://sites.google.com/chromium.org/driver/) sesuai versi Chrome.
   - Letakkan file chromedriver pada PATH/di folder proyek.

## Cara Penggunaan

Jalankan skrip utama:

```bash
python main.py
```

Ikuti instruksi di terminal, misal:
```
Selamat datang di Scraping Lokasi Indonesia!
Pilih level scraping:
1. Provinsi
2. Kabupaten/Kota
3. Kecamatan
4. Kelurahan/Desa
> 2
Masukkan nama/ID provinsi:
> Jawa Barat
...
Simpan hasil ke file JSON (cth: hasil.json)? [y/n]
> y
Nama file:
> lokasi_jabar.json
```

## Contoh Kode Utama

```python
from selenium import webdriver
from bs4 import BeautifulSoup
import json

driver = webdriver.Chrome()
driver.get('https://m.nomor.net/_kodepos.php?_i=kode-wilayah')

soup = BeautifulSoup(driver.page_source, 'html.parser')
# Lakukan parsing data sesuai kebutuhan

driver.quit()

# Simpan hasil ke file json
with open('lokasi.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## Ekspor Data ke JSON

Setelah selesai, data wilayah akan diekspor ke file JSON yang bisa digunakan untuk analisis atau aplikasi lain.

## Kontribusi

Pull request dan saran sangat diterima! Fork repo ini dan ajukan PR jika ingin menambah fitur atau memperbaiki bug.

## Lisensi

MIT License.

---

**Catatan:**  
Scraping hanya untuk tujuan edukasi. Pastikan mengikuti syarat & ketentuan dari sumber data.
