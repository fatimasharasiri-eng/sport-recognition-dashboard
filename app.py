import base64
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
try:
    from scipy.stats import gaussian_kde
except ImportError:
    gaussian_kde = None

from theme import apply_theme


# Page Configuration


st.set_page_config(
    page_title="Sports Exercise Recognition",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Constants & Colors


ACTIVITY = "activity_label"
HR = "heart_rate"

SENSOR_GROUPS = {
    "Wrist Accelerometer": ["wrist_acc_x", "wrist_acc_y", "wrist_acc_z"],
    "Wrist Gyroscope": ["wrist_gyro_x", "wrist_gyro_y", "wrist_gyro_z"],
    "Waist Accelerometer": ["waist_acc_x", "waist_acc_y", "waist_acc_z"],
    "Waist Gyroscope": ["waist_gyro_x", "waist_gyro_y", "waist_gyro_z"],
}
ALL_SENSORS = [c for cols in SENSOR_GROUPS.values() for c in cols]

PURPLE, PURPLE_D = "#5623AE", "#2A0F5C"
GREEN, GREEN_D = "#5DA973", "#1E4A2C"
YELLOW = "#F7E38B"
PALETTE = [PURPLE, GREEN, YELLOW, "#B390F9", "#63A872", "#F3DC84"]

# Paste the original dataset webpage URL here when available.
DATASET_URL = "PASTE_DATASET_URL_HERE"

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = PALETTE
px.defaults.color_continuous_scale = "Viridis"


# Styling (new design: see theme.py)


apply_theme()


# Stickers  


STICKERS = [
    ("assets/sticker-dumbbell.png",  "top:4%;left:-34px",    110, -10),
    ("assets/sticker-stopwatch.png", "top:20%;right:-34px",  100,   8),
    ("assets/sticker-ball.png",      "bottom:6%;left:-30px",  95,   0),
]


TEST_STICKERS = [
    ("assets/sticker-ball.png",  "top:46%;left:-30px",   95,   0),
    ("assets/sticker-shoe2.png", "top:74%;right:-34px", 115,  -8),

]
PREDICTION_STICKERS = [
    ("assets/sticker-tennis.png",  "top:8%;left:-34px",    105, -10),
    ("assets/sticker-soccer.png", "top:42%;right:-34px",  100,   8),
    ("assets/water.png",  "bottom:6%;left:-30px",  95,    0),
]
jump_CARD  = ("assets/sticker-jump.png",  "top:-30px;left:-16px", 100, 30)    
HEART_CARD = ("assets/heartbeat.png", "top:-26px;right:-10px",  58,  8)    

st.markdown("""
<style>
.sticker { z-index: 5; pointer-events: none; filter: drop-shadow(0 4px 6px rgba(0,0,0,.18)); }


""", unsafe_allow_html=True)


def _b64(path):
    p = Path(__file__).parent / path
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


def sticker_html(items, mode="fixed"):
    html = ""
    for f, pos, w, rot in items:
        b = _b64(f)
        if b:
            ext = Path(f).suffix.lstrip(".").lower()
            mime = {"jpg": "jpeg", "svg": "svg+xml"}.get(ext, ext)
            html += (f'<img class="sticker" src="data:image/{mime};base64,{b}" alt="" '
                     f'style="position:{mode};{pos};width:{w}px;transform:rotate({rot}deg);'
                     f'pointer-events:none;z-index:5;">')
    return html


def card_sticker(spec):
    return sticker_html([spec], mode="absolute")


def sticker_layer(items):
    html = sticker_html(items)
    if html:
        st.markdown(html, unsafe_allow_html=True)


# Sticker layer
if st.session_state.get("page") == "Test":
    sticker_layer(PREDICTION_STICKERS)
else:
    sticker_layer(STICKERS)


# Load Data
@st.cache_data
def load_data():

    subject_df = pd.read_csv("data/Subject_Information.csv")
    raw_df = pd.read_csv("data/Sensor_Data.csv")

    subject_df.columns = subject_df.columns.astype(str).str.strip()
    raw_df.columns = raw_df.columns.astype(str).str.strip()

    clean_df = raw_df.drop_duplicates().dropna(subset=[HR] + ALL_SENSORS)

    df = clean_df.merge(
        subject_df,
        left_on="subject_id",
        right_on="Subject_ID",
        how="left"
    ).drop(columns=["Subject_ID"])

    df["Age_Group"] = pd.cut(df["Age"], bins=[0, 25, 35], labels=["Young", "Adult"])

    return subject_df, raw_df, df

try:
    subject_df, raw_df, df = load_data()

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# UI helpers

def section(letter, title, right=""):
    st.markdown(
        f'<div class="sec"><span class="badge">{letter}</span>'
        f'<span class="sec-title">{title}</span>'
        f'<span class="line"></span>'
        f'<span class="sec-right">{right}</span></div>',
        unsafe_allow_html=True
    )


def card_title(title, sub=""):
    st.markdown(
        f'<div class="ctitle"><div class="ct">{title}</div><div class="cs">{sub}</div></div>',
        unsafe_allow_html=True
    )


def metric_strip(items):
    cells = "".join(
        f'<div class="mcell"><div class="mtop"><span class="mlabel">{label}</span>'
        f'<span class="micon">{icon}</span></div>'
        f'<div class="mval">{value}</div><div class="msub">{sub}</div>'
        f'<div class="mbar" style="background:{color}"></div></div>'
        for label, value, sub, icon, color in items
    )
    return f'<div class="mstrip">{cells}</div>'


def metric_card(label, value, sub, icon, color):
    return (
        f'<div class="mcard"><div class="mtop"><span class="mlabel">{label}</span>'
        f'<span class="micon">{icon}</span></div>'
        f'<div class="mval">{value}</div><div class="msub">{sub}</div>'
        f'<div class="mbar" style="background:{color}"></div></div>'
    )


def plot_style(fig, height, title=""):
    fig.update_layout(
        title=title or None,
        height=height,
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Archivo, sans-serif", size=12, color="#16112B"),
    )
    fig.update_xaxes(gridcolor="#EEEAF3", zeroline=False)
    fig.update_yaxes(gridcolor="#EEEAF3", zeroline=False)
    return fig


def selected_points(event):
    try:
        return event["selection"]["points"]
    except Exception:
        return []


# Interactive chart helpers


def hist_chart(data, col, key, title="", bins=20, color=PURPLE, line=PURPLE_D, height=300):
    """Histogram + KDE. Click a bar to see if it is a peak, slope or tail."""
    values = data[col].dropna().to_numpy()
    counts, edges = np.histogram(values, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    width = edges[1] - edges[0]

    fig = go.Figure()
    fig.add_bar(
        x=centers, y=counts, width=width, opacity=0.88,
        marker_color=color, marker_line_color="white", marker_line_width=1,
        hovertemplate=f"{col}: %{{x:.2f}}<br>Count: %{{y:,}}<extra></extra>"
    )

    if gaussian_kde is not None and len(values) > 2 and values.std() > 0:
        sample = values
        if len(values) > 5000:
            sample = np.random.default_rng(42).choice(values, 5000, replace=False)
        xs = np.linspace(values.min(), values.max(), 200)
        ys = gaussian_kde(sample)(xs) * len(values) * width
        fig.add_scatter(x=xs, y=ys, mode="lines",
                        line=dict(color=line, width=2.5), hoverinfo="skip")

    fig.update_layout(showlegend=False, bargap=0, xaxis_title=col, yaxis_title="Count")
    plot_style(fig, height, title)

    event = st.plotly_chart(fig, use_container_width=True, key=key,
                            on_select="rerun", selection_mode="points")

    pts = [p for p in selected_points(event) if p.get("curve_number", 0) == 0]
    if not pts:
        return

    i = pts[0].get("point_index", pts[0].get("point_number"))
    c = counts[i]
    left = counts[i - 1] if i > 0 else -1
    right = counts[i + 1] if i < len(counts) - 1 else -1

    if c == counts.max():
        kind = "the **highest peak** (most common range)"
    elif c > left and c > right:
        kind = "a **local peak**"
    elif c <= 0.1 * counts.max() and (i <= 1 or i >= len(counts) - 2):
        kind = "a **tail** (very few records, possible outliers)"
    else:
        kind = "a **slope** (between a peak and a tail)"

    st.info(f"**{col}: {edges[i]:.2f} – {edges[i + 1]:.2f}** → "
            f"{c:,} records ({c / len(values) * 100:.1f}%). This is {kind}.")


def box_chart(data, value, key, title="", group=None, horizontal=False,
              color=PURPLE, height=300):
    """Boxplot. Click a point to see if it is an outlier."""
    kw = dict(points="outliers")
    if group:
        kw["color"] = group
        if horizontal:
            kw.update(x=value, y=group, orientation="h")
        else:
            kw.update(x=group, y=value)
    else:
        kw["x" if horizontal else "y"] = value
        kw["color_discrete_sequence"] = [color]

    fig = px.box(data, **kw)
    fig.update_layout(showlegend=False)
    if group and horizontal:
        fig.update_yaxes(autorange="reversed")
    plot_style(fig, height, title)

    event = st.plotly_chart(fig, use_container_width=True, key=key,
                            on_select="rerun", selection_mode="points")

    pts = selected_points(event)
    if not pts:
        return

    p = pts[0]
    val = p["x"] if horizontal else p["y"]
    g = (p.get("y") if horizontal else p.get("x")) if group else None

    s = (data.loc[data[group] == g, value] if group else data[value]).dropna()
    q1, med, q3 = s.quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    name = f"{g} – " if g is not None else ""

    if val > hi:
        st.warning(f"{name}**{val:.2f}** is an **outlier**, above the upper limit ({hi:.2f}). Median = {med:.2f}.")
    elif val < lo:
        st.warning(f"{name}**{val:.2f}** is an **outlier**, below the lower limit ({lo:.2f}). Median = {med:.2f}.")
    else:
        st.info(f"{name}**{val:.2f}** is **within the normal range** ({lo:.2f} – {hi:.2f}). Median = {med:.2f}.")


def show_bar(fig, data, y, key, unit, dec=0, overall=None, has_color=False):
    """Show a bar chart. Click a bar to see if it is highest / lowest."""
    event = st.plotly_chart(fig, use_container_width=True, key=key,
                            on_select="rerun", selection_mode="points")

    pts = selected_points(event)
    if not pts:
        return

    p = pts[0]
    name = str(p.get("x"))
    if has_color:
        name += f" / {fig.data[p['curve_number']].name}"
    val = p["y"]

    if val >= data[y].max():
        rank = "the **highest** bar in this chart"
    elif val <= data[y].min():
        rank = "the **lowest** bar in this chart"
    else:
        rank = "in the **middle range** of this chart"

    msg = f"**{name}**: {val:,.{dec}f} {unit} — {rank}."
    if overall is not None:
        diff = val - overall
        direction = "above" if diff > 0 else "below"
        msg += f" It is {abs(diff):.1f} BPM {direction} the overall average ({overall:.1f})."
    st.info(msg)


def count_bar(data, x, key, unit, title=""):
    fig = px.bar(data, x=x, y="Count", color=x, text="Count")
    fig.update_layout(showlegend=False)
    plot_style(fig, 300, title)
    show_bar(fig, data, "Count", key, unit)


def mean_bar(data, x, key, title="", color=None):
    cols = [x] + ([color] if color else [])
    g = data.groupby(cols, observed=True)[HR].mean().reset_index()
    fig = px.bar(g, x=x, y=HR, color=color or x, barmode="group", text_auto=".1f",
                 labels={HR: "Average Heart Rate (BPM)"},
                 color_discrete_sequence=PALETTE)   
    if not color:
        fig.update_layout(showlegend=False)
    plot_style(fig, 320, title)
    show_bar(fig, g, HR, key, "BPM", dec=1, overall=data[HR].mean(), has_color=bool(color))



def insight_box(title, bullets):
    """Expandable manual conclusions. Edit the text in each insight_box call below."""
    with st.expander(f"💡 View insights ", expanded=False):
        for bullet in bullets:
            st.markdown(f"- {bullet}")



# Nav + Hero


dataset_link_html = (
    f'<a class="dataset-link" href="{DATASET_URL}" target="_blank" rel="noopener noreferrer">Open dataset ↗</a>'
    if DATASET_URL != "PASTE_DATASET_URL_HERE"
    else '<span class="dataset-link">Dataset link: https://www.scidb.cn/en/s/MvmE7z</span>'
)

hero_art = _b64("assets/hero_art.png")
hero_art_html = (
    f'<div class="hero-art"><img src="data:image/png;base64,{hero_art}" alt=""></div>'
    if hero_art else ""
)

HERO_CSS = """
<style>
.hero-wrap { padding:0 !important; gap:0 !important; flex-wrap:nowrap !important; align-items:stretch !important; }
.hero-left { flex:1 1 56% !important; min-width:0; padding:36px 2px 34px !important; }
.hero-title { font-family:'Archivo Black','Archivo',sans-serif; text-transform:uppercase; font-weight:400;
              font-size:clamp(36px,5.6vw,72px); line-height:1.02; letter-spacing:-.01em; color:#16112B; }
.hero-title span { display:block; width:fit-content; color:#16112B; -webkit-text-fill-color:#16112B; }
.hero-title span.accent { color:#5623AE; -webkit-text-fill-color:#5623AE; }
.hero-title span.hl { padding-right:.08em; background-image:linear-gradient(transparent 76%, #F4CE23 76%); }
.hero-link { margin-top:22px; }
.hero-art { flex:0 0 44%; display:flex; background:#EBE3FC; }
.hero-art img { width:100%; height:100%; object-fit:cover; object-position:center; display:block; }
@media (max-width:820px) { .hero-art { display:none; } .hero-left { padding:26px 22px !important; } }
</style>
"""

st.markdown(HERO_CSS + f"""
<div class="topbar">
  <span class="tag">ANALYTICS DASHBOARD</span>
</div>
<div class="hero-wrap">
  <div class="hero-left">
    <div class="hero-title"><span>Sports</span><span class="accent">Exercise</span><span class="hl">Recognition</span></div>
<div class="subtitle" style="font-family: 'Poppins', sans-serif;">
    Analyze wearable sensor data to recognize physical activities and explore estimating physical exertion levels using Machine Learning.
</div>
<div class="hero-link">{dataset_link_html}</div>
  </div>
  {hero_art_html}
</div>
""", unsafe_allow_html=True)

st.markdown(metric_strip([
    ("Total Subjects", f"{len(subject_df):,}", "Participants", "👥", GREEN),
    ("Number of Activities", f"{df[ACTIVITY].nunique()}", "Movement types", "⚡", PURPLE_D),
    ("Data Sources", "2", "Wrist and waist sensors", "📡", PURPLE),
]), unsafe_allow_html=True)

# Page switch: Analysis / Test


if "page" not in st.session_state:
    st.session_state.page = "Analysis"


def set_page(p):
    st.session_state.page = p
    st.session_state.pop("act_result", None)


page = st.session_state.page

if "view" not in st.session_state:
    st.session_state.view = "Before"


def set_view(v):
    st.session_state.view = v


view = st.session_state.view

pg1, pg2, _ = st.columns([1, 1.5, 4.5])
pg1.button("Analysis", on_click=set_page, args=("Analysis",), key="btn_page_analysis",
           type="primary" if page == "Analysis" else "secondary", use_container_width=True)
pg2.button("Model Prediction", on_click=set_page, args=("Test",), key="btn_page_test",
           type="primary" if page == "Test" else "secondary", use_container_width=True)

if page == "Test":
    import joblib

    T_PURPLE, T_SOFT = "#6B4FB8", "#EDE8F8"

    @st.cache_resource
    def load_activity_model():
        return joblib.load(Path(__file__).parent / "activity_model.pkl")

    try:
        act = load_activity_model()
    except Exception as e:
        st.error(f"Could not load activity_model.pkl: {e}")
        st.stop()
    ACT_MODEL, ACT_SCALER, ACT_FEATURES = act["model"], act["scaler"], act["features"]

    def t_line(s):
        return "".join(line.strip() for line in s.splitlines())

    def t_med(c):
        return round(float(df[c].median()), 2)

    def t_range(c):
        lo = float(np.floor(df[c].min() * 100) / 100)
        hi = float(np.ceil(df[c].max() * 100) / 100)
        step = max(round((hi - lo) / 100, 2), 0.01)
        return lo, hi, step

    def t_axes(title, loc, kind, label, unit):
        return (title, [(f"{loc}_{kind}_{a}", f"{a.upper()}-axis {label}", unit,
                         t_med(f"{loc}_{kind}_{a}")) for a in "xyz"])

    T_GROUPS = [
        t_axes("WRIST · ACCELEROMETER", "wrist", "acc", "acceleration", "m/s²"),
        t_axes("WRIST · GYROSCOPE", "wrist", "gyro", "angular velocity", "rad/s"),
        t_axes("WAIST · ACCELEROMETER", "waist", "acc", "acceleration", "m/s²"),
        t_axes("WAIST · GYROSCOPE", "waist", "gyro", "angular velocity", "rad/s"),
        ("HEART RATE", [("heart_rate", "Heart rate", "bpm", t_med("heart_rate"))]),
    ]
    T_DEFAULTS = {f"act_{k}": v for _, items in T_GROUPS for k, _, _, v in items}

    def reset_act_inputs():
        for k, v in T_DEFAULTS.items():
            st.session_state[k] = v
        st.session_state.pop("act_result", None)

    def predict_activity(vals):
        X = pd.DataFrame([vals])[ACT_FEATURES]
        proba = ACT_MODEL.predict_proba(ACT_SCALER.transform(X))[0]
        return dict(zip(ACT_MODEL.classes_, proba))

    for k, v in T_DEFAULTS.items():
        st.session_state.setdefault(k, v)

    # ---------- Effort model ----------
    @st.cache_resource
    def load_effort_model():
        return joblib.load(Path(__file__).parent / "effort_model.pkl")

    try:
        eff = load_effort_model()
    except Exception as e:
        st.error(f"Could not load effort_model.pkl: {e}")
        st.stop()
    EFF_MODEL, EFF_FEATURES = eff["model"], eff["features"]
    EFF_SENSORS = [c for c in EFF_FEATURES if c != "activity_label"]
    EFF_GREEN_SOFT, EFF_GREEN_TXT = "#E6F2E6", "#2F6B3A"

    def current_activity():
        r = st.session_state.get("act_result")
        return (max(r, key=r.get), r[max(r, key=r.get)]) if r else (None, None)

    def predict_effort():
        name, _ = current_activity()
        if name is None:
            return
        row = {c: float(st.session_state[f"act_{c}"]) for c in EFF_SENSORS}
        row["activity_label"] = str(name)
        proba = EFF_MODEL.predict_proba(pd.DataFrame([row])[EFF_FEATURES])[0]
        st.session_state["eff_result"] = {
            "inputs": row,
            "probs": {str(k): float(p) for k, p in zip(EFF_MODEL.classes_, proba)},
        }

    # Intro 

    st.button("Reset sample ↺", key="act_reset_top", on_click=reset_act_inputs)
    section("A", "Exercise Type Prediction", "SENSOR READING")

    col_in, col_out = st.columns([1.5, 1], gap="large")

    # Inputs 
    with col_in:
        with st.container(border=True):
            card_title("Sensor data", "Edit the values of a single sensor reading.")

            for group_title, items in T_GROUPS:
                st.markdown(
                    f"<div style='font-size:.65rem;letter-spacing:.08em;color:#8A7BB0;margin:.9rem 0 .2rem;'>{group_title}</div>",
                    unsafe_allow_html=True)
                cols = st.columns(3)
                for c, (k, label, unit, _) in zip(cols, items):
                    lo, hi, stp = t_range(k)
                    v = float(st.session_state[f"act_{k}"])
                    pct = 0.0 if hi == lo else max(0.0, min(100.0, (v - lo) / (hi - lo) * 100))
                    c.markdown(
                        f"<style>.st-key-act_{k} div[style*='linear-gradient']{{"
                        f"background:linear-gradient(to right,#5623AE 0%,#5623AE {pct:.2f}%,"
                        f"#DDD6F0 {pct:.2f}%,#DDD6F0 100%) !important;}}</style>"
                        f"<div class='sl-head'><span class='sl-label'>{label} ({unit})</span>"
                        f"<span class='sl-val'>{v:.2f}</span></div>",
                        unsafe_allow_html=True)
                    c.slider(label, min_value=lo, max_value=hi, step=stp,
                             format="%.2f", key=f"act_{k}", label_visibility="collapsed")

            if st.button("Predict Activity", type="primary", key="act_predict"):
                vals = {k: st.session_state[f"act_{k}"] for _, items in T_GROUPS for k, _, _, _ in items}
                st.session_state["act_result"] = predict_activity(vals)
                st.session_state["eff_activity"] = max(st.session_state["act_result"], key=st.session_state["act_result"].get)

    #  Right column: A result + B effort 
    with col_out:
        # A. Result card (purple)
        result = st.session_state.get("act_result")
        if result:
            ranked = sorted(result.items(), key=lambda kv: kv[1], reverse=True)
            tag = "PREDICTION"
        else:
            ranked = [("Running", .94), ("Jumping", .03), ("Squatting", .01),
                      ("Push-ups", .01), ("Sit-ups", .005), ("Stretching", .005)]
            tag = "EXAMPLE PREDICTION"

        top_name, top_p = ranked[0]
        bars = "".join(f"""
            <div style="display:flex;align-items:center;gap:.6rem;font-size:.75rem;margin:.35rem 0;">
              <span style="width:75px;">{n}</span>
              <div style="flex:1;height:6px;background:#DDD6F0;border-radius:4px;">
                <div style="width:{p*100:.0f}%;height:6px;background:{T_PURPLE};border-radius:4px;"></div></div>
              <span style="width:36px;text-align:right;opacity:.7;">{p*100:.0f}%</span>
            </div>""" for n, p in ranked)

        shoe = card_sticker(jump_CARD)

        st.markdown(t_line(f"""
            <div style="position:relative;background:{T_SOFT};border-radius:16px;padding:1.2rem 1.4rem;color:#2B2740;">
              {shoe}
              <div style="font-size:.65rem;letter-spacing:.08em;color:#8A7BB0;">{tag}</div>
              <div style="background:#fff;border-radius:12px;padding:.8rem 1rem;margin:.6rem 0;">
                <div style="font-size:1.6rem;font-weight:700;">{top_name}</div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:.5rem;">
                <span>Prediction confidence</span><b style="font-size:1.1rem;color:{T_PURPLE};">{top_p*100:.0f}%</b>
              </div>
              {bars}
              <div style="font-size:.7rem;opacity:.65;margin-top:.8rem;">
                Confidence describes the model's classification, not real accuracy.
              </div>
            </div>
        """), unsafe_allow_html=True)

        # B. Exercise Intensity Prediction (green)
        section("B", "Exercise Intensity Prediction")

        act_name, act_conf = current_activity()
        res = st.session_state.get("eff_result") if act_name else None
        heart = card_sticker(HEART_CARD)

        if res:
            cur = {c: float(st.session_state[f"act_{c}"]) for c in EFF_SENSORS}
            cur["activity_label"] = str(act_name)
            stale = res["inputs"] != cur
            probs = res["probs"]
            order = [c for c in ("Low", "High") if c in probs] or list(probs)
            top = max(probs, key=probs.get)
            ebars = "".join(f"""
                <div style="display:flex;align-items:center;gap:.6rem;font-size:.75rem;margin:.35rem 0;">
                  <span style="width:75px;">{n}</span>
                  <div style="flex:1;height:6px;background:#CDE5D0;border-radius:4px;">
                    <div style="width:{probs[n]*100:.0f}%;height:6px;background:{GREEN_D};border-radius:4px;"></div></div>
                  <span style="width:36px;text-align:right;opacity:.7;">{probs[n]*100:.0f}%</span>
                </div>""" for n in order)
            note = ("<div style='font-size:.7rem;opacity:.8;margin-top:.8rem;'>Inputs changed since this estimate. "
                    "Press Predict effort to update it.</div>") if stale else ""
            st.markdown(t_line(f"""
                <div style="position:relative;background:{EFF_GREEN_SOFT};border-radius:16px;padding:1.2rem 1.4rem;
                            color:#1F4D2E;opacity:{.55 if stale else 1};">
                  {heart}
                  <div style="font-size:.65rem;letter-spacing:.08em;color:{EFF_GREEN_TXT};">EFFORT LEVEL</div>
                  <div style="background:#fff;border-radius:12px;padding:.8rem 1rem;margin:.6rem 0;">
                    <div style="font-size:1.6rem;font-weight:700;">{top} effort</div>
                    <div style="font-size:.75rem;opacity:.7;">Activity: {res['inputs']['activity_label']}</div>
                  </div>
                  <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:.5rem;">
                    <span>Model confidence</span><b style="font-size:1.1rem;color:{GREEN_D};">{probs[top]*100:.0f}%</b>
                  </div>
                  {ebars}
                  {note}
                </div>
            """), unsafe_allow_html=True)
        else:
            hint = ("Press Predict effort to estimate the effort level."
                    if act_name else "Press Predict Activity first. Its result is used here.")
            st.markdown(t_line(f"""
                <div style="position:relative;background:{EFF_GREEN_SOFT};border-radius:16px;padding:1.2rem 1.4rem;color:#1F4D2E;">
                  {heart}
                  <div style="font-size:.65rem;letter-spacing:.08em;color:{EFF_GREEN_TXT};">NO PREDICTION YET</div>
                  <div style="background:#fff;border-radius:12px;padding:.8rem 1rem;margin:.6rem 0;">
                    <div style="font-size:1.6rem;font-weight:700;">Low or High effort</div>
                  </div>
                  <div style="font-size:.8rem;opacity:.8;">{hint}</div>
                </div>
            """), unsafe_allow_html=True)

        st.markdown("<div class='eff-marker' style='height:.6rem'></div>", unsafe_allow_html=True)
        st.button("Predict effort", type="primary", key="eff_predict",
                  on_click=predict_effort, disabled=act_name is None,
                  use_container_width=True)

    st.stop()

# =====================================================
# B. Analysis (Before / After toggle)
# =====================================================

st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

v1, v2, _ = st.columns([1, 1, 6])
v1.button("Before", on_click=set_view, args=("Before",), key="btn_before",
          type="primary" if view == "Before" else "secondary", use_container_width=True)
v2.button("After", on_click=set_view, args=("After",), key="btn_after",
          type="primary" if view == "After" else "secondary", use_container_width=True)

# BEFORE: single-variable distributions


if view == "Before":

    st.caption("Each variable on its own:")

    with st.container(border=True):
        card_title("Sensor Histograms", "Accelerometer and gyroscope for wrist and waist")
        group_name = st.radio("Sensor group", list(SENSOR_GROUPS.keys()),
                              horizontal=True, key="hist_group", label_visibility="collapsed")
        cols = st.columns(3)
        for c, col in zip(cols, SENSOR_GROUPS[group_name]):
            with c:
                hist_chart(df, col, key=f"hist_{col}", title=col)
        insight_box(
            "Sensor Histograms",
             [
        "Wrist Accelerometer: X and Y are bimodal and right-skewed; Z has two peaks, mainly at negative values.",
        "Wrist Gyroscope: X is bimodal, Y is right-skewed, and Z is approximately symmetric around zero.",
        "Waist Accelerometer: X and Y are bimodal and right-skewed; Z has two peaks, mainly at negative values.",
        "Waist Gyroscope: X is bimodal, Y is right-skewed, and Z is approximately symmetric around zero.",
    ]
        )

    with st.container(border=True):
        card_title("Heart Rate Histogram", "Distribution of heart rate (BPM)")
        hist_chart(df, HR, key="hist_hr", color=GREEN, line=GREEN_D)
        insight_box(
            "Heart Rate Histogram",
            [ "Most heart rate readings fall between 130 and 145 BPM, with the highest peak around 133 BPM.", "The distribution is multimodal, with smaller peaks at other heart rate levels.", ]
        )

    with st.container(border=True):
        card_title("Subject Boxplots", "Age, weight and height")
        cols = st.columns(3)
        for c, feature in zip(cols, ["Age", "Weight_kg", "Height_cm"]):
            with c:
                box_chart(subject_df, feature, key=f"box_{feature}",
                          title=feature, color=PURPLE if feature != "Weight_kg" else GREEN)
        insight_box(
            "Subject Boxplots",
            [  "Age has two main peaks, around 26–28 and 33–35 years.","Weight is concentrated around 62–70 kg and is slightly right-skewed.", "Height shows two groups, with no clear overall distribution shape." ]
        )

    with st.container(border=True):
        card_title("Count Plots", "Activities, gender and fitness level")

        ac = df[ACTIVITY].value_counts().reset_index()
        ac.columns = ["Activity", "Count"]
        count_bar(ac, "Activity", "count_activity", "records", "Distribution of Activities")

        col1, col2 = st.columns(2)
        with col1:
            gc = subject_df["Gender"].value_counts().reset_index()
            gc.columns = ["Gender", "Count"]
            count_bar(gc, "Gender", "count_gender", "subjects", "Distribution of Gender")
        with col2:
            fc = subject_df["Fitness_Level"].value_counts().reset_index()
            fc.columns = ["Fitness_Level", "Count"]
            count_bar(fc, "Fitness_Level", "count_fitness", "subjects", "Distribution of Fitness Level")
        insight_box(
            "Count Plots",
            [ "Activity records are relatively balanced, with about 310–355 records per activity.", "Males outnumber females (32 vs. 13).", "Fitness levels are relatively balanced, with about 13–18 subjects per level." ]
        )

    st.stop()

# AFTER: relationships + interactive filters

else:

    CORR_FEATURES = {
        "Acc X":  ["wrist_acc_x",  "waist_acc_x"],
        "Acc Y":  ["wrist_acc_y",  "waist_acc_y"],
        "Acc Z":  ["wrist_acc_z",  "waist_acc_z"],
        "Gyro X": ["wrist_gyro_x", "waist_gyro_x"],
        "Gyro Y": ["wrist_gyro_y", "waist_gyro_y"],
        "Gyro Z": ["wrist_gyro_z", "waist_gyro_z"],
        "HR":     [HR],
    }
    SCALE = [[0.0, "#C3D2BC"], [0.35, "#E3EBDF"], [0.5, "#F7F6F4"], [0.75, "#DDD3F0"], [1.0, "#9C84D6"]]
    SENSOR_NAME = {"Acc": "accelerometer", "Gyro": "gyroscope"}

    def one_line(s):
        return "".join(line.strip() for line in s.splitlines())

    def corr_heatmap(corr, height=420):
        labels = list(corr.columns)
        z = corr.values
        fig = go.Figure(go.Heatmap(
            z=z, x=labels, y=labels, zmin=-1, zmax=1,
            colorscale=SCALE, showscale=False, xgap=5, ygap=5,
            hovertemplate="%{y} ↔ %{x}<br>r = %{z:.2f}<extra></extra>",
        ))
        xs = [c for _ in labels for c in labels]
        ys = [r for r in labels for _ in labels]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers", hoverinfo="none", showlegend=False,
            marker=dict(symbol="square", size=54, color="#6B4FB8", opacity=0.01),
            selected=dict(marker=dict(color="#6B4FB8", opacity=0.22)),
            unselected=dict(marker=dict(opacity=0.01)),
        ))
        for i, row in enumerate(labels):
            for j, col in enumerate(labels):
                v = z[i, j]
                fig.add_annotation(x=col, y=row, text=f"{v:.2f}", showarrow=False,
                                   font=dict(size=13, color="#FFFFFF" if v >= 0.6 else "#2B2740"))
        fig.update_layout(
            height=height, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            clickmode="event+select",
            xaxis=dict(side="top", showgrid=False, zeroline=False, fixedrange=True),
            yaxis=dict(autorange="reversed", showgrid=False, zeroline=False, fixedrange=True),
        )
        return fig

    def strongest_pair(corr):
        m = corr.abs().values.copy()
        np.fill_diagonal(m, 0)
        i, j = np.unravel_index(m.argmax(), m.shape)
        return corr.index[i], corr.columns[j]

    def describe_pair(a, b, r):
        if a == b:
            return "Same variable", "A variable is always perfectly correlated with itself."
        ab = abs(r)
        if ab >= 0.9:
            strength, adv = "Very strong", "very strongly"
        elif ab >= 0.7:
            strength, adv = "Strong", "strongly"
        elif ab >= 0.4:
            strength, adv = "Moderate", "moderately"
        elif ab >= 0.2:
            strength, adv = "Weak", "weakly"
        else:
            strength, adv = "Very weak", "very weakly"
        sign = "positively" if r > 0 else "negatively"
        sign_adj = "positive" if r > 0 else "negative"

        if "HR" in (a, b):
            other = b if a == "HR" else a
            if ab < 0.2:
                text = (f"Heart rate has a weak correlation with {other} ({r:+.2f}, below 0.2), indicating that "
                        f"it may provide additional information rather than duplicating the movement sensor readings.")
            elif ab < 0.4:
                text = (f"Heart rate has a weak {sign_adj} correlation with {other} ({r:+.2f}), so it only slightly "
                        f"overlaps with this movement sensor and mostly provides additional information.")
            else:
                text = (f"Heart rate is {adv} {sign} correlated with {other} ({r:+.2f}), so it partly overlaps "
                        f"with movement, but a large part of it is still independent of the sensors.")
        else:
            ta, tb = a.split()[0], b.split()[0]
            cross = (f", even across {SENSOR_NAME[ta]} and {SENSOR_NAME[tb]}"
                     if ta != tb and ab >= 0.7 else "")
            head = f"{a} and {b} are {adv} {sign} correlated ({r:+.2f}){cross}."
            if ab >= 0.7:
                text = f"{head} They carry similar information."
            elif ab >= 0.4:
                text = f"{head} They share some information, but each still adds something of its own."
            else:
                text = f"{head} They are mostly independent, so each gives different information."
        return f"{strength} {sign_adj}", text

    st.caption("Relationships between variables.")

    with st.container(border=True):
        card_title("Heart Rate by Activity", "Median, interquartile range and 1.5×IQR whiskers")
        box_chart(df, HR, key="af_box_hr", group=ACTIVITY, horizontal=True, height=380)
        insight_box(
            "Heart Rate by Activity",
            [ "Jumping recorded the highest heart rate (~152 BPM), while Stretching recorded the lowest (~87 BPM).", "Heart rate distributions varied across activities.", "No significant outliers were observed." ]
        )

    with st.container(border=True):
        feat_df = pd.DataFrame({name: df[cols].mean(axis=1) for name, cols in CORR_FEATURES.items()})
        corr = feat_df.corr()
        labels = list(corr.columns)
        n = len(labels)

        st.markdown(one_line(f"""
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
              <div>
                <div style="font-size:1.25rem;font-weight:600;">Sensor Correlation Heatmap</div>
                <div style="font-size:.8rem;opacity:.65;">Pearson r · window-level means and heart rate · n = {len(df):,} clean windows</div>
              </div>
              <span style="background:#EDE8F8;color:#6B4FB8;padding:4px 12px;border-radius:999px;font-size:.75rem;font-weight:600;">All activities · unfiltered</span>
            </div>
        """), unsafe_allow_html=True)

        col_chart, col_info = st.columns([1.6, 1], gap="large")

        with col_chart:
            event = st.plotly_chart(corr_heatmap(corr), use_container_width=True,
                                    key="af_heatmap", on_select="rerun", selection_mode="points")

        sel, picked = strongest_pair(corr), False
        try:
            pts = event["selection"]["points"]
        except (KeyError, TypeError):
            pts = []
        for p in pts:
            idx = p.get("point_index", p.get("point_number"))
            if idx is not None and 0 <= idx < n * n:
                sel, picked = (labels[idx // n], labels[idx % n]), True
                break

        a, b = sel
        r = corr.loc[a, b]
        label, meaning = describe_pair(a, b, r)
        hint = "Selected cell" if picked else "Strongest relationship · click any cell"

        with col_info:
            st.markdown(one_line(f"""
                <div style="padding-top:1.5rem;">
                  <div style="background:#EDE8F8;border-radius:14px;padding:1.2rem 1.4rem;color:#2B2740;">
                    <div style="font-size:.65rem;letter-spacing:.08em;color:#8A7BB0;margin-bottom:.5rem;">{hint.upper()}</div>
                    <div style="color:#6B4FB8;font-weight:700;font-size:1.3rem;">{a} ↔ {b}</div>
                    <div style="font-size:2rem;font-weight:700;line-height:1.1;margin:.2rem 0;">{r:+.2f}</div>
                    <div style="font-weight:600;font-size:.9rem;margin-bottom:.6rem;">{label} correlation</div>
                    <div style="font-size:.85rem;line-height:1.5;opacity:.85;">{meaning}</div>
                  </div>
                  <div style="height:8px;border-radius:6px;margin-top:1.2rem;background:linear-gradient(90deg,#C3D2BC,#F7F6F4,#9C84D6);"></div>
                  <div style="display:flex;justify-content:space-between;font-size:.7rem;opacity:.6;margin-top:.3rem;"><span>−1 · Negative</span><span>0</span><span>+1 · Positive</span></div>
                </div>
            """), unsafe_allow_html=True)

        st.caption("Acc = accelerometer (m/s²) · Gyro = gyroscope (rad/s) · HR = heart rate (bpm). Correlation coefficients are unitless.")
        
    #  Interactive Filters 

    with st.container(border=True):
        card_title("Interactive Filters", "Choose what to display")

        f1, f2, f3 = st.columns([1, 1.1, 1.1])

        activities = sorted(df[ACTIVITY].dropna().unique().tolist(), key=str)

        activity = f1.selectbox("Activity", activities, key="sig_activity")
        loc = f2.radio("Sensor", ["Both", "Wrist", "Waist"], horizontal=True, key="sig_loc")
        axis = f3.radio("Axis selection", ["X", "Y", "Z", "All"], horizontal=True, key="sig_axis")

        activity_df = df[df[ACTIVITY] == activity].reset_index(drop=True)

        if activity_df.empty:
            st.warning("No records for the selected filters.")

        else:
            locs = ["waist", "wrist"] if loc == "Both" else [loc.lower()]
            axes = ["x", "y", "z"] if axis == "All" else [axis.lower()]

            axis_colors = {
                "wrist": {"x": "#5623AE", "y": "#7B52CC", "z": "#A98BE6"},
                "waist": {"x": "#1E4A2C", "y": "#38754A", "z": "#7CC49A"},
            }

            axis_styles = {
                "x": dict(dash="solid"),
                "y": dict(dash="dash"),
                "z": dict(dash="dot"),
            }

            for sensor_type, kind in [("Accelerometer", "acc"), ("Gyroscope", "gyro")]:
                st.divider()
                card_title(f"{activity} - {sensor_type}")

                fig = go.Figure()

                for l in locs:
                    for a in axes:
                        col = f"{l}_{kind}_{a}"

                        fig.add_trace(
                            go.Scattergl(
                                x=list(range(len(activity_df))),
                                y=activity_df[col].to_numpy(),
                                mode="lines",
                                name=f"{l.title()} - {a.upper()}",
                                line=dict(
                                    color=axis_colors[l][a],
                                    width=1.5,
                                    dash=axis_styles[a]["dash"],
                                ),
                                legendgroup=l,
                            )
                        )

                plot_style(fig, 400)

                fig.update_layout(
                    title=None,
                    xaxis_title="Sample",
                    yaxis_title="Value",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                    margin=dict(t=50, b=45, l=45, r=20),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"sig_{activity}_{loc}_{axis}_{kind}",
                )
                insight_box(
                    f"{activity} · {sensor_type}",
                    [ "Signal patterns vary depending on the selected activity and sensor type.", "The plot helps visualize changes in sensor readings across the selected activity.", ]
                )

    #  Average heart rate 

    with st.container(border=True):
        card_title("Average Heart Rate Comparisons", "By gender, age group, activity and fitness level")

        col1, col2 = st.columns(2)
        with col1:
            mean_bar(df, "Gender", "af_bar_gender", "Average Heart Rate by Gender")
        with col2:
            mean_bar(df, "Age_Group", "af_bar_age",
                     "Average Heart Rate by Age Group and Gender", color="Gender")

        mean_bar(df, ACTIVITY, "af_bar_fitness",
                 "Average Heart Rate by Activity and Fitness Level", color="Fitness_Level")
        mean_bar(df, ACTIVITY, "af_bar_gender_act",
                 "Average Heart Rate by Activity and Gender", color="Gender")
        insight_box(
            "Average Heart Rate Comparisons",
            [ "Females had higher average heart rates than males despite having fewer records.", "Females had higher average heart rates across age groups and most activities, except Sit-ups.", "Beginners had higher average heart rates in Jumping, Sit-ups, and Squatting.", "Advanced participants had higher average heart rates in Push-ups, Running, and Stretching.", "The relationship between fitness level and heart rate varied across activities.", ]
        )



