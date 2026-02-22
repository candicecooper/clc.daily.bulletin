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
page_tab, archive_tab, login_tab = st.tabs(["📋 Bulletin", "🗂️ Archive", "🔐 Staff"])

# ══════════════════════════════════════════════════════════════
# TAB: BULLETIN
# ══════════════════════════════════════════════════════════════
with page_tab:

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

    # ── Week day selector ──
    st.markdown('<div style="background:white;border-bottom:2px solid #e8f0e3;padding:0 1rem;">', unsafe_allow_html=True)
    day_cols = st.columns(5)
    for i, d in enumerate(week):
        with day_cols[i]:
            is_current = d == current_date
            btn_type = "primary" if is_current else "secondary"
            if st.button(d.strftime("%a %-d %b"), key=f"day_{d}", use_container_width=True, type=btn_type):
                st.session_state.selected_date = d
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Edit controls ──
    if st.session_state.authenticated:
        ctrl_cols = st.columns([1,1,6])
        with ctrl_cols[0]:
            if st.button("✏️ Edit" if not edit else "👁️ View", type="primary" if not edit else "secondary", use_container_width=True):
                st.session_state.edit_mode = not st.session_state.edit_mode
                st.rerun()
        with ctrl_cols[1]:
            if edit:
                if st.button("💾 Save", type="primary", use_container_width=True):
                    save_data = {k:v for k,v in bulletin_data.items() if k != "id"}
                    db.save_bulletin(current_date, save_data)
                    st.session_state.edit_mode = False
                    st.success("✅ Bulletin saved!")
                    st.rerun()

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

    st.markdown('</div>', unsafe_allow_html=True)  # end content-area


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
