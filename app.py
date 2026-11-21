import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="BioGen-Physiology Engine | Advanced Vascular Simulation",
    page_icon="🩺",
    layout="wide"
)

# تنسيق الواجهة لدعم العربية (RTL) والبطاقات الإكلينيكية
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, sans-serif; }
    h1, h2, h3, p, label, .stMarkdown { text-align: right !important; }
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: 800; color: #0f766e; }
    .tissue-box {
        background-color: #f0fdfa;
        border-right: 5px solid #0d9488;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 12px 0;
        color: #115e59;
        font-size: 14px;
    }
    .status-optimal {
        background: linear-gradient(135deg, #0f766e 0%, #059669 100%);
        color: white;
        padding: 16px;
        border-radius: 14px;
        margin-top: 10px;
    }
    .status-balanced {
        background: linear-gradient(135deg, #0369a1 0%, #0f766e 100%);
        color: white;
        padding: 16px;
        border-radius: 14px;
        margin-top: 10px;
    }
    .status-critical {
        background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
        color: white;
        padding: 16px;
        border-radius: 14px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# قاعدة البيانات الفسيولوجية المطابقة لنسختكِ الأخيرة
TISSUE_PROFILES = {
    "الجلد والأنسجة الوعائية الدقيقة (Skin & Micro-vasculature)": {
        "baseResistance": 1.0,
        "bpExponent": 1.0,
        "permWeight": 1.0,
        "radiusSensitivity": 0.045,
        "o2Demand": 1.0,
        "desc": "تنظيم ذاتي متوازن؛ يعتمد على سلامة الشبكة الشعرية السطحية."
    },
    "الأوعية الدقيقة لعضلة القلب (Myocardial Micro-vasculature)": {
        "baseResistance": 0.85,
        "bpExponent": 1.25,
        "permWeight": 0.9,
        "radiusSensitivity": 0.065,
        "o2Demand": 1.35,
        "desc": "طلب أيضي مرتفع وحساسية شديدة لهبوط الضغط الشرياني وارتفاع اللزوجة."
    },
    "سقالة تجديد الأدمة البيولوجية (Bio-Dermal Scaffold)": {
        "baseResistance": 1.15,
        "bpExponent": 0.85,
        "permWeight": 1.45,
        "radiusSensitivity": 0.035,
        "o2Demand": 0.85,
        "desc": "بيئة هندسية حيوية؛ تعتمد كفاءتها بشكل رئيسي على نفاذية الشعيرات لتعزيز التوعية."
    },
    "سرير الجرح الإقفاري (Ischemic Wound Bed)": {
        "baseResistance": 1.65,
        "bpExponent": 1.15,
        "permWeight": 0.75,
        "radiusSensitivity": 0.075,
        "o2Demand": 1.15,
        "desc": "نسيج متضرر يعاني من ارتفاع المقاومة الوعائية وضعف الاستجابة التعويضية."
    }
}

def compute_perfusion(bp_val, radius, vis, perm, ox, profile):
    resistance = profile["baseResistance"] * (
        1 + radius * profile["radiusSensitivity"] * ((vis / 3.2) ** 1.2)
    )
    pressure_factor = ((bp_val / 100.0) ** profile["bpExponent"]) * 100.0
    ox_factor = (ox / 95.0) ** profile["o2Demand"]
    perm_factor = perm ** profile["permWeight"]

    raw_score = (pressure_factor * ox_factor * perm_factor) / (resistance * 2.45)
    eff = max(8.0, min(99.2, raw_score))
    oxy_delivery = min(100.0, (eff * (ox / 100.0)) / profile["o2Demand"])
    return round(eff, 2), round(resistance, 2), round(oxy_delivery, 1)

# تهيئة القيم الافتراضية
if "bp" not in st.session_state:
    st.session_state.update({"bp": 115, "radius": 20.0, "vis": 3.5, "perm": 1.2, "ox": 97})

def set_preset(bp_v, rad_v, vis_v, perm_v, ox_v):
    st.session_state.bp = bp_v
    st.session_state.radius = rad_v
    st.session_state.vis = vis_v
    st.session_state.perm = perm_v
    st.session_state.ox = ox_v

st.title("🩺 BioGen-Physiology Engine")
st.caption("محرك المحاكاة الفسيولوجية للأنسجة والأوعية الدقيقة (نموذج متعدد الخصائص)")

# أزرار الحالات السريعة
p1, p2, p3, _ = st.columns([1, 1, 1, 2.5])
p1.button("✨ تروية مثالية", on_click=set_preset, args=(120, 8.0, 3.0, 1.8, 99), use_container_width=True)
p2.button("⚖️ حالة قياسية", on_click=set_preset, args=(115, 20.0, 3.5, 1.2, 97), use_container_width=True)
p3.button("⚠️ صدمة إقفارية", on_click=set_preset, args=(68, 35.0, 5.2, 0.7, 83), use_container_width=True)

st.divider()

col_inputs, col_outputs = st.columns([1.15, 1], gap="large")

with col_inputs:
    st.subheader("🎛️ المتغيرات الفيزيائية والحيوية")
    tissue_name = st.selectbox("نوع النسيج المستهدف", list(TISSUE_PROFILES.keys()))
    bp = st.slider("ضغط الدم الشرياني (MAP - mmHg)", 60, 200, key="bp")
    radius = st.slider("نصف قطر الجرح / الآفة (mm)", 2.0, 50.0, step=0.5, key="radius")
    vis = st.slider("لزوجة الدم (Viscosity - cP)", 1.5, 6.0, step=0.1, key="vis")
    perm = st.slider("نفاذية الشعيرات (Permeability)", 0.5, 3.0, step=0.1, key="perm")
    ox = st.slider("مستوى الأكسجة (SpO2 %)", 70, 100, key="ox")

profile = TISSUE_PROFILES[tissue_name]
eff, resistance, oxy_delivery = compute_perfusion(bp, radius, vis, perm, ox, profile)

with col_outputs:
    st.subheader("📊 التحليل الإكلينيكي اللحظي")
    k1, k2, k3 = st.columns(3)
    k1.metric("كفاءة التروية الوعائية", f"{eff}%")
    k2.metric("مقاومة التدفق", f"{resistance} PRU")
    k3.metric("توصيل الأكسجين", f"{oxy_delivery}%")

    st.progress(int(eff))

    if eff >= 52:
        badge_text = "تدفق مثالي (Optimal Perfusion)"
        clinical_status = f"كفاءة تروية ممتازة لنسيج ({tissue_name})؛ الإمداد الأكسجيني يلبي المتطلبات الأيضية بالكامل."
        st.markdown(f'<div class="status-optimal"><strong>✅ {badge_text}</strong><br>{clinical_status}</div>', unsafe_allow_html=True)
    elif eff >= 30:
        badge_text = "تروية متوازنة (Balanced Range)"
        clinical_status = "تروية مستقرة ضمن النطاق المقبول؛ يُنصح بمراقبة اللزوجة ونفاذية الشعيرات للحفاظ على التوازن."
        st.markdown(f'<div class="status-balanced"><strong>⚖️ {badge_text}</strong><br>{clinical_status}</div>', unsafe_allow_html=True)
    else:
        badge_text = "خطر إقفار حرج (Critical Ischemia)"
        clinical_status = f"تحذير إكلينيكي: قصور حاد في تروية ({tissue_name}) نتيجة ارتفاع المقاومة الوعائية أو نقص الضغط/الأكسجة."
        st.markdown(f'<div class="status-critical"><strong>🚨 {badge_text}</strong><br>{clinical_status}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="tissue-box"><strong>خصائص النسيج:</strong> {profile["desc"]}</div>', unsafe_allow_html=True)

    report_text = (
        f"========================================================\n"
        f"    BIOGEN-PHYSIOLOGY ENGINE - CLINICAL AI REPORT       \n"
        f"========================================================\n"
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Target Tissue: {tissue_name}\n"
        f"--------------------------------------------------------\n"
        f"[Physiological Inputs]\n"
        f"- Arterial Pressure (MAP): {bp} mmHg\n"
        f"- Lesion / Wound Radius: {radius} mm\n"
        f"- Blood Viscosity: {vis} cP\n"
        f"- Capillary Permeability: {perm}\n"
        f"- Baseline SpO2: {ox} %\n"
        f"--------------------------------------------------------\n"
        f"[Tissue-Specific Simulation Outputs]\n"
        f"- Vascular Perfusion Efficiency: {eff}%\n"
        f"- Tissue Vascular Resistance: {resistance} PRU\n"
        f"- Net Oxygen Delivery: {oxy_delivery}%\n"
        f"--------------------------------------------------------\n"
        f"Clinical Assessment ({badge_text}):\n{clinical_status}\n"
        f"========================================================"
    )

    st.download_button(
        label="📥 تحميل التقرير الإكلينيكي الشامل (TXT)",
        data=report_text,
        file_name="BioGen_Physiology_Report.txt",
        mime="text/plain",
        use_container_width=True
    )

# الرسم البياني التفاعلي لاستجابة النسيج لتغير الضغط
st.subheader(f"📈 استجابة التروية في ({tissue_name})")
steps = [60, 90, 120, 150, 180, 200]
trend = [compute_perfusion(v, radius, vis, perm, ox, profile)[0] for v in steps]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[f"{v} mmHg" for v in steps],
    y=trend,
    mode="lines+markers",
    name=tissue_name,
    line=dict(color="#0d9488", width=3),
    marker=dict(size=8, color="#0f766e"),
    fill="tozeroy",
    fillcolor="rgba(13, 148, 136, 0.12)"
))
fig.update_layout(
    yaxis=dict(range=[0, 100], title="كفاءة التروية (%)"),
    xaxis=dict(title="ضغط الدم الشرياني (MAP)"),
    height=330,
    margin=dict(t=20, b=30, l=20, r=20)
)
st.plotly_chart(fig, use_container_width=True)
