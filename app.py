import streamlit as st
from datetime import date, timedelta, datetime
import database as db
import json

st.set_page_config(
    page_title="CLC Daily Bulletin",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── DESIGN SYSTEM ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
  background: #f0f4f0 !important;
  font-family: 'DM Sans', sans-serif;
}
[data-testid="stAppViewContainer"] { padding: 0; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
#MainMenu, footer, .stDeployButton { display: none; }

/* ── Main container ── */
.main .block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

/* ── TOP NAV BAR ── */
.top-nav {
  background: #1a2e44;
  padding: 0 2rem;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.top-nav-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.top-nav-logo {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, #6BBF4E, #4a8f33);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; color: white; font-size: 0.85rem;
}
.top-nav-title {
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 0.95rem;
  color: white;
  letter-spacing: 0.02em;
}
.top-nav-sub {
  font-size: 0.72rem;
  color: rgba(255,255,255,0.5);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.top-nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.nav-badge {
  background: rgba(107,191,78,0.2);
  border: 1px solid rgba(107,191,78,0.4);
  color: #6BBF4E;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  letter-spacing: 0.05em;
}
.nav-badge.edit { background: rgba(232,161,37,0.2); border-color: rgba(232,161,37,0.4); color: #e8a125; }

/* ── BULLETIN HEADER ── */
.bulletin-hero {
  background: linear-gradient(135deg, #3d7a28 0%, #6BBF4E 60%, #8fd468 100%);
  padding: 1.75rem 2rem 1.5rem;
  position: relative;
  overflow: hidden;
}
.bulletin-hero::before {
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 200px; height: 200px;
  background: rgba(255,255,255,0.06);
  border-radius: 50%;
}
.bulletin-hero::after {
  content: '';
  position: absolute;
  bottom: -60px; right: 100px;
  width: 160px; height: 160px;
  background: rgba(255,255,255,0.04);
  border-radius: 50%;
}
.bulletin-hero-inner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  position: relative;
  z-index: 1;
}
.bulletin-date-label {
  font-family: 'DM Mono', monospace;
  font-size: 0.7rem;
  color: rgba(255,255,255,0.7);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 0.3rem;
}
.bulletin-date-main {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  color: white;
  font-weight: 700;
  line-height: 1.1;
}
.bulletin-date-sub {
  font-size: 0.85rem;
  color: rgba(255,255,255,0.75);
  margin-top: 0.25rem;
  font-weight: 400;
}
.fun-fact-pill {
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 12px;
  padding: 0.65rem 1rem;
  max-width: 420px;
}
.fun-fact-label {
  font-size: 0.65rem;
  color: rgba(255,255,255,0.6);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 0.2rem;
}
.fun-fact-text {
  font-size: 0.85rem;
  color: white;
  font-weight: 500;
  line-height: 1.4;
}

/* ── DAY NAV ── */
.day-nav-bar {
  background: white;
  border-bottom: 2px solid #e8f0e3;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  gap: 0;
  overflow-x: auto;
}
.day-pill {
  padding: 0.75rem 1.25rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: #5a6e5a;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
  text-decoration: none;
}
.day-pill:hover { color: #4a8f33; }
.day-pill.active { color: #4a8f33; border-bottom-color: #6BBF4E; }
.day-pill.today { color: #1a2e44; font-weight: 700; }

/* ── CONTENT AREA ── */
.content-area {
  padding: 1.5rem 2rem 3rem;
  max-width: 1600px;
  margin: 0 auto;
}

/* ── SECTION CARDS ── */
.section-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
  margin-bottom: 1.25rem;
}
.section-card-header {
  padding: 0.6rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.section-card-header.green  { background: #6BBF4E; }
.section-card-header.navy   { background: #1a2e44; }
.section-card-header.brown  { background: #A67C6A; }
.section-card-header.amber  { background: #e8a125; }
.section-card-header.blue   { background: #4a7fb5; }
.section-card-header.purple { background: #7a5bb5; }
.section-card-header.slate  { background: #6a7f8a; }
.section-card-header h3 {
  font-size: 0.72rem;
  font-weight: 700;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0;
}
.section-card-header.amber h3 { color: #1a2e44; }
.section-card-body { padding: 0.75rem; }

/* ── DATA TABLES ── */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
}
.data-table th {
  background: #f4f8f2;
  color: #4a6640;
  font-weight: 600;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.4rem 0.6rem;
  text-align: left;
  border-bottom: 2px solid #d8ead2;
}
.data-table td {
  padding: 0.4rem 0.6rem;
  border-bottom: 1px solid #f0f4ee;
  color: #2a3a2a;
  vertical-align: top;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #fafcf9; }
.data-table td.empty { color: #bbb; font-style: italic; font-size: 0.72rem; }

/* Kitchen highlight */
.kitchen-row td { background: #fff8e6 !important; font-weight: 600; }
.kitchen-badge {
  background: #e8a125;
  color: #1a2e44;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Vehicle time grid */
.vehicle-time { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #888; }
.vehicle-booking { 
  background: #e8f5e1; 
  color: #2d6b1a; 
  padding: 0.1rem 0.4rem; 
  border-radius: 4px; 
  font-size: 0.75rem;
  font-weight: 500;
}

/* Program changes scroll */
.pc-scroll { overflow-x: auto; }
.pc-table { min-width: 1400px; }
.pc-table th { background: #1a2e44; color: rgba(255,255,255,0.8); }
.pc-table td.timeslot { background: #f9fbf8; text-align: center; font-family: 'DM Mono', monospace; font-size: 0.7rem; }
.pc-table td.timeslot.filled { background: #e8f5e1; color: #2d6b1a; font-weight: 600; }

/* ── TABS ── */
[data-baseweb="tab-list"] {
  background: transparent !important;
  gap: 0.25rem !important;
  border-bottom: 2px solid #e0e8dc !important;
  padding: 0 !important;
}
[data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 8px 8px 0 0 !important;
  padding: 0.5rem 1rem !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  color: #7a907a !important;
  border: none !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: white !important;
  color: #4a8f33 !important;
  border-bottom: 2px solid #6BBF4E !important;
}
[data-baseweb="tab-panel"] { padding: 1rem 0 0 !important; }

/* ── STREAMLIT FORM OVERRIDES ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  border: 1.5px solid #d8e8d4 !important;
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.82rem !important;
  background: white !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: #6BBF4E !important;
  box-shadow: 0 0 0 3px rgba(107,191,78,0.15) !important;
}
label[data-testid="stWidgetLabel"] p {
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  color: #5a7a5a !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
}
.stButton button {
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
}
.stButton button[kind="primary"] {
  background: #4a8f33 !important;
  border: none !important;
}
.stButton button[kind="primary"]:hover { background: #3d7a28 !important; }

/* ── DATA EDITOR ── */
[data-testid="stDataEditor"] {
  border: 1.5px solid #d8e8d4 !important;
  border-radius: 10px !important;
  overflow: hidden;
}

/* ── ARCHIVE CARD ── */
.arch-card {
  background: white;
  border: 1.5px solid #e0e8dc;
  border-left: 4px solid #6BBF4E;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  margin-bottom: 0.6rem;
  transition: box-shadow 0.15s;
}
.arch-card:hover { box-shadow: 0 4px 16px rgba(107,191,78,0.15); }
.arch-card-date { font-weight: 700; font-size: 0.9rem; color: #1a2e44; }
.arch-card-fact { font-size: 0.78rem; color: #7a907a; margin-top: 0.2rem; }

/* ── EMPTY STATE ── */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #9ab09a;
  font-size: 0.85rem;
}
.empty-state .icon { font-size: 2rem; margin-bottom: 0.5rem; }

/* ── AUTH GATE ── */
.auth-gate {
  max-width: 400px;
  margin: 4rem auto;
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  text-align: center;
}
.auth-gate h2 { font-family: 'Playfair Display', serif; color: #1a2e44; margin-bottom: 0.5rem; }
.auth-gate p { color: #7a907a; font-size: 0.85rem; margin-bottom: 1.5rem; }

/* ── NOTIFICATIONS ── */
.stSuccess, .stError, .stInfo {
  border-radius: 10px !important;
  font-size: 0.85rem !important;
}

/* Responsive */
@media (max-width: 768px) {
  .bulletin-date-main { font-size: 1.4rem; }
  .content-area { padding: 1rem; }
  .fun-fact-pill { max-width: 100%; }
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────
def init_state():
    defaults = {
        "authenticated": False,
        "edit_mode": False,
        "selected_date": date.today(),
        "page": "bulletin",
        "show_login": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "clcstaff2026")

# ── HELPERS ───────────────────────────────────────────────────
def week_dates(d: date):
    monday = d - timedelta(days=d.weekday())
    return [monday + timedelta(days=i) for i in range(5)]

def term_label(d: date):
    y = d.year
    terms = {1:(date(y,1,28),date(y,4,11)), 2:(date(y,4,28),date(y,7,4)),
              3:(date(y,7,21),date(y,9,26)), 4:(date(y,10,13),date(y,12,12))}
    for t,(s,e) in terms.items():
        if s <= d <= e: return f"Term {t} · {y}"
    return str(y)

def default_bulletin():
    return {
        "fun_fact": "",
        "staff_absent": [{"Staff Absence":"","TRT":"","Student Absence":"","Program":"","Reason":""} for _ in range(4)],
        "excursions": [{"Program":"","Staff Member":"","Time Departing":"","Time Returning":"","Location":""} for _ in range(4)],
        "staff_meetings": [{"Type":"","Staff Member":"","Location":"","Time Departing":"","Time Returning":"","Student":""} for _ in range(4)],
        "entry_meetings": [{"Time":"","Program":"","Student":""} for _ in range(4)],
        "additional_messages": [{"Staff Member":"","Visitor":"","Reason":"","Arriving/Departing":""} for _ in range(4)],
        "travel_jp": [{"Student":"","Transport To":"","Transport From":"","Times":""} for _ in range(5)],
        "travel_py": [{"Student":"","Transport To":"","Transport From":"","Times":""} for _ in range(5)],
        "travel_sy": [{"Student":"","Transport To":"","Transport From":"","Times":""} for _ in range(5)],
        "vehicle_bookings": {t:{"van":"","kia":""} for t in ["9:00","10:00","11:00","12:00","1:00","2:00","3:00"]},
        "staff_responsibilities": {"kitchen_duties":"","meeting_pd_focus":"","chair":"","minutes":""},
        "nit_booking": "",
        "program_changes": [{
            "TRT":"","CLC Responsibility":"","Type":"","CLC Staff Absent":"",
            "JP":"","PY":"","SY":"","NIT":"",
            "9:00-9:30":"","9:30-10:00":"","10:00-10:30":"","10:30-11:00":"",
            "11:00-11:30":"","11:30-12:00":"","12:00-12:30":"","12:30-1:00":"",
            "1:00-1:30":"","1:30-2:00":"","2:00-2:30":"","2:30-2:45":""
        } for _ in range(5)]
    }

def load_bulletin(d: date):
    data = db.get_bulletin(d)
    defaults = default_bulletin()
    if not data:
        return defaults
    for k, v in defaults.items():
        if k not in data:
            data[k] = v
    return data


# ── QUICK NOTICE HELPERS ──────────────────────────────────────
NOTICE_CATS = {
    "General":      {"color": "#4a8f33", "bg": "#e8f5e1", "emoji": "📢"},
    "Reminder":     {"color": "#c97b1a", "bg": "#fff3e0", "emoji": "⏰"},
    "Urgent":       {"color": "#b91c1c", "bg": "#fee2e2", "emoji": "🚨"},
    "Student Info": {"color": "#1d4ed8", "bg": "#dbeafe", "emoji": "👨‍🎓"},
    "Facilities":   {"color": "#6d28d9", "bg": "#ede9fe", "emoji": "🏫"},
    "Wellbeing":    {"color": "#0e7490", "bg": "#cffafe", "emoji": "💚"},
}

def _get_sb():
    return db.get_supabase()

def load_notices(for_date=None):
    try:
        q = _get_sb().table("bulletin_notices").select("*").order("created_at", desc=False)
        if for_date:
            q = q.eq("notice_date", str(for_date))
        result = q.execute()
        return result.data or []
    except Exception as e:
        st.warning(f"⚠️ Could not load notices: {e}")
        return []

def save_notice(row):
    try:
        _get_sb().table("bulletin_notices").insert(row).execute()
    except Exception as e:
        st.error(f"Could not save notice: {e}")

def delete_notice(nid):
    try:
        _get_sb().table("bulletin_notices").delete().eq("id", nid).execute()
    except Exception as e:
        st.error(f"Could not delete notice: {e}")



# ══════════════════════════════════════════════════════════════
# DISPLAY MODE — Staff Room Full-Screen View
# Access via: your-app-url/?display=true
# ══════════════════════════════════════════════════════════════

# Check URL params for display mode
params = st.query_params
if params.get("display") == "true":

    # Load today's bulletin
    today = date.today()
    d_data = load_bulletin(today)

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #0f1a0f !important; }
    .main .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stHeader"] { display: none; }
    #MainMenu, footer, .stDeployButton { display: none; }
    [data-baseweb="tab-list"] { display: none !important; }
    [data-baseweb="tab-panel"] { padding: 0 !important; }
    /* hide the normal tabs rendered above */
    section[data-testid="stVerticalBlock"] > div:first-child { display: none; }
    </style>
    """, unsafe_allow_html=True)

    # Auto-refresh every 5 minutes using Streamlit
    import time
    if "display_last_refresh" not in st.session_state:
        st.session_state.display_last_refresh = time.time()
    if time.time() - st.session_state.display_last_refresh > 300:
        st.session_state.display_last_refresh = time.time()
        st.rerun()

    # Google fonts
    st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">""", unsafe_allow_html=True)

    # ── Header banner ──
    sr = d_data.get("staff_responsibilities", {})
    fun = d_data.get("fun_fact", "")

    st.markdown(f"""
    <style>
    .display-header {{
      background: linear-gradient(135deg, #1a2e44 0%, #1e3d1e 100%);
      padding: 0.6rem 1.5rem;
      display: flex; align-items: center; justify-content: space-between;
      border-bottom: 3px solid #6BBF4E;
    }}
    .display-header-title {{ font-family: 'Playfair Display', serif; font-size: 1.1rem; color: white; font-weight: 700; letter-spacing: 0.05em; }}
    .display-header-date {{ font-family: 'DM Mono', monospace; font-size: 1rem; color: #6BBF4E; font-weight: 600; letter-spacing: 0.08em; }}
    .display-header-time {{ font-family: 'DM Mono', monospace; font-size: 1.4rem; color: #e8a125; font-weight: 700; }}
    .dp {{ background: #1a2a1a; border: 1px solid #2a3d2a; border-radius: 8px; overflow: hidden; margin-bottom: 6px; }}
    .dp-header {{ padding: 0.3rem 0.6rem; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: white; }}
    .dp-header.green  {{ background: #4a8f33; }}
    .dp-header.navy   {{ background: #1a2e44; }}
    .dp-header.brown  {{ background: #7a5c4a; }}
    .dp-header.amber  {{ background: #c97b1a; color: #1a2e44; }}
    .dp-header.blue   {{ background: #3a6a9a; }}
    .dp-header.purple {{ background: #6a4a9a; }}
    .dp-header.slate  {{ background: #4a5a6a; }}
    .dp-body {{ padding: 0.4rem 0.5rem; }}
    .dt {{ width: 100%; border-collapse: collapse; font-size: 0.62rem; color: #c8d8c8; font-family: 'DM Sans', sans-serif; }}
    .dt th {{ color: #6BBF4E; font-weight: 600; font-size: 0.55rem; text-transform: uppercase; letter-spacing: 0.06em; padding: 0.2rem 0.3rem; border-bottom: 1px solid #2a3d2a; }}
    .dt td {{ padding: 0.18rem 0.3rem; border-bottom: 1px solid #1e2e1e; vertical-align: top; line-height: 1.3; }}
    .dt tr:last-child td {{ border-bottom: none; }}
    .dt-em {{ color: #3a4a3a; font-style: italic; font-size: 0.55rem; }}
    .dp-empty {{ color: #3a4a3a; font-size: 0.6rem; padding: 0.3rem; font-style: italic; font-family: 'DM Sans', sans-serif; }}
    .vb-time {{ font-family: 'DM Mono', monospace; font-size: 0.58rem; color: #5a7a5a; }}
    .vb-tag {{ background: #2a4a2a; color: #6BBF4E; padding: 0.05rem 0.35rem; border-radius: 3px; font-size: 0.6rem; font-weight: 600; }}
    .kitchen-val {{ background: #c97b1a; border-radius: 4px; padding: 0.1rem 0.4rem; color: #1a2e44; font-weight: 800; font-size: 0.65rem; display: inline-block; }}
    .resp-label {{ font-size: 0.58rem; color: #6BBF4E; font-weight: 600; }}
    .resp-val {{ font-size: 0.62rem; color: #c8d8c8; }}
    .fact-bar {{ background: #1e2e1e; border-top: 2px solid #2a3d2a; padding: 0.4rem 1.5rem; font-size: 0.72rem; color: #a8c8a8; display: flex; align-items: center; gap: 0.75rem; font-family: 'DM Sans', sans-serif; }}
    .fact-label {{ color: #e8a125; font-weight: 700; font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap; }}
    .pc-wrap {{ overflow-x: auto; }}
    .pc-table {{ min-width: 900px; }}
    .slot {{ text-align: center; font-family: 'DM Mono', monospace; font-size: 0.55rem; }}
    .slot.filled {{ background: #1e3d1e; color: #6BBF4E; font-weight: 600; }}
    </style>

    <div class="display-header">
      <div>
        <div class="display-header-title">Cowandilla Learning Centre &mdash; Daily Bulletin</div>
        <div class="display-header-date">{today.strftime("%A %-d %B %Y").upper()}</div>
      </div>
      <div style="display:flex;align-items:center;gap:1.5rem;">
        <div class="display-header-time" id="live-clock">--:-- --</div>
        <a href="/?quickadd=true" style="background:rgba(107,191,78,0.2);border:1px solid rgba(107,191,78,0.5);color:#6BBF4E;font-family:'DM Sans',sans-serif;font-size:0.68rem;font-weight:600;padding:0.3rem 0.85rem;border-radius:6px;text-decoration:none;letter-spacing:0.05em;">📝 Quick Add</a><a href="/?from_display=true" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.18);color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;font-size:0.68rem;font-weight:600;padding:0.3rem 0.85rem;border-radius:6px;text-decoration:none;letter-spacing:0.05em;">✏️ Staff Access</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Helper for table rows ──
    def tbl_rows(rows, keys):
        filtered = [r for r in rows if any(r.get(k,"") for k in keys)]
        if not filtered:
            return '<tr><td colspan="20" class="dt-em">None today</td></tr>'
        return "".join(["<tr>" + "".join([f"<td>{r.get(k,'')}</td>" for k in keys]) + "</tr>" for r in filtered])

    # ── ROW 1: 5 columns ──
    r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns([2,2,2.5,1.5,2])

    with r1c1:
        st.markdown(f"""
        <div class="dp"><div class="dp-header green">🙅 Staff & Student Absent</div><div class="dp-body">
        <table class="dt"><tr><th>Staff</th><th>TRT</th><th>Student</th><th>Program</th><th>Reason</th></tr>
        {tbl_rows(d_data.get("staff_absent",[]), ["Staff Absence","TRT","Student Absence","Program","Reason"])}
        </table></div></div>
        """, unsafe_allow_html=True)

    with r1c2:
        st.markdown(f"""
        <div class="dp"><div class="dp-header blue">🚌 Excursions</div><div class="dp-body">
        <table class="dt"><tr><th>Program</th><th>Staff</th><th>Depart</th><th>Return</th><th>Location</th></tr>
        {tbl_rows(d_data.get("excursions",[]), ["Program","Staff Member","Time Departing","Time Returning","Location"])}
        </table></div></div>
        """, unsafe_allow_html=True)

    with r1c3:
        st.markdown(f"""
        <div class="dp"><div class="dp-header navy">🤝 Staff Meetings</div><div class="dp-body">
        <table class="dt"><tr><th>Type</th><th>Staff</th><th>Location</th><th>Depart</th><th>Return</th><th>Student</th></tr>
        {tbl_rows(d_data.get("staff_meetings",[]), ["Type","Staff Member","Location","Time Departing","Time Returning","Student"])}
        </table></div></div>
        """, unsafe_allow_html=True)

    with r1c4:
        st.markdown(f"""
        <div class="dp"><div class="dp-header brown">📥 Entry Meetings</div><div class="dp-body">
        <table class="dt"><tr><th>Time</th><th>Program</th><th>Student</th></tr>
        {tbl_rows(d_data.get("entry_meetings",[]), ["Time","Program","Student"])}
        </table></div></div>
        """, unsafe_allow_html=True)

    with r1c5:
        # Staff Responsibilities
        kitchen = sr.get("kitchen_duties","") or "—"
        pd_focus = sr.get("meeting_pd_focus","") or "—"
        chair = sr.get("chair","") or "—"
        minutes = sr.get("minutes","") or "—"
        st.markdown(f"""
        <div class="dp"><div class="dp-header amber">⭐ Staff Responsibilities</div><div class="dp-body">
        <div style="margin-bottom:0.35rem;"><span class="kitchen-val">🍳 Kitchen: {kitchen}</span></div>
        <div style="margin-bottom:0.2rem;"><span class="resp-label">📌 PD Focus</span><br><span class="resp-val">{pd_focus}</span></div>
        <div style="margin-bottom:0.2rem;"><span class="resp-label">🪑 Chair</span><br><span class="resp-val">{chair}</span></div>
        <div><span class="resp-label">📝 Minutes</span><br><span class="resp-val">{minutes}</span></div>
        </div></div>
        """, unsafe_allow_html=True)

    # ── ROW 2: Travel + Vehicle + NIT ──
    r2c1, r2c2, r2c3, r2c4, r2c5 = st.columns([2,2,2,1.5,1])

    with r2c1:
        st.markdown(f"""
        <div class="dp"><div class="dp-header blue">🟦 JP – Travel</div><div class="dp-body">
        <table class="dt"><tr><th>Student</th><th>To</th><th>From</th><th>Times</th></tr>
        {tbl_rows(d_data.get("travel_jp",[]), ["Student","Transport To","Transport From","Times"])}
        </table></div></div>
        """, unsafe_allow_html=True)

    with r2c2:
        st.markdown(f"""
        <div class="dp"><div class="dp-header purple">🟣 PY – Travel</div><div class="dp-body">
        <table class="dt"><tr><th>Student</th><th>To</th><th>From</th><th>Times</th></tr>
        {tbl_rows(d_data.get("travel_py",[]), ["Student","Transport To","Transport From","Times"])}
        </table></div></div>
        """, unsafe_allow_html=True)

    with r2c3:
        st.markdown(f"""
        <div class="dp"><div class="dp-header slate">🟫 SY – Travel</div><div class="dp-body">
        <table class="dt"><tr><th>Student</th><th>To</th><th>From</th><th>Times</th></tr>
        {tbl_rows(d_data.get("travel_sy",[]), ["Student","Transport To","Transport From","Times"])}
        </table></div></div>
        """, unsafe_allow_html=True)

    with r2c4:
        vb = d_data.get("vehicle_bookings", {})
        times = ["9:00","10:00","11:00","12:00","1:00","2:00","3:00"]
        vb_rows = "".join([
            f'<tr><td class="vb-time">{t}</td>'
            f'<td>{"<span class=vb-tag>" + vb.get(t,{}).get("van","") + "</span>" if vb.get(t,{}).get("van","") else ""}</td>'
            f'<td>{"<span class=vb-tag>" + vb.get(t,{}).get("kia","") + "</span>" if vb.get(t,{}).get("kia","") else ""}</td></tr>'
            for t in times
        ])
        st.markdown(f"""
        <div class="dp"><div class="dp-header navy">🚗 Vehicles</div><div class="dp-body">
        <table class="dt"><tr><th>Time</th><th>VAN</th><th>KIA</th></tr>{vb_rows}</table>
        </div></div>
        """, unsafe_allow_html=True)

    with r2c5:
        nit = d_data.get("nit_booking","") or '<span class="dp-empty">None today</span>'
        msgs = d_data.get("additional_messages",[])
        msg_rows = tbl_rows(msgs, ["Staff Member","Visitor","Reason","Arriving/Departing"])
        st.markdown(f"""
        <div class="dp"><div class="dp-header green">📋 NIT Booking</div><div class="dp-body">
        <p style="font-size:0.62rem;color:#c8d8c8;margin:0;line-height:1.4;">{nit}</p>
        </div></div>
        <div class="dp"><div class="dp-header slate">💬 Messages</div><div class="dp-body">
        <table class="dt"><tr><th>Staff</th><th>Visitor</th><th>Reason</th><th>Arr/Dep</th></tr>{msg_rows}</table>
        </div></div>
        """, unsafe_allow_html=True)

    # ── ROW 3: Program Changes (full width) ──
    pc_rows = d_data.get("program_changes", [])
    pc_filtered = [r for r in pc_rows if any(r.get(k,"") for k in r)]
    time_slots = ["9:00-9:30","9:30-10:00","10:00-10:30","10:30-11:00","11:00-11:30",
                  "11:30-12:00","12:00-12:30","12:30-1:00","1:00-1:30","1:30-2:00","2:00-2:30","2:30-2:45"]
    pc_headers = "<th>TRT</th><th>CLC Resp.</th><th>Type</th><th>Staff Absent</th><th>JP</th><th>PY</th><th>SY</th><th>NIT</th>" + "".join([f"<th>{s}</th>" for s in time_slots])
    pc_body = ""
    if pc_filtered:
        for r in pc_filtered:
            cells = "".join([f"<td>{r.get(k,'')}</td>" for k in ["TRT","CLC Responsibility","Type","CLC Staff Absent","JP","PY","SY","NIT"]])
            cells += "".join([f'<td class="slot {"filled" if r.get(s,"") else ""}">{r.get(s,"")}</td>' for s in time_slots])
            pc_body += f"<tr>{cells}</tr>"
    else:
        pc_body = '<tr><td colspan="20" class="dt-em">No program changes today</td></tr>'

    st.markdown(f"""
    <div class="dp"><div class="dp-header green">📊 Program Changes</div><div class="dp-body pc-wrap">
    <table class="dt pc-table"><tr>{pc_headers}</tr>{pc_body}</table>
    </div></div>
    """, unsafe_allow_html=True)

    # ── Staff Notices row (display mode) ──
    d_notices = load_notices(for_date=today)
    if d_notices:
        n_parts = []
        for n in d_notices:
            cat = n.get("category","General")
            nc  = NOTICE_CATS.get(cat, NOTICE_CATS["General"])
            n_parts.append(
                f'<span style="background:{nc["bg"]};color:{nc["color"]};font-size:0.58rem;'
                f'font-weight:700;text-transform:uppercase;letter-spacing:0.06em;'
                f'padding:0.1rem 0.4rem;border-radius:10px;">{cat}</span> '
                f'<strong style="color:#c8d8c8;font-size:0.65rem;">{n.get("title","")}</strong>'
                f'<span style="color:#8aaa8a;font-size:0.62rem;"> — {n.get("body","")}</span>'
                f'<span style="color:#4a6a4a;font-size:0.58rem;"> · {n.get("submitted_by","")}</span>'
            )
        n_html = "<br>".join(n_parts)
        st.markdown(
            f'<div class="dp"><div class="dp-header green">📝 Staff Notices</div>'
            f'<div class="dp-body"><div style="font-family:DM Sans,sans-serif;line-height:1.8;">{n_html}</div></div></div>',
            unsafe_allow_html=True)

    # ── Live clock JS (Adelaide time) ──
    st.markdown("""
    <script>
    (function() {
      function updateClock() {
        var now = new Date();
        // Format in Adelaide timezone
        var opts = { timeZone: 'Australia/Adelaide', hour: 'numeric', minute: '2-digit', hour12: true };
        var timeStr = now.toLocaleTimeString('en-AU', opts).toUpperCase();
        var el = document.getElementById('live-clock');
        if (el) el.textContent = timeStr;
      }
      updateClock();
      setInterval(updateClock, 1000);
    })();
    </script>
    """, unsafe_allow_html=True)

    # ── Fun fact footer ──
    st.markdown(f"""
    <div class="fact-bar">
      <span class="fact-label">💡 Fun Fact</span>
      <span>{fun if fun else "No fun fact entered for today"}</span>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════════════════════
# QUICK ADD MODE — Standalone form (no tabs, no login needed)
# Access via: your-app-url/?quickadd=true
# ══════════════════════════════════════════════════════════════
if params.get("quickadd") == "true":
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #f0f7eb !important; }
    .main .block-container { padding: 2rem 2rem 3rem !important; max-width: 620px !important; margin: 0 auto !important; }
    [data-testid="stHeader"] { display: none; }
    #MainMenu, footer, .stDeployButton { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#3d7a28,#6BBF4E);border-radius:14px;
    padding:1.5rem 2rem;margin-bottom:1.5rem;text-align:center;color:white;">
      <div style="font-size:2rem;margin-bottom:0.3rem;">📝</div>
      <div style="font-size:1.3rem;font-weight:700;margin-bottom:0.25rem;">Staff Quick Notice</div>
      <div style="font-size:0.85rem;opacity:0.85;">Cowandilla Learning Centre · Daily Bulletin</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("qa_standalone_form", clear_on_submit=True):
        qa_name  = st.text_input("Your name *", placeholder="e.g. Sarah")
        qa_cat   = st.selectbox("Category *", list(NOTICE_CATS.keys()),
                                format_func=lambda x: f"{NOTICE_CATS[x]['emoji']} {x}")
        qa_title = st.text_input("Title *", placeholder="e.g. Staff meeting moved to Room 3")
        qa_body  = st.text_area("Details (optional)", placeholder="Any extra info staff need to know…", height=110)
        qa_date  = st.date_input("For which day?", value=date.today())
        qa_ok    = st.form_submit_button("📢 Post Notice to Bulletin", type="primary", use_container_width=True)

        if qa_ok:
            if not qa_name.strip():
                st.warning("Please enter your name.")
            elif not qa_title.strip():
                st.warning("Please enter a title.")
            else:
                save_notice({
                    "submitted_by": qa_name.strip(),
                    "category":     qa_cat,
                    "title":        qa_title.strip(),
                    "body":         qa_body.strip(),
                    "notice_date":  str(qa_date),
                })
                st.success(f"✅ Notice posted for {qa_date.strftime('%-d %B')}! It's now live on the bulletin.")
                st.balloons()

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center;">'
        '<a href="/" style="font-size:0.82rem;color:#4a8f33;font-weight:600;text-decoration:none;">← Back to full bulletin</a>'
        '&nbsp;&nbsp;|&nbsp;&nbsp;'
        '<a href="/?display=true" style="font-size:0.82rem;color:#4a8f33;font-weight:600;text-decoration:none;">Staff room display →</a>'
        '</div>',
        unsafe_allow_html=True)

    # Show today's notices below form
    qa_today = load_notices(for_date=date.today())
    if qa_today:
        st.markdown(f"**Posted today ({date.today().strftime('%-d %B')}):**")
        for n in qa_today:
            cat = n.get("category","General")
            nc  = NOTICE_CATS.get(cat, NOTICE_CATS["General"])
            st.markdown(
                f'<div style="background:white;border-radius:10px;border-left:4px solid {nc["color"]};'
                f'padding:0.7rem 1rem;margin-bottom:0.5rem;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
                f'<span style="background:{nc["bg"]};color:{nc["color"]};font-size:0.65rem;font-weight:700;'
                f'text-transform:uppercase;padding:0.15rem 0.5rem;border-radius:20px;">{nc["emoji"]} {cat}</span>'
                f'<span style="font-size:0.7rem;color:#9ab09a;margin-left:0.5rem;">from {n.get("submitted_by","")}</span>'
                f'<div style="font-size:0.9rem;font-weight:700;color:#1a2e44;margin:0.3rem 0 0.15rem;">{n.get("title","")}</div>'
                f'<div style="font-size:0.82rem;color:#3a4a3a;">{n.get("body","") or ""}</div>'
                f'</div>',
                unsafe_allow_html=True)

    st.stop()


# ── TOP NAV ───────────────────────────────────────────────────
edit = st.session_state.edit_mode and st.session_state.authenticated

auth_badge = ""
if st.session_state.authenticated:
    if edit:
        auth_badge = '<span class="nav-badge edit">✏️ Edit Mode</span>'
    else:
        auth_badge = '<span class="nav-badge">✅ Staff</span>'
else:
    auth_badge = ''

st.markdown(f"""
<div class="top-nav">
  <div class="top-nav-left">
    <div class="top-nav-logo">CLC</div>
    <div>
      <div class="top-nav-title">Daily Bulletin</div>
      <div class="top-nav-sub">Cowandilla Learning Centre</div>
    </div>
  </div>
  <div class="top-nav-right">
    {auth_badge}
  </div>
</div>
""", unsafe_allow_html=True)

# ── CURRENT DATE + DATA ────────────────────────────────────────
current_date = st.session_state.selected_date
bulletin_data = load_bulletin(current_date)

# ── PAGE ROUTING ───────────────────────────────────────────────
# Top-level tabs
page_tab, quickadd_tab, archive_tab, login_tab = st.tabs(["📋 Bulletin", "📝 Quick Add", "🗂️ Archive", "🔐 Staff"])

# ══════════════════════════════════════════════════════════════
# TAB: BULLETIN
# ══════════════════════════════════════════════════════════════
with page_tab:

    # ── From display: show quick login banner ──
    if st.query_params.get("from_display") == "true" and not st.session_state.authenticated:
        st.markdown("""
        <div style="background:#1a2e44;border-left:4px solid #6BBF4E;padding:0.75rem 1rem;border-radius:0 8px 8px 0;margin-bottom:1rem;display:flex;align-items:center;gap:1rem;">
          <span style="font-size:1.2rem;">🔐</span>
          <span style="color:white;font-size:0.85rem;">Enter your staff password below to edit today's bulletin, then save to return to the display screen.</span>
        </div>
        """, unsafe_allow_html=True)
        pw_col, btn_col, back_col = st.columns([2,1,1])
        with pw_col:
            quick_pw = st.text_input("Staff Password", type="password", key="quick_pw", label_visibility="collapsed", placeholder="Enter staff password...")
        with btn_col:
            if st.button("🔓 Login", type="primary", use_container_width=True):
                if quick_pw == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.edit_mode = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
        with back_col:
            st.markdown('<a href="/?display=true" style="display:block;text-align:center;background:#eef1f4;color:#1a2e44;font-weight:600;font-size:0.85rem;padding:0.5rem;border-radius:8px;text-decoration:none;">↩️ Back to Display</a>', unsafe_allow_html=True)
        st.markdown("---")

    # ── Hero header ──
    week = week_dates(current_date)
    day_pills = ""
    for d in week:
        active = "active" if d == current_date else ""
        today_cls = "today" if d == date.today() else ""
        day_pills += f'<span class="day-pill {active} {today_cls}" data-date="{d}">{d.strftime("%a %-d %b")}</span>'

    fun_fact_html = ""
    fact = bulletin_data.get("fun_fact","")
    if fact:
        fun_fact_html = f"""
        <div class="fun-fact-pill">
          <div class="fun-fact-label">💡 Fun Fact</div>
          <div class="fun-fact-text">{fact}</div>
        </div>"""

    st.markdown(f"""
    <div class="bulletin-hero">
      <div class="bulletin-hero-inner">
        <div>
          <div class="bulletin-date-label">{term_label(current_date)}</div>
          <div class="bulletin-date-main">{current_date.strftime("%A %-d %B")}</div>
          <div class="bulletin-date-sub">{current_date.strftime("%Y")}</div>
        </div>
        {fun_fact_html}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Week day selector with week navigation ──
    st.markdown('<div style="background:white;border-bottom:2px solid #e8f0e3;padding:0.4rem 1rem 0;">', unsafe_allow_html=True)

    # Week navigation row
    nav_left, nav_mid, nav_right = st.columns([1, 4, 1])
    with nav_left:
        prev_monday = week[0] - timedelta(days=7)
        if st.button("← Prev Week", key="prev_week", use_container_width=True):
            st.session_state.selected_date = prev_monday
            st.rerun()
    with nav_mid:
        week_label_str = f"Week of {week[0].strftime('%-d %b')} – {week[-1].strftime('%-d %b %Y')}"
        is_this_week = date.today() in week
        if is_this_week:
            week_label_str += " · This Week"
        st.markdown(
            f'<div style="text-align:center;padding:0.45rem 0;font-size:0.78rem;font-weight:600;'
            f'color:{"#4a8f33" if is_this_week else "#5a6e5a"};">{week_label_str}</div>',
            unsafe_allow_html=True,
        )
    with nav_right:
        next_monday = week[0] + timedelta(days=7)
        if st.button("Next Week →", key="next_week", use_container_width=True):
            st.session_state.selected_date = next_monday
            st.rerun()

    # Day buttons
    day_cols = st.columns(5)
    for i, d in enumerate(week):
        with day_cols[i]:
            is_current = d == current_date
            is_today   = d == date.today()
            label = d.strftime("%a %-d %b") + (" ◉" if is_today else "")
            btn_type = "primary" if is_current else "secondary"
            if st.button(label, key=f"day_{d}", use_container_width=True, type=btn_type):
                st.session_state.selected_date = d
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Edit controls ──
    # NOTE: Save is triggered here but executed AFTER all data editors below have
    # updated bulletin_data, using a session_state flag to avoid saving stale data.
    if st.session_state.authenticated:
        ctrl_cols = st.columns([1,1,6])
        with ctrl_cols[0]:
            if st.button("✏️ Edit" if not edit else "👁️ View", type="primary" if not edit else "secondary", use_container_width=True):
                st.session_state.edit_mode = not st.session_state.edit_mode
                st.rerun()
        with ctrl_cols[1]:
            if edit:
                if st.button("💾 Save", type="primary", use_container_width=True):
                    st.session_state["_pending_save"] = True

    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION TABS
    # ═══════════════════════════════════════════════════════
    s1, s2, s3, s4 = st.tabs(["👥 Staff & Meetings", "🚌 Travel & Vehicles", "📌 Responsibilities & NIT", "📊 Program Changes"])

    # ─────────────────────────────────────────────────────
    # TAB S1: Staff & Meetings
    # ─────────────────────────────────────────────────────
    with s1:
        if edit:
            bulletin_data["fun_fact"] = st.text_input("💡 Fun Fact of the Day", value=bulletin_data.get("fun_fact",""), placeholder="Enter an interesting fact...")

        col_left, col_right = st.columns(2)

        with col_left:
            # Staff & Student Absent
            st.markdown('<div class="section-card"><div class="section-card-header green"><h3>🙅 Staff & Student Absent</h3></div><div class="section-card-body">', unsafe_allow_html=True)
            if edit:
                import pandas as pd
                df = pd.DataFrame(bulletin_data["staff_absent"])
                edited = st.data_editor(df, key="sa_editor", hide_index=True, use_container_width=True,
                    column_config={c: st.column_config.TextColumn(c) for c in df.columns})
                bulletin_data["staff_absent"] = edited.to_dict("records")
            else:
                rows = bulletin_data["staff_absent"]
                has_data = any(any(v for v in r.values()) for r in rows)
                if has_data:
                    st.markdown('<table class="data-table"><tr><th>Staff Absence</th><th>TRT</th><th>Student</th><th>Program</th><th>Reason</th></tr>' +
                        "".join([f"<tr><td>{r.get('Staff Absence','')}</td><td>{r.get('TRT','')}</td><td>{r.get('Student Absence','')}</td><td>{r.get('Program','')}</td><td>{r.get('Reason','')}</td></tr>"
                        for r in rows if any(v for v in r.values())]) + "</table>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-state"><div class="icon">✅</div>No absences today</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

            # Excursions
            st.markdown('<div class="section-card"><div class="section-card-header blue"><h3>🚌 Excursions</h3></div><div class="section-card-body">', unsafe_allow_html=True)
            if edit:
                df = pd.DataFrame(bulletin_data["excursions"])
                edited = st.data_editor(df, key="ex_editor", hide_index=True, use_container_width=True)
                bulletin_data["excursions"] = edited.to_dict("records")
            else:
                rows = bulletin_data["excursions"]
                has_data = any(any(v for v in r.values()) for r in rows)
                if has_data:
                    st.markdown('<table class="data-table"><tr><th>Program</th><th>Staff</th><th>Departing</th><th>Returning</th><th>Location</th></tr>' +
                        "".join([f"<tr><td>{r.get('Program','')}</td><td>{r.get('Staff Member','')}</td><td>{r.get('Time Departing','')}</td><td>{r.get('Time Returning','')}</td><td>{r.get('Location','')}</td></tr>"
                        for r in rows if any(v for v in r.values())]) + "</table>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-state"><div class="icon">🗺️</div>No excursions today</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

            # Entry Meetings
            st.markdown('<div class="section-card"><div class="section-card-header brown"><h3>📥 Entry Meetings – Annette</h3></div><div class="section-card-body">', unsafe_allow_html=True)
            if edit:
                df = pd.DataFrame(bulletin_data["entry_meetings"])
                edited = st.data_editor(df, key="em_editor", hide_index=True, use_container_width=True)
                bulletin_data["entry_meetings"] = edited.to_dict("records")
            else:
                rows = bulletin_data["entry_meetings"]
                has_data = any(any(v for v in r.values()) for r in rows)
                if has_data:
                    st.markdown('<table class="data-table"><tr><th>Time</th><th>Program</th><th>Student</th></tr>' +
                        "".join([f"<tr><td>{r.get('Time','')}</td><td>{r.get('Program','')}</td><td>{r.get('Student','')}</td></tr>"
                        for r in rows if any(v for v in r.values())]) + "</table>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-state"><div class="icon">📭</div>No entry meetings today</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        with col_right:
            # Staff Meetings
            st.markdown('<div class="section-card"><div class="section-card-header navy"><h3>🤝 Staff Meetings</h3></div><div class="section-card-body">', unsafe_allow_html=True)
            if edit:
                df = pd.DataFrame(bulletin_data["staff_meetings"])
                edited = st.data_editor(df, key="sm_editor", hide_index=True, use_container_width=True)
                bulletin_data["staff_meetings"] = edited.to_dict("records")
            else:
                rows = bulletin_data["staff_meetings"]
                has_data = any(any(v for v in r.values()) for r in rows)
                if has_data:
                    st.markdown('<table class="data-table"><tr><th>Type</th><th>Staff</th><th>Location</th><th>Depart</th><th>Return</th><th>Student</th></tr>' +
                        "".join([f"<tr><td>{r.get('Type','')}</td><td>{r.get('Staff Member','')}</td><td>{r.get('Location','')}</td><td>{r.get('Time Departing','')}</td><td>{r.get('Time Returning','')}</td><td>{r.get('Student','')}</td></tr>"
                        for r in rows if any(v for v in r.values())]) + "</table>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-state"><div class="icon">📅</div>No staff meetings today</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

            # Additional Staff Messages
            st.markdown('<div class="section-card"><div class="section-card-header slate"><h3>💬 Additional Staff Messages</h3></div><div class="section-card-body">', unsafe_allow_html=True)
            if edit:
                df = pd.DataFrame(bulletin_data["additional_messages"])
                edited = st.data_editor(df, key="msg_editor", hide_index=True, use_container_width=True)
                bulletin_data["additional_messages"] = edited.to_dict("records")
            else:
                rows = bulletin_data["additional_messages"]
                has_data = any(any(v for v in r.values()) for r in rows)
                if has_data:
                    st.markdown('<table class="data-table"><tr><th>Staff</th><th>Visitor</th><th>Reason</th><th>Arriving/Departing</th></tr>' +
                        "".join([f"<tr><td>{r.get('Staff Member','')}</td><td>{r.get('Visitor','')}</td><td>{r.get('Reason','')}</td><td>{r.get('Arriving/Departing','')}</td></tr>"
                        for r in rows if any(v for v in r.values())]) + "</table>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-state"><div class="icon">💭</div>No additional messages</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    # TAB S2: Travel & Vehicles
    # ─────────────────────────────────────────────────────
    with s2:
        import pandas as pd
        jp_col, py_col, sy_col = st.columns(3)

        def render_travel_card(col, key, label, color):
            with col:
                st.markdown(f'<div class="section-card"><div class="section-card-header" style="background:{color};"><h3>{label}</h3></div><div class="section-card-body">', unsafe_allow_html=True)
                rows = bulletin_data[key]
                if edit:
                    df = pd.DataFrame(rows)
                    edited = st.data_editor(df, key=f"{key}_editor", hide_index=True, use_container_width=True)
                    bulletin_data[key] = edited.to_dict("records")
                else:
                    has_data = any(any(v for v in r.values()) for r in rows)
                    if has_data:
                        st.markdown('<table class="data-table"><tr><th>Student</th><th>To</th><th>From</th><th>Times</th></tr>' +
                            "".join([f"<tr><td>{r.get('Student','')}</td><td>{r.get('Transport To','')}</td><td>{r.get('Transport From','')}</td><td>{r.get('Times','')}</td></tr>"
                            for r in rows if any(v for v in r.values())]) + "</table>", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="empty-state"><div class="icon">🚐</div>No travel today</div>', unsafe_allow_html=True)
                st.markdown('</div></div>', unsafe_allow_html=True)

        render_travel_card(jp_col, "travel_jp", "🟦 Junior Primary – Travel", "#4a7fb5")
        render_travel_card(py_col, "travel_py", "🟣 Primary Years – Travel", "#7a5bb5")
        render_travel_card(sy_col, "travel_sy", "🟫 Senior Years – Travel", "#8c6a4f")

        # Vehicle bookings
        st.markdown('<div class="section-card"><div class="section-card-header navy"><h3>🚗 Vehicle Room Booking</h3></div><div class="section-card-body">', unsafe_allow_html=True)
        times = ["9:00","10:00","11:00","12:00","1:00","2:00","3:00"]
        vb = bulletin_data["vehicle_bookings"]

        if edit:
            v_cols = st.columns(7)
            new_vb = {}
            for i, t in enumerate(times):
                with v_cols[i]:
                    st.markdown(f"**{t}**")
                    new_vb[t] = {
                        "van": st.text_input("VAN", vb.get(t,{}).get("van",""), key=f"vb_van_{t}"),
                        "kia": st.text_input("KIA", vb.get(t,{}).get("kia",""), key=f"vb_kia_{t}"),
                    }
            bulletin_data["vehicle_bookings"] = new_vb
        else:
            has_vb = any(vb.get(t,{}).get("van","") or vb.get(t,{}).get("kia","") for t in times)
            if has_vb:
                rows_html = "".join([
                    f'<tr><td class="vehicle-time">{t}</td>'
                    f'<td>{"<span class=vehicle-booking>" + vb.get(t,{}).get("van","") + "</span>" if vb.get(t,{}).get("van","") else ""}</td>'
                    f'<td>{"<span class=vehicle-booking>" + vb.get(t,{}).get("kia","") + "</span>" if vb.get(t,{}).get("kia","") else ""}</td></tr>'
                    for t in times
                ])
                st.markdown(f'<table class="data-table"><tr><th>Time</th><th>VAN</th><th>KIA</th></tr>{rows_html}</table>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-state"><div class="icon">🚗</div>No vehicle bookings today</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    # TAB S3: Responsibilities & NIT
    # ─────────────────────────────────────────────────────
    with s3:
        resp_col, nit_col = st.columns([1, 1])

        with resp_col:
            st.markdown('<div class="section-card"><div class="section-card-header amber"><h3>⭐ Staff Responsibilities</h3></div><div class="section-card-body">', unsafe_allow_html=True)
            sr = bulletin_data["staff_responsibilities"]
            if edit:
                bulletin_data["staff_responsibilities"] = {
                    "kitchen_duties": st.text_input("🍳 Kitchen Duties", sr.get("kitchen_duties",""), key="sr_k"),
                    "meeting_pd_focus": st.text_input("📌 Staff Meeting PD Focus", sr.get("meeting_pd_focus",""), key="sr_pd"),
                    "chair": st.text_input("🪑 Meeting Chair", sr.get("chair",""), key="sr_c"),
                    "minutes": st.text_input("📝 Meeting Minutes", sr.get("minutes",""), key="sr_m"),
                }
            else:
                kitchen = sr.get("kitchen_duties","")
                st.markdown(f"""
                <table class="data-table">
                  <tr class="kitchen-row">
                    <td><span class="kitchen-badge">🍳 Kitchen</span></td>
                    <td><strong>{kitchen if kitchen else "—"}</strong></td>
                  </tr>
                  <tr><td>📌 PD Focus</td><td>{sr.get("meeting_pd_focus","") or "—"}</td></tr>
                  <tr><td>🪑 Chair</td><td>{sr.get("chair","") or "—"}</td></tr>
                  <tr><td>📝 Minutes</td><td>{sr.get("minutes","") or "—"}</td></tr>
                </table>""", unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        with nit_col:
            st.markdown('<div class="section-card"><div class="section-card-header green"><h3>📋 Additional NIT Booking</h3></div><div class="section-card-body">', unsafe_allow_html=True)
            if edit:
                bulletin_data["nit_booking"] = st.text_area("NIT Booking Details", value=bulletin_data.get("nit_booking",""), height=120, label_visibility="collapsed")
            else:
                nit = bulletin_data.get("nit_booking","")
                if nit:
                    st.markdown(f'<p style="font-size:0.85rem;color:#2a3a2a;line-height:1.6;">{nit}</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-state"><div class="icon">📋</div>No NIT bookings today</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    # TAB S4: Program Changes
    # ─────────────────────────────────────────────────────
    with s4:
        st.markdown('<div class="section-card"><div class="section-card-header navy"><h3>📊 Program Changes</h3></div><div class="section-card-body">', unsafe_allow_html=True)
        import pandas as pd
        pc_rows = bulletin_data["program_changes"]
        df = pd.DataFrame(pc_rows)

        if edit:
            edited = st.data_editor(df, key="pc_editor", hide_index=True, use_container_width=True,
                column_config={"Type": st.column_config.SelectboxColumn("Type",
                    options=["","Lunch break","NIT change","Addition NIT","Program Teacher"])})
            bulletin_data["program_changes"] = edited.to_dict("records")
        else:
            has_data = any(any(v for v in r.values()) for r in pc_rows)
            if has_data:
                st.markdown('<div class="pc-scroll">', unsafe_allow_html=True)
                headers = list(df.columns)
                header_html = "".join([f"<th>{h}</th>" for h in headers])
                rows_html = ""
                for r in pc_rows:
                    if any(v for v in r.values()):
                        cells = ""
                        for h in headers:
                            val = r.get(h,"")
                            is_time = ":" in h and "-" in h
                            cls = "timeslot filled" if (is_time and val) else ("timeslot" if is_time else "")
                            cells += f'<td class="{cls}">{val}</td>'
                        rows_html += f"<tr>{cells}</tr>"
                st.markdown(f'<table class="data-table pc-table"><tr>{header_html}</tr>{rows_html}</table></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-state"><div class="icon">📊</div>No program changes today</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        # ── Staff Notices card ──
        b_notices = load_notices(for_date=current_date)
        if b_notices or edit:
            st.markdown('<div class="section-card"><div class="section-card-header green"><h3>📝 Staff Notices</h3></div><div class="section-card-body">', unsafe_allow_html=True)
            if b_notices:
                for n in b_notices:
                    cat = n.get("category","General")
                    nc  = NOTICE_CATS.get(cat, NOTICE_CATS["General"])
                    nid = n.get("id","")
                    nc1, nc2 = st.columns([9,1])
                    with nc1:
                        st.markdown(
                            f'<div style="background:white;border-radius:10px;border-left:4px solid {nc["color"]};'
                            f'padding:0.75rem 1rem;margin-bottom:0.5rem;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
                            f'<div style="margin-bottom:0.2rem;">'
                            f'<span style="background:{nc["bg"]};color:{nc["color"]};font-size:0.65rem;'
                            f'font-weight:700;text-transform:uppercase;letter-spacing:0.08em;'
                            f'padding:0.15rem 0.5rem;border-radius:20px;">{nc["emoji"]} {cat}</span>'
                            f'<span style="font-size:0.7rem;color:#9ab09a;margin-left:0.5rem;">from {n.get("submitted_by","")}</span>'
                            f'</div>'
                            f'<div style="font-size:0.9rem;font-weight:700;color:#1a2e44;margin:0.3rem 0 0.2rem;">{n.get("title","")}</div>'
                            f'<div style="font-size:0.82rem;color:#3a4a3a;line-height:1.5;">{n.get("body","")}</div>'
                            f'</div>',
                            unsafe_allow_html=True)
                    with nc2:
                        if edit:
                            st.write("")
                            if st.button("🗑️", key=f"del_n_{nid}", help="Delete notice"):
                                delete_notice(nid); st.rerun()
            else:
                st.markdown('<div style="text-align:center;padding:1.5rem;color:#9ab09a;font-size:0.85rem;">No notices today — staff can add via the 📝 Quick Add tab</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # end content-area

    # ── SAVE EXECUTION — runs here so all data_editors above have already
    # updated bulletin_data before we write to the database ──────────────
    if st.session_state.get("_pending_save"):
        st.session_state["_pending_save"] = False
        save_data = {k: v for k, v in bulletin_data.items() if k != "id"}
        db.save_bulletin(current_date, save_data)
        st.session_state.edit_mode = False
        st.success("✅ Bulletin saved!")
        if st.query_params.get("from_display") == "true":
            st.markdown('<meta http-equiv="refresh" content="2;url=/?display=true">', unsafe_allow_html=True)
            st.info("↩️ Returning to staff room display in 2 seconds...")
        st.rerun()



# ══════════════════════════════════════════════════════════════
# TAB: QUICK ADD
# ══════════════════════════════════════════════════════════════
with quickadd_tab:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#3d7a28,#6BBF4E);border-radius:14px;
    padding:1.5rem 2rem;margin-bottom:1.5rem;color:white;">
      <div style="font-size:1.3rem;font-weight:700;margin-bottom:0.3rem;">📝 Add a Staff Notice</div>
      <div style="font-size:0.85rem;opacity:0.85;">No password needed. Your notice will appear on today's bulletin
      and the staff room display screen straight away.</div>
    </div>
    """, unsafe_allow_html=True)

    qa_col, preview_col = st.columns([1, 1])

    with qa_col:
        with st.form("quick_add_form", clear_on_submit=True):
            qa_name = st.text_input("Your name *", placeholder="e.g. Sarah")
            qa_cat  = st.selectbox("Category *", list(NOTICE_CATS.keys()))
            qa_title = st.text_input("Title *", placeholder="e.g. Staff meeting moved to Room 3")
            qa_body  = st.text_area("Details", placeholder="Any additional info… (optional)", height=120)
            qa_date  = st.date_input("For which day?", value=date.today())
            qa_ok    = st.form_submit_button("📢 Post Notice", type="primary", use_container_width=True)
            if qa_ok:
                if not qa_name.strip():
                    st.warning("Please enter your name.")
                elif not qa_title.strip():
                    st.warning("Please enter a title.")
                else:
                    save_notice({
                        "submitted_by": qa_name.strip(),
                        "category":     qa_cat,
                        "title":        qa_title.strip(),
                        "body":         qa_body.strip(),
                        "notice_date":  str(qa_date),
                    })
                    st.success(f"✅ Notice posted for {qa_date.strftime('%-d %B')}! It's now live on the bulletin.")
                    st.balloons()

    with preview_col:
        st.markdown("**Category guide:**")
        for cat, cfg in NOTICE_CATS.items():
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem;">'
                f'<span style="background:{cfg["bg"]};color:{cfg["color"]};font-size:0.72rem;'
                f'font-weight:700;padding:0.2rem 0.6rem;border-radius:20px;min-width:90px;'
                f'text-align:center;">{cfg["emoji"]} {cat}</span>'
                f'</div>',
                unsafe_allow_html=True)

    # ── Today's notices listed below ──
    st.markdown("---")
    st.markdown(f"**Notices posted for {date.today().strftime('%A %-d %B')}:**")
    listed = load_notices(for_date=date.today())
    if not listed:
        st.markdown('<div style="text-align:center;padding:2rem;color:#9ab09a;font-size:0.85rem;">No notices yet today — be the first!</div>', unsafe_allow_html=True)
    else:
        for n in listed:
            cat = n.get("category","General")
            nc  = NOTICE_CATS.get(cat, NOTICE_CATS["General"])
            nid = n.get("id","")
            nl1, nl2 = st.columns([9,1])
            with nl1:
                st.markdown(
                    f'<div style="background:white;border-radius:10px;border-left:4px solid {nc["color"]};'
                    f'padding:0.75rem 1rem;margin-bottom:0.5rem;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
                    f'<div style="margin-bottom:0.2rem;">'
                    f'<span style="background:{nc["bg"]};color:{nc["color"]};font-size:0.65rem;'
                    f'font-weight:700;text-transform:uppercase;letter-spacing:0.08em;'
                    f'padding:0.15rem 0.5rem;border-radius:20px;">{nc["emoji"]} {cat}</span>'
                    f'<span style="font-size:0.7rem;color:#9ab09a;margin-left:0.5rem;">from {n.get("submitted_by","")}</span>'
                    f'</div>'
                    f'<div style="font-size:0.9rem;font-weight:700;color:#1a2e44;margin:0.3rem 0 0.2rem;">{n.get("title","")}</div>'
                    f'<div style="font-size:0.82rem;color:#3a4a3a;line-height:1.5;">{n.get("body","") or ""}</div>'
                    f'</div>',
                    unsafe_allow_html=True)
            with nl2:
                st.write("")
                if st.session_state.authenticated:
                    if st.button("🗑️", key=f"qa_del_{nid}", help="Delete"):
                        delete_notice(nid); st.rerun()

# ══════════════════════════════════════════════════════════════
# TAB: ARCHIVE
# ══════════════════════════════════════════════════════════════
with archive_tab:
    st.markdown("### 🗂️ Bulletin Archive")
    a1, a2 = st.tabs(["Browse by Week / Term", "Search"])

    with a1:
        c1, c2 = st.columns(2)
        with c1:
            browse_date = st.date_input("Select a date", value=date.today(), key="archive_date")
        with c2:
            browse_mode = st.selectbox("Browse by", ["Week", "Term"])

        y = browse_date.year
        terms_map = {1:(date(y,1,28),date(y,4,11)), 2:(date(y,4,28),date(y,7,4)),
                     3:(date(y,7,21),date(y,9,26)), 4:(date(y,10,13),date(y,12,12))}

        if browse_mode == "Week":
            wk = week_dates(browse_date)
            results = db.get_bulletins_range(wk[0], wk[-1])
            st.markdown(f"**Week of {wk[0].strftime('%-d %b %Y')}**")
        else:
            t_start = t_end = None
            for t,(s,e) in terms_map.items():
                if s <= browse_date <= e:
                    t_start, t_end = s, e
                    st.markdown(f"**Term {t}, {y}**")
                    break
            results = db.get_bulletins_range(t_start, t_end) if t_start else []
            if not t_start:
                st.info("Date is outside term dates.")

        if results:
            for row in results:
                d = datetime.strptime(row["date"], "%Y-%m-%d").date()
                label = d.strftime("%A %-d %B %Y")
                fact = row.get("fun_fact","")
                st.markdown(f'<div class="arch-card"><div class="arch-card-date">{label}</div><div class="arch-card-fact">💡 {fact if fact else "No fun fact recorded"}</div></div>', unsafe_allow_html=True)
                if st.button(f"Open →", key=f"arch_{row['date']}"):
                    st.session_state.selected_date = d
                    st.rerun()
        else:
            st.markdown('<div class="empty-state"><div class="icon">📭</div>No bulletins found for this period</div>', unsafe_allow_html=True)

    with a2:
        keyword = st.text_input("🔍 Search all bulletins", placeholder="Enter staff name, student, excursion, note...")
        if keyword and len(keyword) >= 2:
            results = db.search_bulletins(keyword)
            if results:
                st.markdown(f"**{len(results)} result(s) found for '{keyword}'**")
                for row in results:
                    d = datetime.strptime(row["date"], "%Y-%m-%d").date()
                    label = d.strftime("%A %-d %B %Y")
                    st.markdown(f'<div class="arch-card"><div class="arch-card-date">{label}</div></div>', unsafe_allow_html=True)
                    if st.button(f"Open →", key=f"search_{row['date']}"):
                        st.session_state.selected_date = d
                        st.rerun()
            else:
                st.markdown(f'<div class="empty-state"><div class="icon">🔍</div>No results for "{keyword}"</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB: STAFF LOGIN
# ══════════════════════════════════════════════════════════════
with login_tab:
    if st.session_state.authenticated:
        st.success("✅ You are logged in as Staff")
        st.markdown(f"You can now edit bulletins — head to the **📋 Bulletin** tab and click **✏️ Edit**.")
        if st.button("🚪 Logout", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.edit_mode = False
            st.rerun()
    else:
        st.markdown('<div class="auth-gate">', unsafe_allow_html=True)
        st.markdown("### 🔐 Staff Login")
        st.markdown("Login to create and edit daily bulletins.")
        pw = st.text_input("Password", type="password", placeholder="Enter staff password")
        if st.button("Login", type="primary", use_container_width=True):
            if pw == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("✅ Logged in! Go to the Bulletin tab to start editing.")
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.markdown('</div>', unsafe_allow_html=True)

