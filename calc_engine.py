"""
Core logic simulasi estimasi pendanaan REPO.

Alur (lihat /areas/repo-funding-simulator.md untuk konteks lengkap):
1. Tentukan Group instrumen (LQ45 / IDX80 non LQ45 / Marjin Lainnya / Non Marjin)
2. Tentukan kategori Haircut KPEI (Low / MedLow / MedHigh / High)
3. Cari Recommended Ratio dari matrix rasio (pakai VaR & Days-to-Sell utk pilih tier)
4. Hitung Nilai Jaminan mentah = jumlah lembar x harga (ambil yang terendah
   antara avg closing 3 bulan vs closing terbaru, sebagai buffer konservatif)
5. Cap Nilai Jaminan ke batas per-saham: MIN(5% x Listed Shares Value, 20% x Free Float Value)
6. Estimasi Pendanaan = Nilai Jaminan (setelah cap) / Recommended Ratio

Catatan: batas maksimum per counterpart (15% x Equity PEI) & cek outstanding
REPO existing SENGAJA di-skip di versi ini (keputusan user).
"""
import config


def tentukan_group(index_membership: str, is_margin: bool) -> str:
    idx = (index_membership or "").upper()
    if "LQ45" in idx:
        return "LQ45"
    if "IDX80" in idx:
        return "IDX80_NON_LQ45"
    if is_margin:
        return "MARJIN_LAINNYA"
    return "NON_MARJIN"


def tentukan_kategori_haircut(haircut_pct: float) -> str:
    """
    Bucketing sesuai batas di Peraturan_Rasio_Saham.xlsx:
    Low <20% | MedLow 20-30% | MedHigh 35-50% | High >50%
    Catatan: ada gap 30-35% yang tidak eksplisit didefinisikan di sumber data;
    di sini gap tsb dimasukkan ke MedLow (<35) sebagai asumsi konservatif ringan.
    Sesuaikan threshold ini kalau ada klarifikasi resmi dari Komite HC.
    """
    if haircut_pct < 20:
        return "Low"
    if haircut_pct < 35:
        return "MedLow"
    if haircut_pct <= 50:
        return "MedHigh"
    return "High"


def pilih_tier(group: str, var_pct: float, days_to_sell: float, thresholds: dict) -> int:
    """
    Pilih tier (0/1/2) matrix rasio berdasarkan VaR & Days-to-Sell,
    dibandingkan terhadap threshold spesifik group tsb.
    """
    th = thresholds[group]
    if var_pct is None or days_to_sell is None:
        return 2  # fallback konservatif: anggap tier risiko tertinggi
    if var_pct < th["var_pct"]:
        return 0 if days_to_sell < th["days"] else 1
    return 2


def cari_recommended_ratio(group, tier, kategori_haircut, rasio_matrix) -> float:
    return rasio_matrix[group][tier][kategori_haircut]


def simulate_stock_funding(
    kode_saham: str,
    jumlah_lot: int,
    market_metrics: dict,
    instrument_row: dict,
    haircut_row: dict,
    listed_ff_row: dict,
    rasio_matrix: dict,
    rasio_thresholds: dict,
) -> dict:
    """
    Fungsi utama: hitung estimasi pendanaan REPO untuk 1 saham.

    Params sudah berupa data yang sudah di-fetch/di-lookup dari caller
    (data_loader + market_data), supaya fungsi ini murni logic & mudah di-test.
    """
    jumlah_lembar = jumlah_lot * 100

    # --- 1. Group & kategori haircut ---
    group = tentukan_group(
        instrument_row.get("index_membership"), instrument_row.get("is_margin")
    )
    haircut_pct = haircut_row.get("haircut_kpei_pct")
    if haircut_pct is None:
        return {"error": f"Haircut KPEI untuk {kode_saham} tidak ditemukan"}
    kategori_haircut = tentukan_kategori_haircut(haircut_pct)

    # --- 2. Recommended ratio ---
    tier = pilih_tier(
        group, market_metrics.get("var_20d_pct"),
        market_metrics.get("days_to_sell_10bio"), rasio_thresholds,
    )
    recommended_ratio = cari_recommended_ratio(group, tier, kategori_haircut, rasio_matrix)

    # --- 3. Nilai Jaminan mentah (harga terendah = buffer konservatif) ---
    harga_terendah = min(
        market_metrics["avg_close_3m"], market_metrics["latest_close"]
    )
    nilai_jaminan_mentah = jumlah_lembar * harga_terendah

    # --- 4. Cap per saham (5% Listed Shares / 20% Free Float) ---
    listed_shares = listed_ff_row.get("listed_shares")
    free_float_shares = listed_ff_row.get("free_float_shares")
    listed_shares_value = listed_shares * harga_terendah if listed_shares else None
    free_float_value = free_float_shares * harga_terendah if free_float_shares else None

    cap_listed = listed_shares_value * config.CAP_PCT_LISTED_SHARES if listed_shares_value else None
    cap_freefloat = free_float_value * config.CAP_PCT_FREE_FLOAT if free_float_value else None
    caps = [c for c in (cap_listed, cap_freefloat) if c is not None]
    max_coll_value = min(caps) if caps else None

    nilai_jaminan_final = (
        min(nilai_jaminan_mentah, max_coll_value) if max_coll_value else nilai_jaminan_mentah
    )
    kena_cap = max_coll_value is not None and nilai_jaminan_mentah > max_coll_value

    # --- 5. Estimasi pendanaan ---
    estimasi_pendanaan = nilai_jaminan_final / recommended_ratio

    return {
        "kode_saham": kode_saham,
        "jumlah_lot": jumlah_lot,
        "jumlah_lembar": jumlah_lembar,
        "group": group,
        "kategori_haircut": kategori_haircut,
        "haircut_kpei_pct": haircut_pct,
        "harga_dipakai": harga_terendah,
        "avg_close_3m": market_metrics["avg_close_3m"],
        "latest_close": market_metrics["latest_close"],
        "var_20d_pct": market_metrics.get("var_20d_pct"),
        "days_to_sell_10bio": market_metrics.get("days_to_sell_10bio"),
        "recommended_ratio": recommended_ratio,
        "nilai_jaminan_mentah": nilai_jaminan_mentah,
        "max_coll_value_cap": max_coll_value,
        "kena_cap": kena_cap,
        "nilai_jaminan_final": nilai_jaminan_final,
        "estimasi_pendanaan": estimasi_pendanaan,
    }


# ---------------------------------------------------------------------------
# OBLIGASI
# ---------------------------------------------------------------------------
# Asumsi nominal per unit obligasi di IDX (standar umum). Sesuaikan kalau
# ada data resmi yang berbeda untuk seri tertentu.
NOMINAL_PER_UNIT_OBLIGASI = 1_000_000  # Rp 1 juta / unit

# Rasio korporasi berdasarkan Peraturan_Rasio_Bonds.xlsx: range 105%-120%
# (Sedang) dan >120% (Tinggi). Karena data rating per seri belum tersedia
# (lihat /areas/repo-funding-simulator.md poin 4b - di-skip), dipakai nilai
# representatif dari batas bawah tiap kategori sebagai default konservatif.
RASIO_OBLIGASI_KORPORASI = {
    "Sedang": 1.05,   # batas bawah range 105%-120%
    "Tinggi": 1.20,   # batas bawah range >120%
}
RASIO_OBLIGASI_PEMERINTAH = 1.0


def simulate_bond_funding(
    kode_obligasi: str,
    jumlah_unit: int,
    bond_row: dict,
    kategori_risiko_korporasi: str = "Sedang",
) -> dict:
    """
    Estimasi pendanaan REPO untuk obligasi (pemerintah atau korporasi).

    bond_row: 1 baris dari data_loader.load_statis_efek() untuk kode_obligasi ybs.
    kategori_risiko_korporasi: "Sedang" atau "Tinggi" — HANYA dipakai kalau
      obligasi ini korporasi. Karena rating per seri belum ada di sumber data,
      user memilih manual (default "Sedang" = asumsi paling umum).

    Catatan: closing_price_pct di sumber data StatisEfek dinyatakan sebagai
    fraksi terhadap par (1.0 = 100% dari nominal), BUKAN dalam ribuan/rupiah.
    """
    tipe = (bond_row.get("tipe_instrumen") or "").upper()
    closing_pct = bond_row.get("closing_price_pct")
    if closing_pct is None:
        return {"error": f"Closing price untuk {kode_obligasi} tidak ditemukan"}

    is_pemerintah = tipe in ("GOVERNMENT BOND", "SBSN", "SUKUK", "SPN")

    if is_pemerintah:
        jenis_obligasi = "Pemerintah"
        rasio = RASIO_OBLIGASI_PEMERINTAH
        kategori_risiko = "Rendah"
    else:
        jenis_obligasi = "Korporasi"
        if kategori_risiko_korporasi not in RASIO_OBLIGASI_KORPORASI:
            kategori_risiko_korporasi = "Sedang"
        rasio = RASIO_OBLIGASI_KORPORASI[kategori_risiko_korporasi]
        kategori_risiko = kategori_risiko_korporasi

    # Nilai Jaminan = jumlah unit x nominal per unit x closing price (fraksi par)
    nilai_jaminan = jumlah_unit * NOMINAL_PER_UNIT_OBLIGASI * closing_pct

    # Estimasi Pendanaan = Nilai Jaminan / Rasio
    estimasi_pendanaan = nilai_jaminan / rasio

    return {
        "kode_obligasi": kode_obligasi,
        "nama_obligasi": bond_row.get("nama_efek"),
        "tipe_instrumen": tipe,
        "jenis_obligasi": jenis_obligasi,
        "kategori_risiko": kategori_risiko,
        "jumlah_unit": jumlah_unit,
        "nominal_per_unit": NOMINAL_PER_UNIT_OBLIGASI,
        "closing_price_pct": closing_pct,
        "rasio": rasio,
        "nilai_jaminan": nilai_jaminan,
        "estimasi_pendanaan": estimasi_pendanaan,
        "maturity_date": bond_row.get("maturity_date"),
        "kupon_pct": bond_row.get("kupon_pct"),
    }
