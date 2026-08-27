"""
Fetch data harga saham historis via yfinance, lalu hitung metrik turunan
yang dibutuhkan calc_engine.py:
- avg_close_3m   : rata-rata closing price 3 bulan terakhir
- latest_close   : closing price terbaru
- avg_daily_trade_value : rata-rata nilai transaksi harian (Rp)
- var_20d_pct    : Historical Simulation VaR 20 hari (%), horizon 1 hari
- days_to_sell_10bio : estimasi hari untuk menjual Rp10 Miliar saham ybs

Catatan: yfinance tidak menyediakan data untuk obligasi Indonesia, jadi
modul ini hanya dipakai untuk instrumen saham (EQUITY).
"""
import numpy as np
import yfinance as yf
import config


def fetch_stock_metrics(kode_saham: str) -> dict:
    """
    Ambil & hitung metrik harga untuk 1 kode saham.
    Return dict, atau dict berisi 'error' kalau data tidak tersedia.
    """
    ticker = f"{kode_saham.upper()}{config.YF_SUFFIX}"
    try:
        data = yf.download(
            ticker, period=config.YF_PERIOD, interval=config.YF_INTERVAL,
            progress=False, auto_adjust=False,
        )
    except Exception as e:
        return {"error": f"Gagal fetch data {ticker}: {e}"}

    if data is None or data.empty:
        return {"error": f"Data harga untuk {ticker} tidak ditemukan di Yahoo Finance"}

    # yfinance kadang mengembalikan MultiIndex kolom (Price, Ticker)
    if isinstance(data.columns, __import__("pandas").MultiIndex):
        data.columns = data.columns.get_level_values(0)

    close = data["Close"].dropna()
    volume = data["Volume"].dropna()

    if len(close) < 5:
        return {"error": f"Data harga {ticker} terlalu sedikit ({len(close)} hari) untuk dihitung"}

    avg_close_3m = float(close.mean())
    latest_close = float(close.iloc[-1])

    trading_value = (close * volume).dropna()
    avg_daily_trade_value = float(trading_value.mean())

    # Historical Simulation VaR 20 hari (95%), berbasis return harian
    returns = close.pct_change().dropna()
    var_20d_pct = _calc_hsvar_20d(returns)

    # Days to sell Rp10 Miliar = 10 Miliar / rata-rata nilai transaksi harian
    days_to_sell_10bio = (
        10_000_000_000 / avg_daily_trade_value if avg_daily_trade_value > 0 else None
    )

    return {
        "kode_saham": kode_saham.upper(),
        "avg_close_3m": avg_close_3m,
        "latest_close": latest_close,
        "avg_daily_trade_value": avg_daily_trade_value,
        "var_20d_pct": var_20d_pct,
        "days_to_sell_10bio": days_to_sell_10bio,
        "n_days_data": len(close),
    }


def _calc_hsvar_20d(daily_returns) -> float:
    """
    Historical Simulation VaR: ambil percentile ke-5 (95% confidence) dari
    return harian, lalu scaling ke horizon 20 hari pakai aturan akar-waktu
    (sqrt(20)). Hasil dalam persen absolut (positif = potensi rugi).
    """
    if len(daily_returns) < 5:
        return None
    var_1d = np.percentile(daily_returns, 5)  # biasanya negatif
    var_20d = abs(var_1d) * np.sqrt(20)
    return float(var_20d * 100)  # dalam %
