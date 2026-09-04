# Car Repair & Automotive Service Management

Modul Odoo 18 untuk mengelola layanan perbaikan mobil (bengkel), mulai dari penerimaan kendaraan, diagnosa, perintah kerja, hingga pembuatan penawaran (quotation) dan invoice.

## Fitur Utama

- **Car Repair Order** — Penerimaan kendaraan dengan data kendaraan (plat nomor, model, nomor rangka, dll) dan checklist kondisi fisik.
- **Car Diagnosis** — Proses diagnosa oleh teknisi, hasil diagnosa, perkiraan jam kerja, dan rekomendasi suku cadang.
- **Work Order** — Perintah kerja dengan alur eksekusi (start, pause, resume, finish) dan pencatatan durasi jam kerja.
- **Quotation & Invoice** — Pembuatan penawaran dari hasil diagnosa dan pembuatan invoice secara otomatis.
- **PDF Reports** — 7 laporan cetak (label, tanda terima, checklist, permintaan diagnosa, hasil diagnosa, perintah kerja, dan invoice).

## Alur Kerja

1. Buat **Car Repair Order** dan isi data kendaraan + checklist.
2. Tugaskan teknisi dan buat **Car Diagnosis**.
3. Teknisi mengisi hasil diagnosa dan rekomendasi suku cadang.
4. Buat **Quotation** dari hasil diagnosa (satu diagnosa = satu quotation).
5. Buat **Work Order** untuk eksekusi perbaikan.
6. Konfirmasi quotation dan buat **Invoice** secara otomatis.

## Laporan (PDF Reports)

| Laporan | Deskripsi |
|---------|-----------|
| Car Label | Label/stiker kendaraan |
| Car Receipt | Tanda terima penyerahan kendaraan |
| Car Checklist | Checklist kondisi fisik kendaraan |
| Car Diagnosis Request | Instruksi kerja diagnosa untuk teknisi |
| Car Diagnosis Result | Hasil pemeriksaan teknisi |
| Car Work Orders | Detail pekerjaan perbaikan |
| Car Invoice | Ringkasan biaya / tagihan |

## Instalasi

1. Salin folder `ian_car_repair` ke direktori `addons` Odoo Anda.
2. Aktifkan mode *Developer* di Odoo.
3. Buka menu **Apps** → **Update Apps List**.
4. Cari **Car Repair & Automotive Service Management** lalu klik **Install**.

## Dependensi

- `base`
- `sale_management`
- `account`
- `fleet`
- `mail`

## Struktur Folder

```
ian_car_repair/
├── __manifest__.py
├── data/          # Data sequence
├── demo/          # Data demo
├── models/        # Model Python
├── report/        # Template & action PDF report
├── security/      # Aturan akses
├── views/         # Tampilan (views) XML
└── wizard/        # Wizard
```
