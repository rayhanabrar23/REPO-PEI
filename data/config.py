"""
Konfigurasi path file sumber data untuk REPO Funding Simulator.
Semua file diletakkan di folder data/ (bisa diganti ke DB/API nanti).
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_BROKER = os.path.join(DATA_DIR, "Broker__Exchange_Member_.xlsx")
FILE_INSTRUMENT = os.path.join(DATA_DIR, "Instrument.xlsx")
FILE_SAHAM_MARJIN_SBN_BONDS = os.path.join(DATA_DIR, "Data_Saham_Marjin__SBN__Bonds.xlsx")
FILE_LISTED_FREEFLOAT = os.path.join(DATA_DIR, "Listed_Free_Float.xlsx")
FILE_RASIO_SAHAM = os.path.join(DATA_DIR, "Peraturan_Rasio_Saham.xlsx")
FILE_RASIO_BONDS = os.path.join(DATA_DIR, "Peraturan_Rasio_Bonds.xlsx")
FILE_HAIRCUT_KPEI_TXT = os.path.join(DATA_DIR, "Haircut_Agunan_30062026_status.txt")
FILE_STATIS_EFEK_TXT = os.path.join(DATA_DIR, "StatisEfek20260731.txt")

# Batasan internal PEI untuk cap nilai jaminan per saham
CAP_PCT_LISTED_SHARES = 0.05   # 5% dari Listed Shares Value
CAP_PCT_FREE_FLOAT = 0.20      # 20% dari Free Float Value

# yfinance
YF_PERIOD = "3mo"
YF_INTERVAL = "1d"
YF_SUFFIX = ".JK"
