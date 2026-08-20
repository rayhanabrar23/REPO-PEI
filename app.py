import streamlit as st
from pathlib import Path
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Pendanaan Transaksi REPO — PT Pendanaan Efek Indonesia",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ASSETS_DIR = Path(__file__).parent / "assets"
DOCS_DIR = ASSETS_DIR / "documents"
LOGO_PATH = ASSETS_DIR / "logo.png"

RECIPIENT_EMAIL = "rayhanabrar023@gmail.com"

# ============================================================
# STYLE — Maroon / White / Gray, Roboto Condensed
# ============================================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300;400;500;600;700&display=swap');

:root {
    --maroon: #7A1E28;
    --maroon-dark: #5C1620;
    --maroon-light: #9B3542;
    --gray: #6C6F73;
    --gray-light: #F4F3F2;
    --gray-mid: #E3E1DF;
    --white: #FFFFFF;
}

html, body, [class*="css"], .stMarkdown, .stTextInput, .stSelectbox, .stNumberInput {
    font-family: 'Roboto Condensed', sans-serif !important;
}

.stApp {
    background-color: var(--gray-light);
}

/* ---------- Header ---------- */
.pei-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0 1.25rem 0;
    border-bottom: 3px solid var(--maroon);
    margin-bottom: 1.5rem;
}
.pei-header-title {
    color: var(--maroon-dark);
    font-weight: 700;
    font-size: 1.35rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.pei-header-sub {
    color: var(--gray);
    font-size: 0.95rem;
    margin-top: -4px;
}
.pei-logo-box {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--maroon) 0%, var(--maroon-dark) 100%);
    color: var(--white);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.4rem;
    letter-spacing: 1px;
    box-shadow: 0 3px 10px rgba(122, 30, 40, 0.25);
}

/* ---------- Hero ---------- */
.pei-hero {
    background: linear-gradient(120deg, var(--maroon) 0%, var(--maroon-dark) 100%);
    color: var(--white);
    padding: 2.2rem 2.5rem;
    border-radius: 18px;
    margin-bottom: 1.75rem;
    box-shadow: 0 8px 24px rgba(92, 22, 32, 0.25);
}
.pei-hero h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.pei-hero p {
    font-size: 1.02rem;
    line-height: 1.55;
    color: #F1DEE1;
    max-width: 780px;
}
.pei-hero .legal-badge {
    display: inline-block;
    margin-top: 0.9rem;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.82rem;
    letter-spacing: 0.3px;
}

/* ---------- Section cards ---------- */
.pei-card {
    background: var(--white);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid var(--gray-mid);
    margin-bottom: 1.6rem;
}
.pei-section-title {
    color: var(--maroon-dark);
    font-weight: 700;
    font-size: 1.25rem;
    margin-bottom: 0.15rem;
}
.pei-section-desc {
    color: var(--gray);
    font-size: 0.92rem;
    margin-bottom: 1.1rem;
}
.pei-badge-main {
    display: inline-block;
    background: var(--maroon);
    color: var(--white);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    padding: 0.22rem 0.7rem;
    border-radius: 999px;
    margin-bottom: 0.6rem;
}

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--maroon) 0%, var(--maroon-dark) 100%);
    color: var(--white) !important;
    border: none;
    border-radius: 999px;
    padding: 0.55rem 1.6rem;
    font-family: 'Roboto Condensed', sans-serif;
    font-weight: 600;
    letter-spacing: 0.4px;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 3px 10px rgba(122, 30, 40, 0.25);
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(122, 30, 40, 0.35);
    background: linear-gradient(135deg, var(--maroon-light) 0%, var(--maroon) 100%);
}

/* Secondary / outline buttons (document downloads) */
div[data-testid="stDownloadButton"] > button {
    background: var(--white);
    color: var(--maroon) !important;
    border: 1.5px solid var(--maroon);
    box-shadow: none;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: var(--maroon);
    color: var(--white) !important;
}

/* ---------- Metric result box ---------- */
.pei-result-box {
    background: var(--gray-light);
    border: 1.5px dashed var(--maroon-light);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    text-align: center;
    margin-top: 0.8rem;
}
.pei-result-value {
    color: var(--maroon-dark);
    font-size: 2.1rem;
    font-weight: 700;
}
.pei-result-label {
    color: var(--gray);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ---------- Footer ---------- */
.pei-footer {
    margin-top: 2.5rem;
    padding-top: 2rem;
    border-top: 2px solid var(--gray-mid);
    text-align: center;
    color: var(--gray);
}
.pei-footer .pei-logo-box {
    margin: 0 auto 0.8rem auto;
}
.pei-footer .company-name {
    color: var(--maroon-dark);
    font-weight: 700;
    font-size: 1.05rem;
    margin-bottom: 0.15rem;
}
.pei-footer .address {
    font-size: 0.85rem;
    line-height: 1.5;
}

hr.pei-divider {
    border: none;
    border-top: 1.5px solid var(--gray-mid);
    margin: 1.6rem 0;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================
col_title, col_logo = st.columns([5, 1])
with col_title:
    st.markdown(
        """
        <div style="padding-top:0.4rem;">
            <div class="pei-header-title">PT Pendanaan Efek Indonesia</div>
            <div class="pei-header-sub">Portal Simulasi &amp; Pengajuan Pendanaan Transaksi REPO</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=72)
    else:
        st.markdown('<div class="pei-logo-box">PEI</div>', unsafe_allow_html=True)

st.markdown('<div style="border-bottom:3px solid var(--maroon); margin-bottom:1.6rem;"></div>', unsafe_allow_html=True)

# ============================================================
# HERO / DEFINISI REPO
# ============================================================
st.markdown(
    """
    <div class="pei-hero">
        <h1>Wujudkan Likuiditas dari Portofolio Efek Anda</h1>
        <p>
        Transaksi Repurchase Agreement (<b>Transaksi Repo</b>) adalah kontrak jual atau beli Efek
        dengan janji beli atau jual kembali pada waktu dan harga yang telah ditetapkan.
        Melalui PT Pendanaan Efek Indonesia (PEI), saham dan/atau obligasi yang Anda miliki
        dapat dijadikan jaminan untuk memperoleh pendanaan secara cepat, transparan, dan sesuai ketentuan.
        </p>
        <span class="legal-badge">Diawasi &amp; Diatur oleh OJK</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DOKUMEN PENDUKUNG
# ============================================================
with st.container():
    st.markdown('<div class="pei-card">', unsafe_allow_html=True)
    st.markdown('<div class="pei-section-title">📄 Dokumen Pendukung</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pei-section-desc">Unduh dokumen informasi produk, ketentuan, dan formulir terkait Pendanaan Transaksi REPO.</div>',
        unsafe_allow_html=True,
    )

    doc_files = sorted(DOCS_DIR.glob("*.pdf")) if DOCS_DIR.exists() else []

    if doc_files:
        cols = st.columns(min(len(doc_files), 3))
        for i, doc in enumerate(doc_files):
            with cols[i % len(cols)]:
                st.download_button(
                    label=f"⬇ {doc.stem.replace('_', ' ').title()}",
                    data=doc.read_bytes(),
                    file_name=doc.name,
                    mime="application/pdf",
                    use_container_width=True,
                )
    else:
        st.info(
            "Dokumen pendukung (PDF) belum tersedia — akan tampil otomatis di sini setelah "
            "file ditambahkan ke folder `assets/documents/` pada repository.",
            icon="📎",
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SIMULATOR (placeholder logic — engine perhitungan menyusul)
# ============================================================
with st.container():
    st.markdown('<div class="pei-card">', unsafe_allow_html=True)
    st.markdown('<span class="pei-badge-main">Menu Utama</span>', unsafe_allow_html=True)
    st.markdown('<div class="pei-section-title">🧮 Simulator Perhitungan REPO</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pei-section-desc">Simulasikan estimasi nilai pendanaan dari saham/obligasi yang akan Anda jaminkan. '
        '<i>Catatan: formula perhitungan final (haircut, concentration limit, dsb.) masih dalam tahap pengembangan — '
        'angka di bawah ini bersifat estimasi awal.</i></div>',
        unsafe_allow_html=True,
    )

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        jenis_efek = st.selectbox("Jenis Efek", ["Saham", "Obligasi"])
    with sim_col2:
        kode_efek = st.text_input("Kode Efek", placeholder="Contoh: BBCA")
    with sim_col3:
        jumlah_lembar = st.number_input("Jumlah Lembar / Unit", min_value=0, step=100, value=0)

    harga_efek = st.number_input("Estimasi Harga per Lembar (Rp)", min_value=0, step=50, value=0)

    if st.button("Hitung Estimasi Pendanaan", key="sim_button"):
        if jumlah_lembar > 0 and harga_efek > 0:
            nilai_pasar = jumlah_lembar * harga_efek
            # Placeholder haircut — akan digantikan engine perhitungan resmi
            haircut_dummy = 0.50 if jenis_efek == "Saham" else 0.70
            estimasi_pendanaan = nilai_pasar * haircut_dummy

            st.markdown(
                f"""
                <div class="pei-result-box">
                    <div class="pei-result-label">Estimasi Nilai Pendanaan (Sementara)</div>
                    <div class="pei-result-value">Rp {estimasi_pendanaan:,.0f}</div>
                    <div style="color:var(--gray); font-size:0.8rem; margin-top:0.4rem;">
                        Nilai Pasar: Rp {nilai_pasar:,.0f} &nbsp;•&nbsp; Haircut Estimasi: {int((1-haircut_dummy)*100)}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning("Mohon lengkapi jumlah lembar dan estimasi harga terlebih dahulu.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# FORM PENGAJUAN CALON NASABAH
# ============================================================

def send_submission_email(nama, broker, rencana, saham_obligasi):
    """Kirim notifikasi pengajuan ke email PEI via SMTP (Gmail).
    Kredensial pengirim disimpan di st.secrets, bukan hard-coded."""
    sender_email = st.secrets.get("EMAIL_SENDER", "")
    sender_password = st.secrets.get("EMAIL_PASSWORD", "")

    if not sender_email or not sender_password:
        raise RuntimeError(
            "Kredensial email belum dikonfigurasi di st.secrets "
            "(EMAIL_SENDER / EMAIL_PASSWORD)."
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Portal REPO] Pengajuan Baru — {nama}"
    msg["From"] = sender_email
    msg["To"] = RECIPIENT_EMAIL

    body = f"""
    Pengajuan baru masuk dari Portal Pendanaan Transaksi REPO — PEI

    Waktu           : {datetime.now().strftime('%d %B %Y, %H:%M')} WIB
    Nama Nasabah    : {nama}
    Broker Digunakan: {broker}
    Rencana Pengajuan: {rencana}
    Saham/Obligasi Diajukan: {saham_obligasi}

    ---
    Email ini dikirim otomatis dari Portal Pendanaan Transaksi REPO PEI.
    """
    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, RECIPIENT_EMAIL, msg.as_string())


with st.container():
    st.markdown('<div class="pei-card">', unsafe_allow_html=True)
    st.markdown('<div class="pei-section-title">📝 Form Pengajuan Calon Nasabah</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pei-section-desc">Sudah mendapatkan estimasi dari simulator? Lengkapi form berikut untuk melanjutkan proses pengajuan pendanaan.</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_pengajuan", clear_on_submit=True):
        f_nama = st.text_input("Nama Nasabah *")
        f_broker = st.text_input("Broker yang Dipakai *", placeholder="Contoh: XYZ Sekuritas")
        f_rencana = st.text_area("Rencana Pengajuan *", placeholder="Jelaskan singkat kebutuhan pendanaan Anda")
        f_saham = st.text_area("Saham/Obligasi yang Diajukan *", placeholder="Contoh: BBCA 10.000 lembar, Obligasi ABC Seri A Rp500.000.000")

        submitted = st.form_submit_button("Kirim Pengajuan")

        if submitted:
            if not (f_nama and f_broker and f_rencana and f_saham):
                st.warning("Mohon lengkapi seluruh kolom bertanda (*) sebelum mengirim.")
            else:
                try:
                    send_submission_email(f_nama, f_broker, f_rencana, f_saham)
                    st.success("Pengajuan berhasil dikirim! Tim kami akan segera menghubungi Anda.")
                except Exception as e:
                    st.error(
                        "Pengajuan tercatat, namun notifikasi email gagal terkirim. "
                        f"Detail teknis: {e}"
                    )

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown('<div class="pei-footer">', unsafe_allow_html=True)
if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=64)
else:
    st.markdown('<div class="pei-logo-box">PEI</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="company-name">PT Pendanaan Efek Indonesia</div>
    <div class="address">
        Indonesia Stock Exchange Building Tower I, 3rd Floor Suite 301<br/>
        Jl. Jend. Sudirman Kav. 52-53, Jakarta 12190
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
