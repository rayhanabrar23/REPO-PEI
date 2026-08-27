"""
Load semua sumber data statis (Excel/txt) menjadi pandas DataFrame yang siap
dipakai oleh calc_engine.py.

Setiap fungsi punya tanggung jawab tunggal: baca 1 file sumber -> DataFrame
dengan kolom yang sudah dinormalisasi (nama kolom konsisten & tipe data bersih).
"""
import pandas as pd
import config


# ---------------------------------------------------------------------------
# 1. Broker / Exchange Member
# ---------------------------------------------------------------------------
def load_broker() -> pd.DataFrame:
    df = pd.read_excel(config.FILE_BROKER, sheet_name="Broker (Exchange Member)")
    df = df.rename(columns={
        "Broker Code": "broker_code",
        "Broker Name": "broker_name",
        "Opers Status": "opers_status",
        "Clearing Status": "clearing_status",
    })
    df["broker_name"] = df["broker_name"].astype(str).str.strip()
    return df[["broker_code", "broker_name", "opers_status", "clearing_status"]]


# ---------------------------------------------------------------------------
# 2. Instrument master (harga terakhir, haircut, index, status margin)
# ---------------------------------------------------------------------------
def load_instrument() -> pd.DataFrame:
    # Baris 1 di file adalah label grup gabungan (Margin / Reverse Repo),
    # header kolom sebenarnya ada di baris ke-2 -> header=1
    df = pd.read_excel(config.FILE_INSTRUMENT, sheet_name="Instrument", header=1)
    df = df.rename(columns={
        "Instrument Code": "kode_efek",
        "Type": "tipe_instrumen",
        "Margin": "is_margin",
        "Status": "status",
        "Index": "index_membership",
        "Instrument Name": "nama_instrumen",
        "Last Close Price": "last_close_price",
        "Last Price Date": "last_price_date",
        "Haircut KPEI": "haircut_kpei_instrument",
        "Sector": "sector",
        "Max Loan Value": "max_loan_value",
        "Available Loan Value": "available_loan_value",
    })
    keep = [
        "kode_efek", "tipe_instrumen", "is_margin", "status", "index_membership",
        "nama_instrumen", "last_close_price", "last_price_date", "sector",
        "max_loan_value", "available_loan_value",
    ]
    df = df[keep].copy()
    # Instrument.xlsx pakai suffix ".IDX" (mis. "BDMN.IDX") -> dinormalisasi
    # ke kode polos ("BDMN") supaya bisa di-join ke file lain yang tidak pakai suffix
    df["kode_efek"] = df["kode_efek"].astype(str).str.strip().str.replace(".IDX", "", regex=False)
    df["is_margin"] = df["is_margin"].astype(str).str.upper().eq("TRUE")
    return df


# ---------------------------------------------------------------------------
# 3. Haircut KPEI resmi (sumber of truth, sesuai keputusan: pakai file txt)
# ---------------------------------------------------------------------------
def load_haircut_kpei() -> pd.DataFrame:
    df = pd.read_csv(config.FILE_HAIRCUT_KPEI_TXT, sep="|", dtype=str)
    df = df.rename(columns={
        "Tanggal": "tanggal",
        "KODE EFEK": "kode_efek",
        "Nama Saham": "nama_saham",
        "Haircut": "haircut_kpei_pct",
        "Status": "update_status",
    })
    df["kode_efek"] = df["kode_efek"].astype(str).str.strip()
    df["haircut_kpei_pct"] = pd.to_numeric(df["haircut_kpei_pct"], errors="coerce")
    # Kalau ada duplikat tanggal, ambil yang paling baru per kode efek
    df = df.sort_values("tanggal").drop_duplicates("kode_efek", keep="last")
    return df[["kode_efek", "nama_saham", "haircut_kpei_pct", "update_status"]]


# ---------------------------------------------------------------------------
# 4. Daftar saham marjin / SBN / obligasi korporasi yang bisa dijaminkan
# ---------------------------------------------------------------------------
def load_daftar_jaminan() -> dict:
    saham_marjin = pd.read_excel(
        config.FILE_SAHAM_MARJIN_SBN_BONDS, sheet_name="Saham Marjin"
    ).rename(columns={"Kode": "kode_efek", "Nama": "nama_efek"})

    sbn = pd.read_excel(
        config.FILE_SAHAM_MARJIN_SBN_BONDS, sheet_name="SBN"
    ).rename(columns={"Kode": "kode_efek", "Nama Seri": "nama_efek"})

    obligasi_korporasi = pd.read_excel(
        config.FILE_SAHAM_MARJIN_SBN_BONDS, sheet_name="Sheet3"
    ).rename(columns={"Kode Seri": "kode_efek", "Nama Seri": "nama_efek"})

    for d in (saham_marjin, sbn, obligasi_korporasi):
        d["kode_efek"] = d["kode_efek"].astype(str).str.strip()

    return {
        "saham_marjin": saham_marjin[["kode_efek", "nama_efek"]],
        "sbn": sbn[["kode_efek", "nama_efek"]],
        "obligasi_korporasi": obligasi_korporasi[["kode_efek", "nama_efek"]],
    }


# ---------------------------------------------------------------------------
# 5. Listed shares & free float
# ---------------------------------------------------------------------------
def load_listed_freefloat() -> pd.DataFrame:
    df = pd.read_excel(config.FILE_LISTED_FREEFLOAT, sheet_name="Listed and Free Float")
    df = df.rename(columns={
        "Kode Emiten": "kode_efek",
        "Total_Listed_Shares": "listed_shares",
        "Free_Float_Shares": "free_float_shares",
    })
    df = df[["kode_efek", "listed_shares", "free_float_shares"]].dropna(subset=["kode_efek"])
    df["kode_efek"] = df["kode_efek"].astype(str).str.strip()
    return df


# ---------------------------------------------------------------------------
# 6. Peraturan rasio saham (matrix Group x VaR/Days x Haircut kategori)
# ---------------------------------------------------------------------------
def load_rasio_saham_matrix() -> dict:
    """
    Hasil parsing manual dari Peraturan_Rasio_Saham.xlsx menjadi struktur
    lookup: {group: {tier_index: {haircut_category: ratio}}}

    tier_index 0 = VaR rendah & days rendah
    tier_index 1 = VaR rendah & days tinggi
    tier_index 2 = VaR tinggi (days diabaikan)

    Threshold VaR & Days per group disimpan terpisah di RASIO_SAHAM_THRESHOLDS.
    """
    return {
        "LQ45": [
            {"Low": 1.5, "MedLow": 1.55, "MedHigh": 1.65, "High": 1.75},
            {"Low": 1.55, "MedLow": 1.6, "MedHigh": 1.7, "High": 1.75},
            {"Low": 1.6, "MedLow": 1.65, "MedHigh": 1.75, "High": 1.75},
        ],
        "IDX80_NON_LQ45": [
            {"Low": 1.75, "MedLow": 1.8, "MedHigh": 1.9, "High": 2.0},
            {"Low": 1.8, "MedLow": 1.85, "MedHigh": 1.95, "High": 2.0},
            {"Low": 1.85, "MedLow": 1.9, "MedHigh": 2.0, "High": 2.0},
        ],
        "MARJIN_LAINNYA": [
            {"Low": 2.0, "MedLow": 2.05, "MedHigh": 2.15, "High": 2.25},
            {"Low": 2.05, "MedLow": 2.1, "MedHigh": 2.2, "High": 2.25},
            {"Low": 2.1, "MedLow": 2.15, "MedHigh": 2.25, "High": 2.25},
        ],
        "NON_MARJIN": [
            {"Low": 2.25, "MedLow": 2.3, "MedHigh": 2.4, "High": 2.5},
            {"Low": 2.3, "MedLow": 2.35, "MedHigh": 2.45, "High": 2.5},
            {"Low": 2.35, "MedLow": 2.4, "MedHigh": 2.5, "High": 2.5},
        ],
    }


# Threshold VaR(%) & Days-to-Sell per group, dipakai untuk pilih tier di atas
RASIO_SAHAM_THRESHOLDS = {
    "LQ45": {"var_pct": 25, "days": 0.5},
    "IDX80_NON_LQ45": {"var_pct": 35, "days": 1},
    "MARJIN_LAINNYA": {"var_pct": 50, "days": 5},
    "NON_MARJIN": {"var_pct": 50, "days": 10},
}


def load_rasio_bonds() -> pd.DataFrame:
    df = pd.read_excel(config.FILE_RASIO_BONDS, sheet_name="Sheet1")
    df = df.rename(columns={
        "Jenis\nObligasi": "jenis_obligasi",
        "Rasio": "rasio",
        "Kategori Risiko": "kategori_risiko",
    })
    return df


# ---------------------------------------------------------------------------
# 7. Data dasar obligasi (StatisEfek) — maturity, kupon, closing price, dll
# ---------------------------------------------------------------------------
def load_statis_efek() -> pd.DataFrame:
    df = pd.read_csv(config.FILE_STATIS_EFEK_TXT, sep="|", dtype=str, encoding="utf-8")
    df = df.rename(columns={
        "Code": "kode_efek",
        "Description": "nama_efek",
        "Type": "tipe_instrumen",
        "Issuer": "penerbit",
        "Status": "status",
        "Maturity Date": "maturity_date",
        "Interest": "kupon_pct",
        "Interest Type": "tipe_kupon",
        "Interest Freq": "frekuensi_kupon",
        "Current Amt": "outstanding_amt",
        "Closing Price": "closing_price_pct",
    })
    df["kode_efek"] = df["kode_efek"].astype(str).str.strip()
    df["kupon_pct"] = pd.to_numeric(df["kupon_pct"], errors="coerce")
    df["outstanding_amt"] = pd.to_numeric(df["outstanding_amt"], errors="coerce")
    df["closing_price_pct"] = pd.to_numeric(df["closing_price_pct"], errors="coerce")
    return df[[
        "kode_efek", "nama_efek", "tipe_instrumen", "penerbit", "status",
        "maturity_date", "kupon_pct", "tipe_kupon", "frekuensi_kupon",
        "outstanding_amt", "closing_price_pct",
    ]]


# ---------------------------------------------------------------------------
# Loader gabungan (dipanggil sekali di awal app, di-cache oleh Streamlit)
# ---------------------------------------------------------------------------
def load_all() -> dict:
    return {
        "broker": load_broker(),
        "instrument": load_instrument(),
        "haircut_kpei": load_haircut_kpei(),
        "daftar_jaminan": load_daftar_jaminan(),
        "listed_freefloat": load_listed_freefloat(),
        "rasio_saham_matrix": load_rasio_saham_matrix(),
        "rasio_saham_thresholds": RASIO_SAHAM_THRESHOLDS,
        "rasio_bonds": load_rasio_bonds(),
        "statis_efek": load_statis_efek(),
    }
