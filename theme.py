"""
Usage in your main file: replace the big <style> st.markdown block with

    from theme import apply_theme
    apply_theme()
"""
import streamlit as st

THEME_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Archivo+Black&family=Caveat:wght@600&display=swap');

:root {
    --radius: 0.75rem;
    --background: #F8F5FE;
    --foreground: oklch(0.22 0.06 290);
    --card: oklch(0.995 0.004 300);
    --primary: oklch(0.42 0.2 292);
    --primary-foreground: oklch(0.98 0.01 300);
    --secondary: oklch(0.93 0.035 300);
    --muted: oklch(0.945 0.02 300);
    --muted-foreground: oklch(0.5 0.05 290);
    --border: oklch(0.88 0.03 300);
    --input: oklch(0.9 0.025 300);
    --sport-green: oklch(0.5 0.12 145);
    --sport-green-soft: oklch(0.94 0.045 140);
    --sport-yellow: oklch(0.86 0.17 95);
    --ink: oklch(0.2 0.05 290);
    --shadow-card: 0 1px 0 oklch(0.2 0.05 290 / 0.06), 0 18px 40px -28px oklch(0.3 0.15 292 / 0.45);
    --shadow-pop: 4px 4px 0 0 var(--ink);
    --font-display: "Archivo Black", "Archivo", sans-serif;
    --font-body: "Archivo", system-ui, sans-serif;
    --font-hand: "Caveat", cursive;
}

html, body, [class*="css"], .stApp, button, input, textarea { font-family: var(--font-body); color: var(--foreground); }
.stApp {
    background-color: #F8F5FE !important;
    background-image: radial-gradient(circle at 1px 1px, #ECE5F8 1px, transparent 0) !important;
    background-size: 22px 22px !important;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent !important; }
.block-container { max-width: 1180px; padding-top: 1.1rem; padding-bottom: 3rem; }
#MainMenu, footer, header { visibility: hidden; }

/* Top bar */
.topbar { display:flex; align-items:center; justify-content:flex-start; margin:0 2px 14px; }
.tag { font-size:11px; letter-spacing:.12em; font-weight:700; color:var(--ink); background:var(--sport-yellow);
       border:2px solid var(--ink); padding:5px 13px; border-radius:999px; box-shadow:2px 2px 0 0 var(--ink); }

/* Hero */
.hero-wrap {
    position:relative; display:flex; align-items:center; justify-content:space-between; flex-wrap:nowrap;
    text-align:left; padding:0; margin:0 0 20px; gap:0;
    background: var(--card); border:2px solid var(--ink); border-radius:calc(var(--radius) + 8px);
    box-shadow: var(--shadow-pop); overflow:hidden;
}
.hero-left { flex:1 1 55%; min-width:0; padding:34px 40px 32px; }
.hero-title { font-family:var(--font-display); text-transform:uppercase; font-weight:400;
              font-size:clamp(34px, 5.4vw, 68px); line-height:1.02; letter-spacing:-.01em; color:var(--ink); }
.hero-title span { display:block; width:fit-content; }
.hero-title .accent { color:var(--primary); }
.hero-title .hl { padding-right:.08em;
    background-image:linear-gradient(transparent 76%, var(--sport-yellow) 76%); }
.hero-link { margin-top:22px; }
.hero-art { flex:0 0 44%; align-self:stretch; display:flex; background:oklch(0.93 0.04 300); }
.hero-art img { width:100%; height:100%; object-fit:cover; object-position:center; display:block; }
@media (max-width:820px) { .hero-art { display:none; } .hero-left { padding:26px 22px; } }
.hero-sub { color:var(--muted-foreground); font-size:15px; line-height:1.7; max-width:760px; margin:14px 0 0; }
.dataset-link { display:inline-block; padding:9px 16px; border-radius:12px; background:var(--card);
    border:2px solid var(--ink); color:var(--ink) !important; text-decoration:none !important;
    font-size:13px; font-weight:700; box-shadow:3px 3px 0 0 var(--ink); transition:all .15s ease; white-space:nowrap; }
.dataset-link:hover { background:var(--sport-yellow); transform:translate(1px,1px); box-shadow:2px 2px 0 0 var(--ink); }

/* Buttons */
div.stButton > button {
    border-radius:12px; border:2px solid var(--ink); background:var(--card); color:var(--ink);
    font-weight:700; font-size:14px; min-height:2.6rem; box-shadow:var(--shadow-pop); transition:all .15s ease;
}
div.stButton > button p { color:inherit; font-weight:700; }
div.stButton > button:hover { border-color:var(--ink); color:var(--ink); background:var(--sport-yellow);
    transform:translate(2px,2px); box-shadow:2px 2px 0 0 var(--ink); }
div.stButton > button:active { transform:translate(4px,4px); box-shadow:0 0 0 0 var(--ink); }
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="stBaseButton-primary"] {
    background:var(--primary); border-color:var(--ink); color:var(--primary-foreground);
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background:oklch(0.5 0.21 292); color:var(--primary-foreground);
}
div.stButton > button:disabled { opacity:.5; transform:none; box-shadow:2px 2px 0 0 var(--ink); }

/* Predict effort button: green.
   Matches by key class (Streamlit >= 1.39) OR by the .eff-marker element placed right before the button. */
.st-key-eff_predict button,
div[data-testid="stElementContainer"]:has(.eff-marker) + div[data-testid="stElementContainer"] button,
div.element-container:has(.eff-marker) + div.element-container button {
    background:var(--sport-green) !important; border-color:var(--ink) !important; color:#fff !important;
}
.st-key-eff_predict button p,
div[data-testid="stElementContainer"]:has(.eff-marker) + div[data-testid="stElementContainer"] button p,
div.element-container:has(.eff-marker) + div.element-container button p { color:#fff !important; }
.st-key-eff_predict button:hover,
div[data-testid="stElementContainer"]:has(.eff-marker) + div[data-testid="stElementContainer"] button:hover,
div.element-container:has(.eff-marker) + div.element-container button:hover {
    background:oklch(0.56 0.13 145) !important; color:#fff !important;
}

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border:1.5px solid var(--border) !important;
    border-radius:calc(var(--radius) + 4px);
    box-shadow: var(--shadow-card);
}

/* Inputs & alerts */
div[data-baseweb="select"] > div { border-radius:12px; border:1.5px solid var(--input); background:var(--card); }
div[data-testid="stWidgetLabel"] p { font-size:13px; color:var(--foreground); font-weight:600; }
div[data-testid="stAlert"] { border-radius:12px; border:1.5px solid var(--ink); }
hr { border-color: var(--border) !important; }
div[data-testid="stCaptionContainer"] { color: var(--muted-foreground); }

/* Sensor group as pill buttons */
.st-key-hist_group div[role="radiogroup"] { gap:10px; flex-wrap:wrap; }
.st-key-hist_group div[role="radiogroup"] > label {
    background:var(--card); border:2px solid var(--ink); border-radius:12px;
    padding:6px 16px; margin:0; cursor:pointer;
    box-shadow:3px 3px 0 0 var(--ink); transition:all .15s ease;
}
.st-key-hist_group div[role="radiogroup"] > label > div:first-child { display:none; }
.st-key-hist_group div[role="radiogroup"] > label p { font-weight:700; font-size:14px; color:var(--ink); }
.st-key-hist_group div[role="radiogroup"] > label:hover {
    background:var(--sport-yellow); transform:translate(1px,1px); box-shadow:2px 2px 0 0 var(--ink);
}
.st-key-hist_group div[role="radiogroup"] > label:has(input:checked) { background:var(--primary); }
.st-key-hist_group div[role="radiogroup"] > label:has(input:checked) p { color:var(--primary-foreground); }

/* Sliders: yellow thumb with ink border (like .sport-range) */
div[data-baseweb="slider"] div[role="slider"] {
    background-color:var(--sport-yellow) !important; border:2px solid var(--ink) !important;
    box-shadow:none !important; height:18px !important; width:18px !important;
}
div[data-testid="stSliderThumbValue"], div[data-testid="stThumbValue"] { color:var(--ink) !important; font-weight:700; }

/* Section header */
.sec { display:flex; align-items:center; gap:12px; margin:30px 0 14px 0; }
.sec .badge { width:28px; height:28px; border-radius:9px; color:var(--ink); background:var(--sport-yellow);
              border:2px solid var(--ink); box-shadow:2px 2px 0 0 var(--ink);
              display:inline-flex; align-items:center; justify-content:center; font-family:var(--font-display); font-size:13px; }
.sec .sec-title { font-family:var(--font-display); font-size:19px; color:var(--ink); white-space:nowrap; }
.sec .line { flex:1; height:2px; background:var(--ink); opacity:.12; min-width:12px; }
.sec .sec-right { font-size:11px; letter-spacing:.12em; color:var(--muted-foreground); font-weight:700; white-space:nowrap; }

/* Stats strip */
.mstrip { display:flex; background: var(--card); border:2px solid var(--ink); border-radius:calc(var(--radius) + 6px);
          box-shadow:var(--shadow-pop); margin:0 0 20px 0; overflow:hidden; }
.mcell { position:relative; flex:1; padding:16px 26px 18px; transition: background .15s ease; }
.mcell + .mcell { border-left:2px solid var(--ink); }
.mcell:hover { background:var(--sport-green-soft); }
@media (max-width:700px) {
    .mstrip { flex-direction:column; }
    .mcell + .mcell { border-left:none; border-top:2px solid var(--ink); }
}
.mtop { display:flex; justify-content:space-between; align-items:center; }
.mlabel { font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted-foreground); font-weight:700; }
.micon { width:32px; height:32px; border-radius:10px; background:var(--sport-yellow); border:2px solid var(--ink);
         display:inline-flex; align-items:center; justify-content:center; font-size:14px; color:var(--ink); }
.mval { font-family:var(--font-display); font-size:34px; color:var(--ink); margin:8px 0 0 0; line-height:1.15; }
.msub { font-size:12px; color:var(--muted-foreground); }
.mbar { width:32px; height:4px; border-radius:4px; margin-top:12px; }

/* Card titles */
.ctitle { margin-bottom:8px; }
.ct { font-family:var(--font-display); font-size:16px; color:var(--ink); display:flex; align-items:center; gap:8px; }
.ct::before { content:""; width:10px; height:10px; border-radius:3px; flex:none;
              background:var(--sport-yellow); border:2px solid var(--ink); }
.cs { font-size:12px; color:var(--muted-foreground); margin-left:18px; }

.note { background:var(--sport-green-soft); border:2px solid var(--ink); border-radius:12px; padding:10px 14px;
        color:var(--ink); font-size:13px; margin-top:14px; }

/* ---- Boxes styled inline in Python (matched by their old colors, so the Python code stays untouched) ---- */
div[style*="background:#EDE8F8"] { background:var(--secondary) !important; color:var(--ink) !important;
    border:2px solid var(--ink); box-shadow:var(--shadow-pop); border-radius:calc(var(--radius) + 6px) !important; }
div[style*="background:#E6F2E6"] { background:var(--sport-green-soft) !important; color:var(--ink) !important;
    border:2px solid var(--ink); box-shadow:var(--shadow-pop); border-radius:calc(var(--radius) + 6px) !important; }
div[style*="background:#fff;border-radius:12px"] { background:var(--card) !important; border:2px solid var(--ink); border-radius:12px !important; }
div[style*="background:#6B4FB8"] { background:var(--primary) !important; }
div[style*="background:#3F7A4C"] { background:var(--sport-green) !important; }
div[style*="background:#DDD6F0"], div[style*="background:#CDE5D0"] { background:var(--border) !important; }
[style*="color:#6B4FB8"] { color:var(--primary) !important; }
[style*="color:#3F7A4C"] { color:oklch(0.45 0.13 140) !important; }
[style*="color:#8A7BB0"], [style*="color:#2F6B3A"] { color:var(--muted-foreground) !important; font-weight:700; }
[style*="font-size:1.6rem"], [style*="font-size:2.2rem"], [style*="font-size:2rem"], [style*="font-size:1.3rem"] {
    font-family:var(--font-display); font-weight:400 !important; }
span[style*="border-radius:999px"] { background:var(--sport-yellow) !important; color:var(--ink) !important;
    border:2px solid var(--ink); box-shadow:2px 2px 0 0 var(--ink); }

/* Stickers */
.sticker { position:fixed; z-index:1; pointer-events:none;
           filter:drop-shadow(0 6px 10px rgba(40,20,90,.28)); }
@media (max-width:1300px) { .sticker { display:block; } }
/* Fix radio button text visibility on all devices */
.stRadio label,
.stRadio label p,
.stRadio [data-testid="stMarkdownContainer"] p {
    color: #24183D !important;
    opacity: 1 !important;
    visibility: visible !important;
}

.stRadio div[role="radiogroup"] label {
    color: #24183D !important;
    -webkit-text-fill-color: #24183D !important;
}

.stRadio div[role="radiogroup"] label p {
    color: inherit !important;
    -webkit-text-fill-color: inherit !important;
}
</style>
"""

def apply_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)
