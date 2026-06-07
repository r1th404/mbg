import streamlit as st
import requests
import io
import random
import tempfile
import os
import numpy as np
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

st.set_page_config(
    page_title="Nutriport",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem; }
section[data-testid="stSidebar"] { background: #0f0f0f; }
section[data-testid="stSidebar"] * { color: #ccc !important; }
section[data-testid="stSidebar"] .stFileUploader label { color: #aaa !important; }

.nutriport-nav {
    background: #0a0a0a; color: #fff; padding: 1rem 2rem;
    display: flex; justify-content: space-between; align-items: center;
    margin: -1rem -1rem 0 -1rem;
}
.nutriport-nav .brand { font-family: 'DM Serif Display', serif; font-size: 1.4rem; letter-spacing: -0.02em; }
.nutriport-nav .date-badge { font-size: 0.85rem; color: #888; letter-spacing: 0.05em; }

.school-card {
    background: #f8f6f0; border-radius: 16px; padding: 1.5rem 2rem;
    margin-bottom: 1.5rem; border-left: 4px solid #0a0a0a;
}
.school-name { font-family: 'DM Serif Display', serif; font-size: 1.6rem; color: #0a0a0a; margin-bottom: 0.25rem; }
.school-meta { font-size: 0.85rem; color: #666; line-height: 1.8; }

.score-container {
    display: flex; align-items: center; gap: 1.5rem;
    background: #0a0a0a; color: white; border-radius: 16px; padding: 1.5rem 2rem;
}
.score-number { font-family: 'DM Serif Display', serif; font-size: 3.5rem; line-height: 1; }
.score-label { font-size: 0.8rem; color: #aaa; text-transform: uppercase; letter-spacing: 0.08em; }
.score-category { font-size: 1.1rem; color: #e8e0d0; margin-top: 0.2rem; }

.food-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 1rem; }
.food-tag { padding: 6px 14px; border-radius: 99px; font-size: 0.82rem; font-weight: 500; }
.tag-ok   { background: #d4edda; color: #1a5c2a; }
.tag-warn { background: #fff3cd; color: #7d5c00; }
.tag-bad  { background: #f8d7da; color: #721c24; }

.section-header {
    font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: #0a0a0a;
    margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e0ddd5;
}
.metric-row { display: flex; gap: 12px; margin-bottom: 1.5rem; }
.metric-box { flex: 1; background: #f8f6f0; border-radius: 12px; padding: 1rem 1.25rem; text-align: center; }
.metric-val { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #0a0a0a; display: block; }
.metric-lbl { font-size: 0.78rem; color: #888; text-transform: uppercase; letter-spacing: 0.06em; }

.history-item {
    background: #fff; border: 1px solid #e8e4da; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 0.75rem;
    display: flex; justify-content: space-between; align-items: center;
}
.history-date { font-size: 0.82rem; color: #999; }
.history-score { font-family: 'DM Serif Display', serif; font-size: 1.4rem; }

.stButton > button {
    background: #0a0a0a !important; color: white !important; border: none !important;
    border-radius: 99px !important; padding: 0.6rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important;
    font-weight: 500 !important;
}
.stButton > button:hover { background: #333 !important; }
.logout-btn > button {
    background: transparent !important; color: #888 !important;
    border: 1px solid #444 !important; padding: 0.3rem 1.2rem !important;
    font-size: 0.8rem !important;
}
.stTextInput > div > div > input {
    border-radius: 12px !important; border: 1.5px solid #d0cdc5 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 1.1rem !important;
    padding: 0.75rem 1rem !important; letter-spacing: 0.08em !important;
}
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: #f0ede6; padding: 4px; border-radius: 12px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px; padding: 0.4rem 1.2rem; font-family: 'DM Sans', sans-serif; font-size: 0.88rem; }
.stTabs [aria-selected="true"] { background: #0a0a0a !important; color: white !important; }

.report-box {
    background: #fffef8; border: 1px solid #e0ddd5; border-radius: 12px;
    padding: 1.5rem; font-size: 0.85rem; line-height: 1.9; color: #333;
}
.custom-alert { padding: 0.75rem 1rem; border-radius: 10px; font-size: 0.88rem; margin-bottom: 1rem; }
.alert-warn { background: #fff8e6; border-left: 3px solid #e8a000; color: #7d5c00; }
.alert-good { background: #edfaf0; border-left: 3px solid #28a745; color: #1a5c2a; }
.alert-info { background: #e8f0fe; border-left: 3px solid #4285f4; color: #1a3c8f; }

.model-status-ok  { background:#edfaf0; border:1px solid #28a745; border-radius:10px; padding:0.6rem 1rem; font-size:0.83rem; color:#1a5c2a; margin-bottom:0.5rem; }
.model-status-no  { background:#f8f0e6; border:1px solid #e8a000; border-radius:10px; padding:0.6rem 1rem; font-size:0.83rem; color:#7d5c00; margin-bottom:0.5rem; }
</style>
""", unsafe_allow_html=True)


# ── CONSTANTS ─────────────────────────────────────────────────────────────────
# Mapping: class name in model → display label + kategori nutrisi
CLASS_MAP = {
    "makanan_pokok": {"label": "Makanan Pokok", "kategori": "Makanan Pokok"},
    "nasi":          {"label": "Makanan Pokok", "kategori": "Makanan Pokok"},
    "lauk":          {"label": "Lauk/Protein",  "kategori": "Lauk/Protein"},
    "protein":       {"label": "Lauk/Protein",  "kategori": "Lauk/Protein"},
    "sayur":         {"label": "Sayur",          "kategori": "Sayur"},
    "sayuran":       {"label": "Sayur",          "kategori": "Sayur"},
    "buah":          {"label": "Buah",           "kategori": "Buah"},
    "buahan":        {"label": "Buah",           "kategori": "Buah"},
    "susu":          {"label": "Susu",           "kategori": "Susu"},
}
KOMPONEN_WAJIB = ["Makanan Pokok", "Lauk/Protein", "Sayur", "Buah", "Susu"]

# Confidence thresholds
CONF_OK   = 0.6   # ≥ 0.6 → cukup
CONF_WARN = 0.35  # 0.35–0.6 → sedikit/kurang yakin

# Bbox draw colors per class
BBOX_COLORS = {
    "Makanan Pokok": "#00d4ff",
    "Lauk/Protein":  "#ff6b35",
    "Sayur":         "#4ade80",
    "Buah":          "#a78bfa",
    "Susu":          "#60a5fa",
}


# ── HELPERS ───────────────────────────────────────────────────────────────────
def nav_bar():
    today = datetime.now().strftime("%d %b %Y").upper()
    st.markdown(f"""
    <div class="nutriport-nav">
        <span class="brand">Nutriport</span>
        <span class="date-badge">{today}</span>
    </div>
    """, unsafe_allow_html=True)


def fetch_school(npsn: str):
    try:
        r = requests.get(f"https://api.fazriansyah.eu.org/v1/sekolah?npsn={npsn}", timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def score_color(score: int) -> str:
    if score >= 80: return "#c8f0a0"
    if score >= 60: return "#ffd98f"
    return "#ff9f9f"


def score_category(score: int) -> str:
    if score >= 85: return "Sangat Baik"
    if score >= 70: return "Baik"
    if score >= 55: return "Cukup"
    return "Perlu Perbaikan"


def get_jenjang_label(nama: str) -> str:
    nama = nama.upper()
    for key in ["SMK", "SMA", "SMP", "SD", "TK", "MI", "MTS", "MA"]:
        if key in nama:
            return key
    return "SEKOLAH"


def generate_dummy_history(npsn: str, n=14):
    random.seed(int(npsn[:6]) if npsn.isdigit() else 42)
    history = []
    for i in range(n):
        date = datetime.now() - timedelta(days=n - i)
        score = random.randint(48, 95)
        history.append({
            "Tanggal": date.strftime("%Y-%m-%d"),
            "Skor": score,
            "Kategori": score_category(score),
        })
    return history


def load_yolo_model(model_bytes: bytes):
    """Load YOLOv8 model from bytes. Returns model or None."""
    try:
        from ultralytics import YOLO
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as f:
            f.write(model_bytes)
            tmp_path = f.name
        model = YOLO(tmp_path)
        return model
    except ImportError:
        st.sidebar.error("ultralytics belum terinstall. Jalankan: pip install ultralytics")
        return None
    except Exception as e:
        st.sidebar.error(f"Gagal load model: {e}")
        return None


def draw_detections(pil_img: Image.Image, detections: list) -> Image.Image:
    """Draw bounding boxes on image. detections = list of {label, conf, box:[x1,y1,x2,y2]}"""
    img = pil_img.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    for det in detections:
        label  = det["label"]
        conf   = det["conf"]
        x1, y1, x2, y2 = det["box"]
        color  = BBOX_COLORS.get(label, "#ffffff")

        # box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        # label background
        text = f"{label.split('/')[0].lower()} {conf:.2f}"
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except:
            font = ImageFont.load_default()

        bbox_text = draw.textbbox((x1, y1 - 18), text, font=font)
        draw.rectangle([bbox_text[0]-2, bbox_text[1]-2, bbox_text[2]+2, bbox_text[3]+2], fill=color)
        draw.text((x1, y1 - 18), text, fill="#000000", font=font)

    return img


def run_yolo_inference(model, pil_img: Image.Image, conf_threshold: float = 0.25) -> dict:
    """Run real YOLOv8 inference. Returns structured result dict."""
    import numpy as np

    img_array = np.array(pil_img.convert("RGB"))
    results = model(img_array, conf=conf_threshold, verbose=False)
    result  = results[0]

    # Parse detections
    detections = []
    raw_classes = {}  # kategori → list of conf

    for box in result.boxes:
        cls_id   = int(box.cls[0])
        cls_name = model.names[cls_id].lower().strip()
        conf     = float(box.conf[0])
        xyxy     = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

        # Map to nutrisi category
        mapped = CLASS_MAP.get(cls_name)
        if mapped is None:
            # Try partial match
            for k, v in CLASS_MAP.items():
                if k in cls_name or cls_name in k:
                    mapped = v
                    break
        if mapped is None:
            mapped = {"label": cls_name.title(), "kategori": cls_name.title()}

        kategori = mapped["kategori"]
        label    = mapped["label"]

        detections.append({
            "label": label,
            "conf": conf,
            "box": xyxy,
            "cls_raw": cls_name,
        })

        if kategori not in raw_classes:
            raw_classes[kategori] = []
        raw_classes[kategori].append(conf)

    # Build component summary
    components = {}
    for komp in KOMPONEN_WAJIB:
        if komp in raw_classes:
            best_conf = max(raw_classes[komp])
            if best_conf >= CONF_OK:
                porsi = "cukup"
                status = "terdeteksi"
            elif best_conf >= CONF_WARN:
                porsi = "sedikit"
                status = "terdeteksi"
            else:
                porsi = "tidak yakin"
                status = "terdeteksi"
        else:
            porsi  = "tidak ada"
            status = "tidak terdeteksi"
        components[komp] = {"status": status, "porsi": porsi}

    # Score: weighted by detected components + avg confidence
    detected_count = sum(1 for v in components.values() if v["status"] == "terdeteksi")
    full_count     = sum(1 for v in components.values() if v["porsi"] == "cukup")
    all_confs      = [max(v) for v in raw_classes.values()] if raw_classes else [0]
    avg_conf       = sum(all_confs) / len(all_confs) if all_confs else 0

    score = int(
        (detected_count / 5) * 50 +   # 50 pts: semua komponen ada
        (full_count / 5) * 30 +        # 30 pts: semua porsi cukup
        avg_conf * 20                  # 20 pts: confidence rata-rata
    )
    score = min(100, max(0, score))

    kurang = [k for k, v in components.items()
              if v["status"] == "tidak terdeteksi" or v["porsi"] in ["sedikit", "tidak ada", "tidak yakin"]]

    # Rough nutrition estimate
    kalori   = 350 + detected_count * 40 + full_count * 30
    protein  = 8   + detected_count * 4

    return {
        "score":      score,
        "category":   score_category(score),
        "components": components,
        "detections": detections,
        "kurang":     kurang,
        "kalori":     kalori,
        "protein_g":  protein,
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M"),
        "n_detected": len(detections),
    }


def run_dummy_inference(pil_img: Image.Image) -> dict:
    """Fallback when no model loaded."""
    random.seed(sum(list(pil_img.tobytes()[:64])))
    components = {
        "Makanan Pokok": {"status": "terdeteksi",      "porsi": "cukup"},
        "Lauk/Protein":  {"status": "terdeteksi",      "porsi": random.choice(["cukup", "sedikit"])},
        "Sayur":         {"status": "terdeteksi",      "porsi": random.choice(["cukup", "sedikit"])},
        "Buah":          {"status": random.choice(["terdeteksi", "tidak terdeteksi"]), "porsi": "sedikit"},
        "Susu":          {"status": random.choice(["terdeteksi", "tidak terdeteksi"]), "porsi": "cukup"},
    }
    detected = sum(1 for v in components.values() if v["status"] == "terdeteksi")
    full     = sum(1 for v in components.values() if v["porsi"] == "cukup")
    score    = int((detected / 5) * 50 + (full / 5) * 30 + random.uniform(0.5, 0.9) * 20)
    kurang   = [k for k, v in components.items()
                if v["status"] == "tidak terdeteksi" or v["porsi"] in ["sedikit", "tidak ada"]]
    # Fake bboxes for visualization
    W, H = pil_img.size
    dummy_dets = []
    positions = [(0.05, 0.05, 0.45, 0.48), (0.5, 0.05, 0.95, 0.48),
                 (0.05, 0.52, 0.45, 0.95), (0.5, 0.52, 0.75, 0.95), (0.1, 0.7, 0.4, 0.95)]
    for i, (komp, info) in enumerate(components.items()):
        if info["status"] == "terdeteksi" and i < len(positions):
            x1r, y1r, x2r, y2r = positions[i]
            dummy_dets.append({
                "label": komp,
                "conf": round(random.uniform(0.65, 0.92), 2),
                "box": [W*x1r, H*y1r, W*x2r, H*y2r],
            })
    return {
        "score": score, "category": score_category(score),
        "components": components, "detections": dummy_dets,
        "kurang": kurang, "kalori": 350 + detected * 40,
        "protein_g": 8 + detected * 4,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "n_detected": len(dummy_dets),
    }


# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "school_data"      not in st.session_state: st.session_state.school_data      = None
if "npsn_input"       not in st.session_state: st.session_state.npsn_input       = ""
if "detection_result" not in st.session_state: st.session_state.detection_result = None
if "annotated_image"  not in st.session_state: st.session_state.annotated_image  = None
if "report_history"   not in st.session_state: st.session_state.report_history   = []
if "yolo_model"       not in st.session_state: st.session_state.yolo_model       = None
if "model_name"       not in st.session_state: st.session_state.model_name       = ""


# ── SIDEBAR — Model Upload ────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="font-family:'DM Serif Display',serif; font-size:1.2rem; color:#eee; margin-bottom:1rem;">
            🧠 Model YOLOv8
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.yolo_model is not None:
            st.markdown(f"""
            <div class="model-status-ok">
                ✅ Model aktif<br>
                <span style="font-size:0.78rem; opacity:0.8;">{st.session_state.model_name}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🗑 Hapus Model", use_container_width=True):
                st.session_state.yolo_model = None
                st.session_state.model_name = ""
                st.rerun()
        else:
            st.markdown("""
            <div class="model-status-no">
                ⚠️ Belum ada model<br>
                <span style="font-size:0.78rem;">Mode simulasi aktif</span>
            </div>
            """, unsafe_allow_html=True)

        model_file = st.file_uploader(
            "Upload file .pt",
            type=["pt"],
            help="Model YOLOv8 hasil training (.pt)",
            label_visibility="visible"
        )

        if model_file is not None and model_file.name != st.session_state.model_name:
            with st.spinner("Loading model..."):
                model = load_yolo_model(model_file.read())
            if model is not None:
                st.session_state.yolo_model = model
                st.session_state.model_name = model_file.name
                st.success(f"Model berhasil dimuat!")
                # Show classes
                class_names = list(model.names.values())
                st.markdown(f"""
                <div style="font-size:0.78rem; color:#aaa; margin-top:0.5rem;">
                    <strong style="color:#ddd;">Kelas terdeteksi ({len(class_names)}):</strong><br>
                    {', '.join(class_names[:20])}{'...' if len(class_names) > 20 else ''}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.78rem; color:#666; line-height:1.7;">
            <strong style="color:#aaa;">Tips:</strong><br>
            • Upload model YOLOv8s/m yang sudah ditraining<br>
            • Class: makanan_pokok, lauk, sayur, buah, susu<br>
            • Threshold confidence: 0.25
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.school_data:
            st.markdown("---")
            st.markdown('<div style="font-size:0.78rem; color:#666; margin-bottom:0.5rem;">Session</div>', unsafe_allow_html=True)
            sp = st.session_state.school_data.get("satuanPendidikan", {})
            st.markdown(f'<div style="font-size:0.82rem; color:#aaa;">{sp.get("nama","")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.75rem; color:#555;">NPSN: {sp.get("npsn","")}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — LOGIN
# ════════════════════════════════════════════════════════════════════════════
def page_login():
    nav_bar()
    render_sidebar()

    col_center = st.columns([1, 1.8, 1])[1]
    with col_center:
        st.markdown("""
        <div style="padding: 4rem 0 2rem; text-align: center;">
            <div style="font-family:'DM Serif Display',serif; font-size:3rem; line-height:1.1; color:#0a0a0a; margin-bottom:0.5rem;">
                Pantau kualitas<br><em>menu MBG</em> sekolah
            </div>
            <div style="font-size:1rem; color:#666; margin:1rem 0 2rem; line-height:1.7;">
                Sistem laporan harian gizi program<br>Makan Bergizi Gratis berbasis AI.
            </div>
        </div>
        """, unsafe_allow_html=True)

        npsn = st.text_input("", placeholder="Masukkan NPSN sekolah (8 digit)", max_chars=12)
        col_btn = st.columns([1, 1, 1])[1]
        with col_btn:
            login_btn = st.button("Masuk →", use_container_width=True)

        if login_btn:
            npsn_clean = npsn.strip()
            if len(npsn_clean) < 6:
                st.error("NPSN minimal 6 digit.")
            else:
                with st.spinner("Mengambil data sekolah..."):
                    data = fetch_school(npsn_clean)
                if data and "data" in data:
                    st.session_state.school_data  = data["data"]
                    st.session_state.npsn_input   = npsn_clean
                    st.session_state.report_history = generate_dummy_history(npsn_clean)
                    st.rerun()
                else:
                    st.error("Sekolah tidak ditemukan. Periksa NPSN dan coba lagi.")

        st.markdown("""
        <div style="text-align:center; margin-top:3rem; font-size:0.8rem; color:#bbb;">
            Data sekolah bersumber dari Kemdikbud · Deteksi makanan oleh YOLOv8
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    nav_bar()
    render_sidebar()

    school  = st.session_state.school_data
    sp      = school.get("satuanPendidikan", {})
    npsn    = sp.get("npsn", st.session_state.npsn_input)
    nama    = sp.get("nama", "Sekolah")
    jenjang = get_jenjang_label(nama)
    alamat  = sp.get("alamatJalan", "") + ", " + sp.get("namaKecamatan", "")
    kota    = sp.get("namaKabupaten", "") + ", " + sp.get("namaProvinsi", "")
    akred   = sp.get("akreditasi", "-")
    history = st.session_state.report_history

    # ── School header ──────────────────────────────────────────────────────
    col_main, col_logout = st.columns([6, 1])
    with col_main:
        st.markdown(f"""
        <div class="school-card">
            <div class="school-name">{nama}</div>
            <div class="school-meta">
                NPSN: {npsn} &nbsp;·&nbsp; Jenjang: {jenjang} &nbsp;·&nbsp; Akreditasi: {akred}<br>
                📍 {alamat}<br>{kota}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Keluar"):
            st.session_state.school_data      = None
            st.session_state.detection_result = None
            st.session_state.annotated_image  = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📸  Unggah & Analisis", "📊  Riwayat & Grafik", "📄  Laporan"])

    # ────────────────────────────────────────────────────────────────────
    # TAB 1 — Upload & Detect
    # ────────────────────────────────────────────────────────────────────
    with tab1:
        model_loaded = st.session_state.yolo_model is not None
        if not model_loaded:
            st.markdown("""
            <div class="custom-alert alert-info">
                ℹ️ <strong>Mode simulasi:</strong> Upload model <code>.pt</code> di sidebar kiri untuk deteksi nyata dengan YOLOv8.
            </div>
            """, unsafe_allow_html=True)

        col_up, col_res = st.columns([1, 1], gap="large")

        with col_up:
            st.markdown('<div class="section-header">Foto Menu Hari Ini</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader(
                "Unggah foto nampan makanan MBG",
                type=["jpg", "jpeg", "png", "webp"],
                label_visibility="collapsed"
            )

            if uploaded:
                img_bytes = uploaded.read()
                pil_img   = Image.open(io.BytesIO(img_bytes))
                st.image(pil_img, use_container_width=True, caption="Foto asli")

                if st.button("🔍  Analisis Sekarang", use_container_width=True):
                    with st.spinner("Mendeteksi komponen makanan..."):
                        if model_loaded:
                            result = run_yolo_inference(st.session_state.yolo_model, pil_img)
                        else:
                            result = run_dummy_inference(pil_img)

                        # Draw bboxes
                        annotated = draw_detections(pil_img, result["detections"])
                        st.session_state.detection_result = result
                        st.session_state.annotated_image  = annotated

                        # Add to history
                        new_entry = {
                            "Tanggal":  result["timestamp"][:10],
                            "Skor":     result["score"],
                            "Kategori": result["category"],
                        }
                        st.session_state.report_history = [new_entry] + st.session_state.report_history
                    st.rerun()

            # Show annotated image if result exists
            if st.session_state.annotated_image is not None:
                st.markdown('<div style="margin-top:1rem; font-size:0.82rem; color:#888;">Hasil deteksi:</div>', unsafe_allow_html=True)
                st.image(st.session_state.annotated_image, use_container_width=True, caption="Bounding box deteksi")

        with col_res:
            st.markdown('<div class="section-header">Hasil Analisis</div>', unsafe_allow_html=True)
            result = st.session_state.detection_result

            if result:
                sc    = result["score"]
                cat   = result["category"]
                col_c = score_color(sc)

                st.markdown(f"""
                <div class="score-container">
                    <div>
                        <div class="score-label">Skor Kualitas Menu</div>
                        <div class="score-number" style="color:{col_c}">{sc}</div>
                        <div style="font-size:0.75rem; color:#888;">/100</div>
                    </div>
                    <div>
                        <div class="score-category">{cat}</div>
                        <div style="font-size:0.8rem; color:#888; margin-top:4px;">{result['timestamp']}</div>
                        <div style="font-size:0.75rem; color:#666; margin-top:4px;">
                            {result['n_detected']} objek terdeteksi
                            {'· YOLOv8 real' if model_loaded else '· mode simulasi'}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div style="margin-top:1.25rem;"></div>', unsafe_allow_html=True)

                # Component tags
                tags_html = '<div class="food-tags">'
                for name, info in result["components"].items():
                    if info["status"] == "terdeteksi" and info["porsi"] == "cukup":
                        cls, label = "tag-ok",  f"✓ {name}"
                    elif info["status"] == "terdeteksi":
                        cls, label = "tag-warn", f"△ {name} ({info['porsi']})"
                    else:
                        cls, label = "tag-bad",  f"✗ {name}"
                    tags_html += f'<span class="food-tag {cls}">{label}</span>'
                tags_html += "</div>"
                st.markdown(tags_html, unsafe_allow_html=True)

                st.markdown('<div style="margin-top:1.25rem;"></div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-box">
                        <span class="metric-val">{result['kalori']}</span>
                        <span class="metric-lbl">Kalori (kkal)</span>
                    </div>
                    <div class="metric-box">
                        <span class="metric-val">{result['protein_g']}g</span>
                        <span class="metric-lbl">Protein</span>
                    </div>
                    <div class="metric-box">
                        <span class="metric-val">{sum(1 for v in result['components'].values() if v['status']=='terdeteksi')}/5</span>
                        <span class="metric-lbl">Komponen</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if result["kurang"]:
                    st.markdown(f"""
                    <div class="custom-alert alert-warn">
                        ⚠️ <strong>Perlu perbaikan:</strong> {', '.join(result['kurang'])}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="custom-alert alert-good">
                        ✅ Menu lengkap! Semua komponen 4 sehat 5 sempurna terdeteksi.
                    </div>
                    """, unsafe_allow_html=True)

                rekomendasi = (
                    "Menu sudah memiliki beberapa komponen utama, tetapi perlu perbaikan pada komponen yang belum ada atau porsinya masih kecil."
                    if result["kurang"] else
                    "Menu hari ini sudah memenuhi standar gizi MBG. Pertahankan!"
                )
                st.markdown(f"""
                <div style="font-size:0.88rem; color:#555; margin-top:0.5rem;">
                    <strong>Rekomendasi:</strong> {rekomendasi}
                </div>
                """, unsafe_allow_html=True)

                # Detection details (expandable)
                if result["detections"]:
                    with st.expander("Detail deteksi per objek"):
                        for det in result["detections"]:
                            conf_pct = int(det['conf'] * 100)
                            st.markdown(f"- **{det['label']}** — confidence {conf_pct}%")
            else:
                st.markdown("""
                <div style="padding:3rem 0; text-align:center; color:#bbb; font-size:0.95rem;">
                    Unggah foto makanan untuk melihat<br>hasil analisis di sini.
                </div>
                """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────
    # TAB 2 — History & Chart
    # ────────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Grafik Performa MBG</div>', unsafe_allow_html=True)

        if history:
            df = pd.DataFrame(history)
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])
            df = df.sort_values("Tanggal")

            avg_score     = int(df["Skor"].mean())
            max_score     = int(df["Skor"].max())
            min_score     = int(df["Skor"].min())
            total_reports = len(df)

            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-box"><span class="metric-val">{avg_score}</span><span class="metric-lbl">Rata-rata Skor</span></div>
                <div class="metric-box"><span class="metric-val">{max_score}</span><span class="metric-lbl">Skor Tertinggi</span></div>
                <div class="metric-box"><span class="metric-val">{min_score}</span><span class="metric-lbl">Skor Terendah</span></div>
                <div class="metric-box"><span class="metric-val">{total_reports}</span><span class="metric-lbl">Total Laporan</span></div>
            </div>
            """, unsafe_allow_html=True)

            chart_df = df[["Tanggal", "Skor"]].set_index("Tanggal")
            st.line_chart(chart_df, height=280, use_container_width=True)

            st.markdown('<div class="section-header">Riwayat Laporan</div>', unsafe_allow_html=True)
            recent = df.sort_values("Tanggal", ascending=False).head(10)
            for _, row in recent.iterrows():
                sc      = row["Skor"]
                col_dot = score_color(sc)
                date_str = row["Tanggal"].strftime("%d %b %Y")
                cat      = row["Kategori"]
                st.markdown(f"""
                <div class="history-item">
                    <div>
                        <div class="history-date">{date_str}</div>
                        <div style="font-size:0.88rem; color:#555;">{cat}</div>
                    </div>
                    <div class="history-score" style="color:{col_dot}">{sc}<span style="font-size:0.9rem;color:#bbb;font-family:'DM Sans';">/100</span></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada riwayat laporan.")

    # ────────────────────────────────────────────────────────────────────
    # TAB 3 — Report
    # ────────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Laporan Otomatis</div>', unsafe_allow_html=True)
        result    = st.session_state.detection_result
        today_str = datetime.now().strftime("%Y-%m-%d")

        if result:
            report_text = f"""LAPORAN HARIAN KUALITAS MENU MBG
{"="*40}

Identitas Sekolah
- Nama Sekolah  : {nama}
- NPSN          : {npsn}
- Alamat        : {alamat}
- Kota/Provinsi : {kota}
- Tanggal       : {today_str}

Hasil Deteksi Komponen Menu
"""
            for comp, info in result["components"].items():
                report_text += f"- {comp}: {info['status']}, porsi {info['porsi']}\n"

            report_text += f"""
Jumlah Objek Terdeteksi : {result['n_detected']}
Metode Deteksi          : {'YOLOv8 (' + st.session_state.model_name + ')' if st.session_state.yolo_model else 'Simulasi'}

Estimasi Gizi
- Kalori  : {result['kalori']} kkal
- Protein : {result['protein_g']} gram

Skor Kualitas Menu : {result['score']}/100
Kategori           : {result['category']}

Catatan
Porsi yang terlihat kurang: {', '.join(result['kurang']) if result['kurang'] else 'Semua porsi cukup'}

Rekomendasi
{"Menu sudah memiliki beberapa komponen utama, tetapi perlu perbaikan pada komponen yang belum ada atau porsinya masih kecil." if result['kurang'] else "Menu hari ini sudah memenuhi standar gizi MBG. Pertahankan kualitas ini!"}

Laporan dibuat otomatis oleh Nutriport — {datetime.now().strftime("%d %B %Y, %H:%M")}
"""
            st.markdown(f'<div class="report-box"><pre style="font-family:\'DM Sans\',sans-serif;font-size:0.85rem;white-space:pre-wrap;margin:0;">{report_text}</pre></div>', unsafe_allow_html=True)

            col_dl = st.columns([2, 1, 2])[1]
            with col_dl:
                st.download_button(
                    "⬇  Unduh Laporan",
                    data=report_text,
                    file_name=f"laporan_mbg_{npsn}_{today_str}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            st.markdown(f"""
            <div style="text-align:center; margin-top:1rem; font-size:0.82rem; color:#aaa;">
                Sudah melakukan laporan sekolah <strong>{nama}</strong> di tanggal {today_str}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="padding:2.5rem; text-align:center; color:#bbb;">
                Analisis foto makanan terlebih dahulu<br>untuk menghasilkan laporan otomatis.
            </div>
            """, unsafe_allow_html=True)


# ── ROUTER ────────────────────────────────────────────────────────────────────
if st.session_state.school_data is None:
    page_login()
else:
    page_dashboard()
