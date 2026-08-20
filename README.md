# Portal Pendanaan Transaksi REPO — PT Pendanaan Efek Indonesia (PEI)

Portal untuk calon nasabah: simulasi awal pendanaan REPO + form pengajuan yang
otomatis mengirim notifikasi email.

## Struktur folder

repo-portal/
├── app.py # Aplikasi utama Streamlit
├── requirements.txt
├── README.md
├── .streamlit/
│ ├── config.toml # Tema warna (maroon/putih/abu)
│ └── secrets.toml.example # Template kredensial email (JANGAN commit versi aslinya)
└── assets/
├── logo.png # (belum ada) — taruh logo PEI di sini
└── documents/ # (belum ada) — taruh PDF dokumen pendukung di sini


## Yang masih perlu ditambahkan

1. **Logo PEI** → simpan sebagai `assets/logo.png`. Jika file belum ada, halaman
   otomatis menampilkan logo teks "PEI" sebagai fallback (tidak akan error).
2. **Dokumen pendukung (PDF)** → taruh semua file `.pdf` di `assets/documents/`.
   Tombol unduh akan muncul otomatis untuk setiap file yang ada di folder tsb.
3. **Engine perhitungan simulator** → saat ini simulator memakai haircut dummy
   (50% saham / 30% obligasi) hanya untuk keperluan tampilan. Formula resmi
   menyusul.

## Setup pengiriman email

Form pengajuan mengirim email ke `rayhanabrar023@gmail.com` via Gmail SMTP.

1. Aktifkan **2-Step Verification** di akun Gmail yang akan dipakai untuk mengirim.
2. Buat **App Password** di https://myaccount.google.com/apppasswords
3. Isi kredensial:
   - **Lokal**: salin `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml`, isi `EMAIL_SENDER` dan `EMAIL_PASSWORD`.
   - **Streamlit Community Cloud**: buka app → *Settings → Secrets*, isi dengan format yang sama (jangan upload file secrets.toml ke GitHub).

## Menjalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ke Streamlit Community Cloud

1. Push seluruh folder ini ke repo GitHub baru (mis. `pei-repo-portal`).
2. Buka https://share.streamlit.io → **New app** → pilih repo & branch, `app.py` sebagai entry point.
3. Sebelum deploy pertama (atau setelah), isi **Secrets** sesuai langkah di atas.
4. Deploy.

## Catatan keamanan

- `secrets.toml` (versi asli, berisi password) sudah otomatis diabaikan bila
  Anda menambahkan `.gitignore` berikut sebelum push pertama:

.streamlit/secrets.toml
