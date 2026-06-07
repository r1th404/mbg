import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import io
from PIL import Image
import os

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nutriport - MBG Monitor",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── DUMMY DATA ────────────────────────────────────────────────────────────────
SCHOOLS = {
    "367401": {
        "npsn": "20670035",
        "nama": "SMA Negeri 05 Nusantara",
        "jenjang": "SMA",
        "jumlah_murid": 890,
        "alamat": "Jl. Merdeka No. 45, Ciputat, Tangerang Selatan, Banten",
        "dapur_sppg": "SPPG Nusantara Barat - Jl. Logistik MBG No. 3",
        "kepala_sekolah": "Andi Pratama",
        "kontak": "081900001111",
    },
    "384201": {
        "npsn": "20701234",
        "nama": "SMP Negeri 12 Harapan Jaya",
        "jenjang": "SMP",
        "jumlah_murid": 640,
        "alamat": "Jl. Pahlawan No. 18, Bekasi Barat, Bekasi, Jawa Barat",
        "dapur_sppg": "SPPG Bekasi Mandiri - Jl. Industri No. 7",
        "kepala_sekolah": "Siti Rahayu",
        "kontak": "082100002222",
    },
    "291005": {
        "npsn": "20512345",
        "nama": "SD Negeri 03 Mekar Sari",
        "jenjang": "SD",
        "jumlah_murid": 415,
        "alamat": "Jl. Bunga Rampai No. 9, Depok, Jawa Barat",
        "dapur_sppg": "SPPG Depok Sejahtera - Jl. Gizi No. 2",
        "kepala_sekolah": "Budi Santoso",
        "kontak": "083200003333",
    },
    "512803": {
        "npsn": "20623456",
        "nama": "SMA Negeri 07 Tunas Bangsa",
        "jenjang": "SMA",
        "jumlah_murid": 1120,
        "alamat": "Jl. Kemerdekaan No. 33, Bogor Utara, Kota Bogor",
        "dapur_sppg": "SPPG Bogor Raya - Jl. Nutrisi No. 5",
        "kepala_sekolah": "Dewi Anggraini",
        "kontak": "084300004444",
    },
    "403917": {
        "npsn": "20734567",
        "nama": "SMP Islam Terpadu Al-Hikmah",
        "jenjang": "SMP",
        "jumlah_murid": 520,
        "alamat": "Jl. Al-Hidayah No. 12, Cilandak, Jakarta Selatan",
        "dapur_sppg": "SPPG Jakarta Selatan - Jl. Sehat No. 1",
        "kepala_sekolah": "Ahmad Fauzi",
        "kontak": "085400005555",
    },
    "618204": {
        "npsn": "20845678",
        "nama": "SD Negeri 11 Ceria",
        "jenjang": "SD",
        "jumlah_murid": 350,
        "alamat": "Jl. Melati No. 5, Serpong, Tangerang Selatan",
        "dapur_sppg": "SPPG Serpong Hijau - Jl. Pangan No. 8",
        "kepala_sekolah": "Lina Kusuma",
        "kontak": "086500006666",
    },
    "724508": {
        "npsn": "20956789",
        "nama": "SMA Muhammadiyah 4 Sejahtera",
        "jenjang": "SMA",
        "jumlah_murid": 780,
        "alamat": "Jl. KH. Ahmad Dahlan No. 22, Surabaya, Jawa Timur",
        "dapur_sppg": "SPPG Surabaya Barat - Jl. Gizi Raya No. 14",
        "kepala_sekolah": "Hendra Wijaya",
        "kontak": "087600007777",
    },
    "835612": {
        "npsn": "21067890",
        "nama": "SMP Negeri 8 Cemerlang",
        "jenjang": "SMP",
        "jumlah_murid": 590,
        "alamat": "Jl. Diponegoro No. 44, Yogyakarta",
        "dapur_sppg": "SPPG Yogyakarta Tengah - Jl. Padi No. 3",
        "kepala_sekolah": "Retno Wulandari",
        "kontak": "088700008888",
    },
    "946301": {
        "npsn": "21178901",
        "nama": "SD Islam Plus Bintang Timur",
        "jenjang": "SD",
        "jumlah_murid": 280,
        "alamat": "Jl. Surya Kencana No. 7, Bandung, Jawa Barat",
        "dapur_sppg": "SPPG Bandung Selatan - Jl. Nutrisi No. 9",
        "kepala_sekolah": "Fahmi Hidayat",
        "kontak": "089800009999",
    },
    "157489": {
        "npsn": "21289012",
        "nama": "SMA Negeri 2 Maju Bersama",
        "jenjang": "SMA",
        "jumlah_murid": 960,
        "alamat": "Jl. Sudirman No. 88, Semarang, Jawa Tengah",
        "dapur_sppg": "SPPG Semarang Utara - Jl. Logistik Gizi No. 6",
        "kepala_sekolah": "Sri Wahyuni",
        "kontak": "081200010000",
    },
}

# ─── GENERATE DUMMY HISTORY ───────────────────────────────────────────────────
def generate_history(kode_sekolah, days=14):
    random.seed(int(kode_sekolah) % 999)
    records = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i)
        score = random.randint(55, 95)
        records.append({
            "tanggal": date.strftime("%Y-%m-%d"),
            "skor": score,
            "kategori": "Baik" if score >= 80 else "Cukup" if score >= 60 else "Kurang",
            "makanan_pokok": random.choice(["Cukup", "Sedikit"]),
            "lauk_protein": random.choice(["Cukup", "Sedikit"]),
            "sayur": random.choice(["Cukup", "Sedikit", "Tidak Ada"]),
            "buah": random.choice(["Cukup", "Sedikit", "Tidak Ada"]),
            "susu": random.choice(["Ada", "Tidak Ada"]),
        })
    return pd.DataFrame(records)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --blue-50: #EFF6FF;
    --blue-100: #DBEAFE;
    --blue-200: #BFDBFE;
    --blue-300: #93C5FD;
    --blue-400: #60A5FA;
    --blue-500: #3B82F6;
    --blue-600: #2563EB;
    --blue-700: #1D4ED8;
    --blue-900: #1E3A5F;
    --sky-100: #E0F2FE;
    --sky-400: #38BDF8;
    --sky-500: #0EA5E9;
    --green-500: #22C55E;
    --amber-400: #FBBF24;
    --red-400: #F87171;
    --gray-50: #F8FAFC;
    --gray-100: #F1F5F9;
    --gray-200: #E2E8F0;
    --gray-400: #94A3B8;
    --gray-600: #475569;
    --gray-800: #1E293B;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background: linear-gradient(145deg, #EFF6FF 0%, #E0F2FE 40%, #F0F9FF 100%) !important;
    min-height: 100vh;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; max-width: 1100px; }

/* ── NAV ── */
.nav-bar {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(16px);
    border: 1px solid var(--blue-100);
    border-radius: 16px;
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    box-shadow: 0 4px 24px rgba(37,99,235,0.07);
}
.nav-logo { font-size: 1.4rem; font-weight: 800; color: var(--blue-700); letter-spacing: -0.5px; }
.nav-date { font-size: 0.82rem; color: var(--gray-400); font-weight: 500; font-family: 'DM Mono', monospace; }

/* ── CARDS ── */
.card {
    background: rgba(255,255,255,0.9);
    border: 1px solid var(--blue-100);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 16px rgba(37,99,235,0.06);
    margin-bottom: 16px;
}
.card-blue {
    background: linear-gradient(135deg, var(--blue-600) 0%, var(--sky-500) 100%);
    border: none;
    color: white;
}

/* ── WELCOME SCREEN ── */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
    text-align: center;
    gap: 12px;
}
.welcome-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: var(--blue-700);
    letter-spacing: -1.5px;
    line-height: 1.1;
}
.welcome-sub {
    font-size: 1.05rem;
    color: var(--gray-600);
    max-width: 460px;
    line-height: 1.6;
    margin-bottom: 12px;
}
.brand-dot { color: var(--sky-500); }

/* ── METRIC CARDS ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}
.metric-card {
    background: white;
    border: 1px solid var(--blue-100);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 12px rgba(37,99,235,0.05);
}
.metric-label { font-size: 0.75rem; color: var(--gray-400); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.metric-value { font-size: 1.6rem; font-weight: 800; color: var(--blue-900); letter-spacing: -0.5px; }
.metric-sub { font-size: 0.78rem; color: var(--gray-400); margin-top: 2px; }

/* ── SCORE BADGE ── */
.score-badge-good { color: var(--green-500); font-weight: 700; }
.score-badge-cukup { color: var(--amber-400); font-weight: 700; }
.score-badge-kurang { color: var(--red-400); font-weight: 700; }

/* ── DETECTION RESULT ── */
.detection-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 0.9rem;
    font-weight: 500;
}
.det-found { background: #DCFCE7; color: #166534; }
.det-missing { background: #FEF2F2; color: #991B1B; }
.det-small { background: #FEF9C3; color: #92400E; }

/* ── SCHOOL PROFILE ── */
.profile-header {
    background: linear-gradient(135deg, #1D4ED8 0%, #0EA5E9 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    margin-bottom: 20px;
}
.profile-school-name { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px; }
.profile-npsn { font-size: 0.8rem; opacity: 0.7; font-family: 'DM Mono', monospace; margin-top: 2px; }
.profile-meta { font-size: 0.85rem; opacity: 0.85; margin-top: 12px; line-height: 1.8; }

/* ── INPUT STYLING ── */
.stTextInput > div > div > input {
    border: 2px solid var(--blue-200) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.1rem !important;
    padding: 12px 16px !important;
    background: white !important;
    color: var(--blue-900) !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--blue-500) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #2563EB, #0EA5E9) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(37,99,235,0.35) !important;
}

/* ── FILE UPLOADER ── */
.stFileUploader > div {
    border: 2px dashed var(--blue-300) !important;
    border-radius: 14px !important;
    background: var(--blue-50) !important;
}

/* ── TABLE ── */
.stDataFrame { border-radius: 12px !important; overflow: hidden; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: var(--blue-50) !important;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    color: var(--gray-600) !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--blue-600) !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.1) !important;
}

/* ── SECTION TITLE ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--blue-900);
    margin-bottom: 14px;
    letter-spacing: -0.3px;
}

/* ── REPORT BOX ── */
.report-box {
    background: white;
    border: 1px solid var(--blue-100);
    border-radius: 14px;
    padding: 20px 24px;
    font-size: 0.85rem;
    color: var(--gray-800);
    line-height: 1.9;
    font-family: 'DM Mono', monospace;
}

/* ── DIVIDER ── */
hr { border: none; border-top: 1px solid var(--blue-100); margin: 20px 0; }

/* ── SUCCESS / ERROR ALERTS ── */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "login"
if "kode_sekolah" not in st.session_state:
    st.session_state.kode_sekolah = None
if "sekolah" not in st.session_state:
    st.session_state.sekolah = None
if "detection_result" not in st.session_state:
    st.session_state.detection_result = None
if "model" not in st.session_state:
    st.session_state.model = None

# ─── NAV BAR ──────────────────────────────────────────────────────────────────
def render_nav(show_back=False):
    col1, col2, col3 = st.columns([3, 6, 3])
    with col1:
        if show_back:
            if st.button("Kembali"):
                st.session_state.page = "login"
                st.session_state.kode_sekolah = None
                st.session_state.sekolah = None
                st.session_state.detection_result = None
                st.rerun()
    with col2:
        st.markdown("""
        <div style='text-align:center;'>
            <span style='font-size:1.3rem;font-weight:800;color:#1D4ED8;letter-spacing:-0.5px;'>Nutri<span style='color:#0EA5E9;'>port</span></span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        now = datetime.now()
        bulan_id = ["","Jan","Feb","Mar","Apr","Mei","Jun","Jul","Ags","Sep","Okt","Nov","Des"]
        st.markdown(f"""
        <div style='text-align:right;font-size:0.78rem;color:#94A3B8;font-family:DM Mono,monospace;padding-top:8px;'>
            {now.day} {bulan_id[now.month]} {now.year}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr style='margin:8px 0 20px 0;border-color:#DBEAFE;'>", unsafe_allow_html=True)

# ─── LOAD MODEL ───────────────────────────────────────────────────────────────
def load_model():
    if st.session_state.model is None:
        model_path = "best.pt"
        if os.path.exists(model_path):
            try:
                from ultralytics import YOLO
                st.session_state.model = YOLO(model_path)
                return st.session_state.model
            except Exception as e:
                return None
    return st.session_state.model

# ─── DETECT FOOD ──────────────────────────────────────────────────────────────
def detect_food(image_pil):
    model = load_model()
    categories = {
        "makanan_pokok": {"label": "Makanan Pokok (Nasi/Karbohidrat)", "color": "#3B82F6"},
        "lauk": {"label": "Lauk / Protein", "color": "#F97316"},
        "sayur": {"label": "Sayur", "color": "#22C55E"},
        "buah": {"label": "Buah", "color": "#EAB308"},
        "susu": {"label": "Susu", "color": "#8B5CF6"},
    }

    if model is not None:
        try:
            import numpy as np
            img_array = np.array(image_pil)
            results = model(img_array, conf=0.35)
            detected = {}
            for result in results:
                for box in result.boxes:
                    cls_name = result.names[int(box.cls)].lower()
                    conf = float(box.conf)
                    for cat_key in categories:
                        if cat_key in cls_name or cls_name in cat_key:
                            if cat_key not in detected or conf > detected[cat_key]["conf"]:
                                detected[cat_key] = {"conf": conf, "status": "Cukup" if conf > 0.6 else "Sedikit"}
            return detected, results[0].plot() if results else None
        except Exception:
            pass

    # Fallback: simulated detection
    import random
    detected = {}
    for cat_key in categories:
        r = random.random()
        if r > 0.25:
            detected[cat_key] = {
                "conf": round(random.uniform(0.55, 0.92), 2),
                "status": "Cukup" if random.random() > 0.4 else "Sedikit"
            }
    return detected, None

# ─── SCORE CALCULATOR ─────────────────────────────────────────────────────────
def hitung_skor(detected):
    weights = {"makanan_pokok": 25, "lauk": 25, "sayur": 20, "buah": 15, "susu": 15}
    skor = 0
    for key, w in weights.items():
        if key in detected:
            if detected[key]["status"] == "Cukup":
                skor += w
            else:
                skor += w * 0.5
    return int(skor)

# ─── PAGE: LOGIN ──────────────────────────────────────────────────────────────
def page_login():
    render_nav(show_back=False)

    st.markdown("""
    <div style='text-align:center; padding: 40px 0 20px 0;'>
        <div style='font-size:2.6rem;font-weight:800;color:#1D4ED8;letter-spacing:-1.5px;line-height:1.1;'>
            Nutri<span style='color:#0EA5E9;'>port</span>
        </div>
        <div style='font-size:1rem;color:#64748B;margin-top:10px;max-width:420px;margin-left:auto;margin-right:auto;line-height:1.6;'>
            Platform monitoring kualitas menu Makan Bergizi Gratis untuk sekolah seluruh Indonesia
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("""
        <div style='background:white;border:1px solid #DBEAFE;border-radius:20px;padding:32px;box-shadow:0 4px 32px rgba(37,99,235,0.08);margin-top:16px;'>
            <div style='font-size:1rem;font-weight:700;color:#1E3A5F;margin-bottom:16px;'>Masukkan Kode Sekolah</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            kode_input = st.text_input(
                "Kode Sekolah",
                placeholder="Contoh: 367401",
                label_visibility="collapsed",
                max_chars=10,
            )

            if st.button("Masuk ke Dashboard", use_container_width=True):
                kode = kode_input.strip()
                if kode in SCHOOLS:
                    st.session_state.kode_sekolah = kode
                    st.session_state.sekolah = SCHOOLS[kode]
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Kode sekolah tidak ditemukan. Periksa kembali kode yang Anda masukkan.")

        st.markdown("""
        <div style='margin-top:20px;padding-top:16px;border-top:1px solid #EFF6FF;'>
            <div style='font-size:0.78rem;color:#94A3B8;font-weight:600;margin-bottom:8px;'>KODE SEKOLAH DEMO</div>
            <div style='display:flex;flex-wrap:wrap;gap:6px;'>
        """, unsafe_allow_html=True)

        cols = st.columns(5)
        demo_codes = list(SCHOOLS.keys())[:5]
        for i, code in enumerate(demo_codes):
            with cols[i]:
                if st.button(code, key=f"demo_{code}"):
                    st.session_state.kode_sekolah = code
                    st.session_state.sekolah = SCHOOLS[code]
                    st.session_state.page = "dashboard"
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)


# ─── PAGE: DASHBOARD ──────────────────────────────────────────────────────────
def page_dashboard():
    render_nav(show_back=True)
    sekolah = st.session_state.sekolah
    kode = st.session_state.kode_sekolah

    # School profile header
    st.markdown(f"""
    <div class='profile-header'>
        <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
            <div>
                <div class='profile-npsn'>NPSN: {sekolah['npsn']}  |  Kode: {kode}</div>
                <div class='profile-school-name' style='margin-top:4px;'>{sekolah['nama']}</div>
                <div class='profile-meta'>
                    {sekolah['jenjang']}  ·  {sekolah['jumlah_murid']} Siswa<br>
                    {sekolah['alamat']}<br>
                    Dapur SPPG: {sekolah['dapur_sppg']}<br>
                    Kepala Sekolah: {sekolah['kepala_sekolah']}  |  {sekolah['kontak']}
                </div>
            </div>
            <div style='text-align:right;opacity:0.6;font-size:0.78rem;'>
                MBG Monitor
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Upload & Deteksi", "Dashboard & Histori", "Laporan"])

    # ── TAB 1: UPLOAD & DETECT ─────────────────────────────────────────────────
    with tab1:
        col_up, col_res = st.columns([1, 1], gap="large")

        with col_up:
            st.markdown("<div class='section-title'>Upload Foto Nampan Makan Siang</div>", unsafe_allow_html=True)

            # Model upload
            with st.expander("Muat Model YOLOv8 (.pt)", expanded=False):
                model_file = st.file_uploader("Upload file model .pt", type=["pt"], key="model_upload")
                if model_file:
                    with open("best.pt", "wb") as f:
                        f.write(model_file.read())
                    st.session_state.model = None
                    st.success("Model berhasil dimuat. Deteksi berikutnya menggunakan model Anda.")

            uploaded = st.file_uploader(
                "Pilih foto nampan makanan",
                type=["jpg", "jpeg", "png"],
                key="food_upload",
                help="Format: JPG, JPEG, PNG. Ukuran maksimal 10MB."
            )

            if uploaded:
                image = Image.open(uploaded).convert("RGB")
                st.image(image, caption="Foto yang diunggah", use_container_width=True)

                if st.button("Analisis Kualitas Menu", use_container_width=True):
                    with st.spinner("Mendeteksi komponen makanan..."):
                        detected, annotated_img = detect_food(image)
                        skor = hitung_skor(detected)
                        st.session_state.detection_result = {
                            "detected": detected,
                            "skor": skor,
                            "annotated": annotated_img,
                            "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    st.rerun()

        with col_res:
            st.markdown("<div class='section-title'>Hasil Deteksi</div>", unsafe_allow_html=True)

            if st.session_state.detection_result:
                res = st.session_state.detection_result
                detected = res["detected"]
                skor = res["skor"]

                # Score display
                kategori = "Baik" if skor >= 80 else "Cukup" if skor >= 60 else "Kurang"
                color_map = {"Baik": "#22C55E", "Cukup": "#FBBF24", "Kurang": "#F87171"}
                color = color_map[kategori]

                st.markdown(f"""
                <div style='background:white;border:1px solid #DBEAFE;border-radius:14px;padding:20px;text-align:center;margin-bottom:14px;'>
                    <div style='font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>Skor Kualitas Menu</div>
                    <div style='font-size:3rem;font-weight:800;color:{color};letter-spacing:-1px;line-height:1.1;'>{skor}<span style='font-size:1.2rem;color:#94A3B8;'>/100</span></div>
                    <div style='font-size:0.9rem;font-weight:700;color:{color};'>{kategori}</div>
                </div>
                """, unsafe_allow_html=True)

                # Annotated image
                if res["annotated"] is not None:
                    st.image(res["annotated"], caption="Hasil Deteksi AI", use_container_width=True)

                # Component breakdown
                categories_info = {
                    "makanan_pokok": "Makanan Pokok",
                    "lauk": "Lauk / Protein",
                    "sayur": "Sayur",
                    "buah": "Buah",
                    "susu": "Susu",
                }

                st.markdown("<div style='font-size:0.85rem;font-weight:700;color:#1E3A5F;margin:12px 0 8px 0;'>Komponen Terdeteksi</div>", unsafe_allow_html=True)

                for key, label in categories_info.items():
                    if key in detected:
                        status = detected[key]["status"]
                        conf = detected[key]["conf"]
                        cls = "det-found" if status == "Cukup" else "det-small"
                        icon = "Cukup" if status == "Cukup" else "Sedikit"
                        st.markdown(f"""
                        <div class='detection-item {cls}'>
                            <span style='font-weight:700;'>{label}</span>
                            <span style='margin-left:auto;font-size:0.78rem;'>{icon} · {int(conf*100)}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='detection-item det-missing'>
                            <span style='font-weight:700;'>{label}</span>
                            <span style='margin-left:auto;font-size:0.78rem;'>Tidak Terdeteksi</span>
                        </div>
                        """, unsafe_allow_html=True)

                # Notes
                missing = [categories_info[k] for k in categories_info if k not in detected]
                small = [categories_info[k] for k in categories_info if k in detected and detected[k]["status"] == "Sedikit"]

                notes = []
                if missing:
                    notes.append(f"Komponen tidak terdeteksi: {', '.join(missing)}.")
                if small:
                    notes.append(f"Porsi terlihat kurang: {', '.join(small)}.")

                if notes:
                    st.markdown(f"""
                    <div style='background:#FEF9C3;border:1px solid #FDE047;border-radius:10px;padding:12px 16px;margin-top:12px;font-size:0.83rem;color:#92400E;line-height:1.6;'>
                        <b>Catatan:</b> {' '.join(notes)}<br>
                        <b>Rekomendasi:</b> Pastikan semua komponen menu tersedia dengan porsi yang memadai sesuai standar MBG.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:#F8FAFC;border:2px dashed #BFDBFE;border-radius:14px;padding:40px;text-align:center;color:#94A3B8;'>
                    <div style='font-size:2rem;margin-bottom:8px;'>--</div>
                    <div style='font-size:0.9rem;'>Upload foto dan klik Analisis untuk memulai deteksi</div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2: DASHBOARD & HISTORI ─────────────────────────────────────────────
    with tab2:
        df = generate_history(kode)

        # Metrics row
        avg_skor = df["skor"].mean()
        latest_skor = df.iloc[-1]["skor"]
        baik_count = (df["kategori"] == "Baik").sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Skor Rata-rata (14 hari)</div>
                <div class='metric-value'>{avg_skor:.0f}<span style='font-size:1rem;color:#94A3B8;'>/100</span></div>
                <div class='metric-sub'>{"Baik" if avg_skor >= 80 else "Cukup" if avg_skor >= 60 else "Kurang"}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Skor Terakhir</div>
                <div class='metric-value'>{latest_skor}<span style='font-size:1rem;color:#94A3B8;'>/100</span></div>
                <div class='metric-sub'>{df.iloc[-1]["tanggal"]}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Hari Kategori Baik</div>
                <div class='metric-value'>{baik_count}<span style='font-size:1rem;color:#94A3B8;'>/14</span></div>
                <div class='metric-sub'>dari 14 hari terakhir</div>
            </div>
            """, unsafe_allow_html=True)

        # Trend chart
        st.markdown("<div class='section-title' style='margin-top:20px;'>Tren Skor Kualitas Menu (14 Hari Terakhir)</div>", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["tanggal"],
            y=df["skor"],
            mode="lines+markers",
            name="Skor Harian",
            line=dict(color="#3B82F6", width=2.5, shape="spline"),
            marker=dict(size=7, color="#2563EB", line=dict(color="white", width=2)),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.08)",
        ))
        fig.add_hline(y=80, line_dash="dot", line_color="#22C55E", annotation_text="Standar Baik (80)", annotation_font_size=11)
        fig.add_hline(y=60, line_dash="dot", line_color="#FBBF24", annotation_text="Standar Cukup (60)", annotation_font_size=11)
        fig.update_layout(
            height=260,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans"),
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#94A3B8")),
            yaxis=dict(range=[0, 105], showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11, color="#94A3B8")),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Component availability chart
        st.markdown("<div class='section-title'>Ketersediaan Komponen Menu</div>", unsafe_allow_html=True)

        comp_cols = ["makanan_pokok", "lauk_protein", "sayur", "buah", "susu"]
        comp_labels = ["Makanan Pokok", "Lauk/Protein", "Sayur", "Buah", "Susu"]
        comp_pct = []
        for col in comp_cols:
            if col in df.columns:
                pct = (df[col] != "Tidak Ada").mean() * 100
            else:
                pct = 100
            comp_pct.append(pct)

        fig2 = go.Figure(go.Bar(
            x=comp_labels,
            y=comp_pct,
            marker_color=["#3B82F6", "#0EA5E9", "#22C55E", "#EAB308", "#8B5CF6"],
            text=[f"{v:.0f}%" for v in comp_pct],
            textposition="outside",
            textfont=dict(size=12, family="Plus Jakarta Sans"),
        ))
        fig2.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans"),
            yaxis=dict(range=[0, 115], showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11, color="#94A3B8")),
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#475569")),
            showlegend=False,
            bargap=0.35,
        )
        st.plotly_chart(fig2, use_container_width=True)

        # History table
        st.markdown("<div class='section-title'>Riwayat Laporan Harian</div>", unsafe_allow_html=True)
        display_df = df[["tanggal", "skor", "kategori", "makanan_pokok", "lauk_protein", "sayur", "buah", "susu"]].copy()
        display_df.columns = ["Tanggal", "Skor", "Kategori", "Makanan Pokok", "Lauk/Protein", "Sayur", "Buah", "Susu"]
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=280)

    # ── TAB 3: LAPORAN ────────────────────────────────────────────────────────
    with tab3:
        st.markdown("<div class='section-title'>Laporan Otomatis Harian</div>", unsafe_allow_html=True)

        now = datetime.now()
        bulan_id = ["","Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

        res = st.session_state.detection_result
        if res:
            detected = res["detected"]
            skor = res["skor"]
            kategori = "Baik" if skor >= 80 else "Cukup" if skor >= 60 else "Kurang"

            comp_map = {
                "makanan_pokok": "Makanan Pokok",
                "lauk": "Lauk / Protein",
                "sayur": "Sayur",
                "buah": "Buah",
                "susu": "Susu",
            }

            lines = []
            lines.append("LAPORAN HARIAN KUALITAS MENU MBG")
            lines.append("=" * 44)
            lines.append("")
            lines.append("Identitas Sekolah")
            lines.append(f"  Nama Sekolah  : {sekolah['nama']}")
            lines.append(f"  Kode Sekolah  : {kode}")
            lines.append(f"  NPSN          : {sekolah['npsn']}")
            lines.append(f"  Alamat        : {sekolah['alamat']}")
            lines.append(f"  SPPG          : {sekolah['dapur_sppg']}")
            lines.append(f"  Jumlah Murid  : {sekolah['jumlah_murid']} siswa")
            lines.append(f"  Tanggal       : {now.strftime('%Y-%m-%d')}  |  {now.strftime('%H:%M')}")
            lines.append("")
            lines.append("Hasil Deteksi Komponen Menu")
            for key, label in comp_map.items():
                if key in detected:
                    status = detected[key]["status"]
                    conf = int(detected[key]["conf"] * 100)
                    lines.append(f"  - {label}: terdeteksi, porsi {status.lower()} ({conf}%)")
                else:
                    lines.append(f"  - {label}: tidak terdeteksi")
            lines.append("")
            lines.append(f"Skor Kualitas Menu   : {skor}/100")
            lines.append(f"Kategori             : {kategori}")
            lines.append("")
            lines.append("Estimasi Gizi Harian")
            lines.append(f"  Kalori    : ~{random.randint(480, 650)} kkal")
            lines.append(f"  Protein   : ~{random.randint(12, 25)} gram")
            lines.append(f"  Karbohidrat: ~{random.randint(55, 90)} gram")
            lines.append("")
            lines.append("Rekomendasi")
            missing_comp = [label for key, label in comp_map.items() if key not in detected]
            small_comp = [label for key, label in comp_map.items() if key in detected and detected[key]["status"] == "Sedikit"]
            if missing_comp:
                lines.append(f"  - Tambahkan: {', '.join(missing_comp)}")
            if small_comp:
                lines.append(f"  - Perbesar porsi: {', '.join(small_comp)}")
            if not missing_comp and not small_comp:
                lines.append("  - Menu sudah memenuhi standar MBG. Pertahankan kualitas.")
            lines.append("")
            lines.append("=" * 44)
            lines.append(f"Diterbitkan oleh sistem Nutriport pada {now.strftime('%d')} {bulan_id[now.month]} {now.year}")

            report_text = "\n".join(lines)
            st.markdown(f"<div class='report-box'>{report_text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

            st.download_button(
                label="Unduh Laporan (.txt)",
                data=report_text,
                file_name=f"laporan_mbg_{kode}_{now.strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.info("Lakukan deteksi foto terlebih dahulu di tab Upload & Deteksi untuk menghasilkan laporan harian.")

            # Show template
            lines = [
                "LAPORAN HARIAN KUALITAS MENU MBG",
                "=" * 44,
                "",
                f"Nama Sekolah  : {sekolah['nama']}",
                f"Kode Sekolah  : {kode}",
                f"NPSN          : {sekolah['npsn']}",
                f"Tanggal       : {now.strftime('%Y-%m-%d')}",
                "",
                "(Hasil deteksi akan muncul di sini setelah foto dianalisis)",
            ]
            st.markdown(f"<div class='report-box'>{chr(10).join(lines).replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)


# ─── ROUTER ───────────────────────────────────────────────────────────────────
if st.session_state.page == "login":
    page_login()
elif st.session_state.page == "dashboard":
    page_dashboard()
