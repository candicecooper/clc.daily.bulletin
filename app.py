import streamlit as st
from datetime import date, timedelta, datetime
import database as db
import json
import calendar

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="CLC Daily Bulletin",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Brand colours ─────────────────────────────────────────────
st.markdown("""
<style>
  /* Brand colours */
  :root {
    --green: #6BBF4E;
    --green-dark: #4a8f33;
    --brown: #A67C6A;
    --navy: #1a2e44;
    --amber: #e8a125;
    --white: #ffffff;
  }

  /* Hide Streamlit chrome */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  .stDeployButton {display: none;}

  /* Header banner */
  .bulletin-header {
    background: linear-gradient(135deg, #4a8f33, #6BBF4E);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  .bulletin-header h1 {
    color: white;
    font-size: 1.6rem;
    margin: 0;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }
  .bulletin-header .date-sub {
    color: rgba(255,255,255,0.85);
    font-size: 0.9rem;
    margin-top: 0.2rem;
  }
  .fun-fact {
    background: #fffbe6;
    border-left: 4px solid #e8a125;
    padding: 0.5rem 1rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.85rem;
    color: #7a5800;
    margin-bottom: 1rem;
  }

  /* Section headers */
  .section-header {
    background: #6BBF4E;
    color: white;
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.4rem 0.75rem;
    border-radius: 6px 6px 0 0;
    margin-bottom: 0;
  }
  .section-header.brown { background: #A67C6A; }
  .section-header.navy  { background: #1a2e44; }
  .section-header.amber { background: #e8a125; color: #1a2e44; }

  /* Tables */
  .bulletin-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.78rem;
    margin-bottom: 1rem;
    border: 1px solid #ddd;
    border-radius: 0 0 6px 6px;
    overflow: hidden;
  }
  .bulletin-table th {
    background: #e8f5e1;
    color: #2d6b1a;
    font-weight: 700;
    padding: 0.35rem 0.5rem;
    text-align: left;
    border: 1px solid #c5deba;
    font-size: 0.72rem;
    text-transform: uppercase;
  }
  .bulletin-table td {
    padding: 0.3rem 0.5rem;
    border: 1px solid #e0e0e0;
    background: white;
    vertical-align: top;
  }
  .bulletin-table tr:nth-child(even) td { background: #f9fdf6; }

  /* Kitchen duties highlight */
  .kitchen-highlight {
    background: #e8a125 !important;
    color: #1a2e44;
    font-weight: 700;
  }

  /* Nav pills */
  .day-nav {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }

  /* Edit mode indicator */
  .edit-badge {
    background: #e8a125;
    color: #1a2e44;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    display: inline-block;
    margin-left: 0.5rem;
  }

  /* Archive card */
  .archive-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid #6BBF4E;
    cursor: pointer;
    transition: box-shadow 0.15s;
  }
  .archive-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

  /* Responsive */
  @media (max-width: 768px) {
    .bulletin-header h1 { font-size: 1.1rem; }
    .bulletin-table { font-size: 0.68rem; }
  }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()
if "page" not in st.session_state:
    st.session_state.page = "bulletin"  # bulletin | archive | login

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "clcstaff2026")

# ── Helpers ───────────────────────────────────────────────────
def week_dates(d: date):
    """Return Mon-Fri for the week containing d."""
    monday = d - timedelta(days=d.weekday())
    return [monday + timedelta(days=i) for i in range(5)]

def term_label(d: date):
    """Very rough SA term detection."""
    y = d.year
    terms = {
        1: (date(y, 1, 28), date(y, 4, 11)),
        2: (date(y, 4, 28), date(y, 7, 4)),
        3: (date(y, 7, 21), date(y, 9, 26)),
        4: (date(y, 10, 13), date(y, 12, 12)),
    }
    for t, (start, end) in terms.items():
        if start <= d <= end:
            return f"Term {t}, {y}"
    return str(y)

def empty_rows(n=5):
    return [{"col1": "", "col2": "", "col3": "", "col4": "", "col5": "", "col6": ""} for _ in range(n)]

def fmt_date(d: date):
    return d.strftime("%A %-d %B %Y").upper()

# ── Default bulletin structure ────────────────────────────────
def default_bulletin():
    return {
        "fun_fact": "",
        "staff_absent": [{"staff_absence": "", "trt": "", "student_absence": "", "program": "", "reason": ""} for _ in range(4)],
        "excursions": [{"program": "", "staff_member": "", "time_departing": "", "time_returning": "", "location": ""} for _ in range(4)],
        "staff_meetings": [{"type_of_meeting": "", "staff_member": "", "location": "", "time_departing": "", "time_returning": "", "student": ""} for _ in range(4)],
        "entry_meetings": [{"time": "", "program": "", "student": ""} for _ in range(4)],
        "additional_messages": [{"staff_member": "", "visitor": "", "reason": "", "arriving_departing": ""} for _ in range(4)],
        "travel_jp": [{"student": "", "transport_to": "", "transport_from": "", "times": ""} for _ in range(6)],
        "travel_py": [{"student": "", "transport_to": "", "transport_from": "", "times": ""} for _ in range(6)],
        "travel_sy": [{"student": "", "transport_to": "", "transport_from": "", "times": ""} for _ in range(5)],
        "vehicle_bookings": {t: {"van": "", "kia": ""} for t in ["9:00","10:00","11:00","12:00","1:00","2:00","3:00"]},
        "staff_responsibilities": {
            "kitchen_duties": "",
            "meeting_pd_focus": "",
            "chair": "",
            "minutes": ""
        },
        "nit_booking": "",
        "program_changes": [
            {"trt": "", "clc_responsibility": "", "type": "", "clc_staff_absent": "",
             "jp": "", "py": "", "sy": "", "nit": "",
             "t0900": "", "t0930": "", "t1000": "", "t1030": "", "t1100": "",
             "t1130": "", "t1200": "", "t1230": "", "t1300": "", "t1330": "",
             "t1400": "", "t1430": "", "t1500": ""}
            for _ in range(5)
        ]
    }

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/6BBF4E/FFFFFF?text=CLC+Bulletin", use_container_width=True)
    st.markdown("---")

    # Page navigation
    page_choice = st.radio("Navigate", ["📋 Today's Bulletin", "🗂️ Archive", "🔐 Staff Login"], label_visibility="collapsed")
    if "Bulletin" in page_choice:
        st.session_state.page = "bulletin"
    elif "Archive" in page_choice:
        st.session_state.page = "archive"
    elif "Login" in page_choice:
        st.session_state.page = "login"

    st.markdown("---")

    # Date picker
    st.markdown("**📅 Select Date**")
    selected = st.date_input("Date", value=st.session_state.selected_date, label_visibility="collapsed")
    st.session_state.selected_date = selected

    # Week navigation buttons
    week = week_dates(selected)
    st.markdown("**This Week**")
    for d in week:
        label = d.strftime("%a %-d %b")
        is_selected = d == selected
        if st.button(label, key=f"nav_{d}", use_container_width=True,
                     type="primary" if is_selected else "secondary"):
            st.session_state.selected_date = d
            st.session_state.page = "bulletin"
            st.rerun()

    st.markdown("---")

    # Auth status
    if st.session_state.authenticated:
        st.success("✅ Logged in as Staff")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.edit_mode = False
            st.rerun()
        if st.session_state.page == "bulletin":
            edit_label = "💾 Save & Exit Edit" if st.session_state.edit_mode else "✏️ Edit Bulletin"
            if st.button(edit_label, use_container_width=True, type="primary"):
                st.session_state.edit_mode = not st.session_state.edit_mode
                st.rerun()
    else:
        st.info("🔒 View only — login to edit")


# ── LOAD BULLETIN DATA ────────────────────────────────────────
current_date = st.session_state.selected_date
bulletin_data = db.get_bulletin(current_date)
if bulletin_data:
    # Merge with defaults to handle missing keys
    defaults = default_bulletin()
    for k, v in defaults.items():
        if k not in bulletin_data:
            bulletin_data[k] = v
else:
    bulletin_data = default_bulletin()
    bulletin_data["date"] = str(current_date)


# ══════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "login":
    st.markdown("## 🔐 Staff Login")
    st.markdown("Enter the staff password to create and edit bulletins.")
    with st.form("login_form"):
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login", type="primary"):
            if pw == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.page = "bulletin"
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")


# ══════════════════════════════════════════════════════════════
# PAGE: ARCHIVE
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "archive":
    st.markdown("## 🗂️ Bulletin Archive")

    tab1, tab2 = st.tabs(["Browse by Week / Term", "Search"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            browse_date = st.date_input("Select any date in the week/term", value=date.today())
        with col2:
            browse_mode = st.selectbox("View by", ["Week", "Term"])

        if browse_mode == "Week":
            wk = week_dates(browse_date)
            results = db.get_bulletins_range(wk[0], wk[-1])
            st.markdown(f"**Week of {wk[0].strftime('%-d %b %Y')}**")
        else:
            y = browse_date.year
            terms = {
                1: (date(y, 1, 28), date(y, 4, 11)),
                2: (date(y, 4, 28), date(y, 7, 4)),
                3: (date(y, 7, 21), date(y, 9, 26)),
                4: (date(y, 10, 13), date(y, 12, 12)),
            }
            t_start, t_end = None, None
            for t, (s, e) in terms.items():
                if s <= browse_date <= e:
                    t_start, t_end = s, e
                    st.markdown(f"**Term {t}, {y}**")
                    break
            if t_start:
                results = db.get_bulletins_range(t_start, t_end)
            else:
                results = []
                st.info("Date is outside term dates. Try adjusting.")

        if results:
            for row in results:
                d = datetime.strptime(row["date"], "%Y-%m-%d").date()
                label = d.strftime("%A %-d %B %Y")
                fact = row.get("fun_fact", "")
                with st.container():
                    st.markdown(f"""
                    <div class="archive-card">
                        <strong>{label}</strong><br>
                        <span style="color:#666;font-size:0.8rem;">💡 {fact if fact else 'No fun fact recorded'}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Open {label}", key=f"open_{row['date']}"):
                        st.session_state.selected_date = d
                        st.session_state.page = "bulletin"
                        st.rerun()
        else:
            st.info("No bulletins found for this period.")

    with tab2:
        keyword = st.text_input("🔍 Search bulletins", placeholder="e.g. staff name, excursion, note...")
        if keyword and len(keyword) >= 2:
            results = db.search_bulletins(keyword)
            if results:
                st.markdown(f"**{len(results)} result(s) found**")
                for row in results:
                    d = datetime.strptime(row["date"], "%Y-%m-%d").date()
                    label = d.strftime("%A %-d %B %Y")
                    st.markdown(f"""
                    <div class="archive-card">
                        <strong>{label}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"View {label}", key=f"search_{row['date']}"):
                        st.session_state.selected_date = d
                        st.session_state.page = "bulletin"
                        st.rerun()
            else:
                st.info(f"No bulletins found matching '{keyword}'.")
        elif keyword:
            st.caption("Type at least 2 characters to search.")


# ══════════════════════════════════════════════════════════════
# PAGE: BULLETIN (view or edit)
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "bulletin":

    edit = st.session_state.edit_mode and st.session_state.authenticated

    # ── Header ──
    edit_badge = '<span class="edit-badge">EDIT MODE</span>' if edit else ''
    st.markdown(f"""
    <div class="bulletin-header">
        <div>
            <h1>Cowandilla Learning Centre — Daily Bulletin {edit_badge}</h1>
            <div class="date-sub">{fmt_date(current_date)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fun fact
    if edit:
        bulletin_data["fun_fact"] = st.text_input("💡 Fun Fact", value=bulletin_data.get("fun_fact", ""), placeholder="Enter today's fun fact...")
    else:
        fact = bulletin_data.get("fun_fact", "")
        if fact:
            st.markdown(f'<div class="fun-fact">💡 <strong>Fun Fact:</strong> {fact}</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # ROW 1: Staff/Student Absent | Excursions | Staff Meetings | Entry Meetings | Additional Messages
    # ════════════════════════════════════════════════════════
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2.5, 1.5, 2])

    # ── Staff & Student Absent ──
    with c1:
        st.markdown('<div class="section-header">Staff and Student Absent</div>', unsafe_allow_html=True)
        if edit:
            rows = bulletin_data["staff_absent"]
            new_rows = []
            for i, row in enumerate(rows):
                with st.expander(f"Entry {i+1}", expanded=i==0):
                    new_rows.append({
                        "staff_absence": st.text_input("Staff Absence", row.get("staff_absence",""), key=f"sa_s_{i}"),
                        "trt": st.text_input("TRT", row.get("trt",""), key=f"sa_t_{i}"),
                        "student_absence": st.text_input("Student Absence", row.get("student_absence",""), key=f"sa_stu_{i}"),
                        "program": st.text_input("Program", row.get("program",""), key=f"sa_p_{i}"),
                        "reason": st.text_input("Reason", row.get("reason",""), key=f"sa_r_{i}"),
                    })
            bulletin_data["staff_absent"] = new_rows
        else:
            st.markdown("""
            <table class="bulletin-table">
            <tr><th>Staff Absence</th><th>TRT</th><th>Student Absence</th><th>Program</th><th>Reason</th></tr>
            """ + "".join([
                f"<tr><td>{r.get('staff_absence','')}</td><td>{r.get('trt','')}</td><td>{r.get('student_absence','')}</td><td>{r.get('program','')}</td><td>{r.get('reason','')}</td></tr>"
                for r in bulletin_data["staff_absent"]
            ]) + "</table>", unsafe_allow_html=True)

    # ── Excursions ──
    with c2:
        st.markdown('<div class="section-header">Excursions</div>', unsafe_allow_html=True)
        if edit:
            rows = bulletin_data["excursions"]
            new_rows = []
            for i, row in enumerate(rows):
                with st.expander(f"Entry {i+1}", expanded=i==0):
                    new_rows.append({
                        "program": st.text_input("Program", row.get("program",""), key=f"ex_p_{i}"),
                        "staff_member": st.text_input("Staff Member", row.get("staff_member",""), key=f"ex_sm_{i}"),
                        "time_departing": st.text_input("Time Departing", row.get("time_departing",""), key=f"ex_td_{i}"),
                        "time_returning": st.text_input("Time Returning", row.get("time_returning",""), key=f"ex_tr_{i}"),
                        "location": st.text_input("Location", row.get("location",""), key=f"ex_l_{i}"),
                    })
            bulletin_data["excursions"] = new_rows
        else:
            st.markdown("""
            <table class="bulletin-table">
            <tr><th>Program</th><th>Staff</th><th>Departing</th><th>Returning</th><th>Location</th></tr>
            """ + "".join([
                f"<tr><td>{r.get('program','')}</td><td>{r.get('staff_member','')}</td><td>{r.get('time_departing','')}</td><td>{r.get('time_returning','')}</td><td>{r.get('location','')}</td></tr>"
                for r in bulletin_data["excursions"]
            ]) + "</table>", unsafe_allow_html=True)

    # ── Staff Meetings ──
    with c3:
        st.markdown('<div class="section-header">Staff Meetings</div>', unsafe_allow_html=True)
        if edit:
            rows = bulletin_data["staff_meetings"]
            new_rows = []
            for i, row in enumerate(rows):
                with st.expander(f"Entry {i+1}", expanded=i==0):
                    new_rows.append({
                        "type_of_meeting": st.text_input("Type", row.get("type_of_meeting",""), key=f"sm_t_{i}"),
                        "staff_member": st.text_input("Staff Member", row.get("staff_member",""), key=f"sm_s_{i}"),
                        "location": st.text_input("Location", row.get("location",""), key=f"sm_l_{i}"),
                        "time_departing": st.text_input("Time Departing", row.get("time_departing",""), key=f"sm_td_{i}"),
                        "time_returning": st.text_input("Time Returning", row.get("time_returning",""), key=f"sm_tr_{i}"),
                        "student": st.text_input("Student", row.get("student",""), key=f"sm_stu_{i}"),
                    })
            bulletin_data["staff_meetings"] = new_rows
        else:
            st.markdown("""
            <table class="bulletin-table">
            <tr><th>Type</th><th>Staff</th><th>Location</th><th>Depart</th><th>Return</th><th>Student</th></tr>
            """ + "".join([
                f"<tr><td>{r.get('type_of_meeting','')}</td><td>{r.get('staff_member','')}</td><td>{r.get('location','')}</td><td>{r.get('time_departing','')}</td><td>{r.get('time_returning','')}</td><td>{r.get('student','')}</td></tr>"
                for r in bulletin_data["staff_meetings"]
            ]) + "</table>", unsafe_allow_html=True)

    # ── Entry Meetings ──
    with c4:
        st.markdown('<div class="section-header brown">Entry Meetings – Annette</div>', unsafe_allow_html=True)
        if edit:
            rows = bulletin_data["entry_meetings"]
            new_rows = []
            for i, row in enumerate(rows):
                with st.expander(f"Entry {i+1}", expanded=i==0):
                    new_rows.append({
                        "time": st.text_input("Time", row.get("time",""), key=f"em_t_{i}"),
                        "program": st.text_input("Program", row.get("program",""), key=f"em_p_{i}"),
                        "student": st.text_input("Student", row.get("student",""), key=f"em_s_{i}"),
                    })
            bulletin_data["entry_meetings"] = new_rows
        else:
            st.markdown("""
            <table class="bulletin-table">
            <tr><th>Time</th><th>Program</th><th>Student</th></tr>
            """ + "".join([
                f"<tr><td>{r.get('time','')}</td><td>{r.get('program','')}</td><td>{r.get('student','')}</td></tr>"
                for r in bulletin_data["entry_meetings"]
            ]) + "</table>", unsafe_allow_html=True)

    # ── Additional Staff Messages ──
    with c5:
        st.markdown('<div class="section-header navy">Additional Staff Messages</div>', unsafe_allow_html=True)
        if edit:
            rows = bulletin_data["additional_messages"]
            new_rows = []
            for i, row in enumerate(rows):
                with st.expander(f"Entry {i+1}", expanded=i==0):
                    new_rows.append({
                        "staff_member": st.text_input("Staff Member", row.get("staff_member",""), key=f"am_sm_{i}"),
                        "visitor": st.text_input("Visitor", row.get("visitor",""), key=f"am_v_{i}"),
                        "reason": st.text_input("Reason", row.get("reason",""), key=f"am_r_{i}"),
                        "arriving_departing": st.text_input("Arriving/Departing", row.get("arriving_departing",""), key=f"am_ad_{i}"),
                    })
            bulletin_data["additional_messages"] = new_rows
        else:
            st.markdown("""
            <table class="bulletin-table">
            <tr><th>Staff</th><th>Visitor</th><th>Reason</th><th>Arriving/Departing</th></tr>
            """ + "".join([
                f"<tr><td>{r.get('staff_member','')}</td><td>{r.get('visitor','')}</td><td>{r.get('reason','')}</td><td>{r.get('arriving_departing','')}</td></tr>"
                for r in bulletin_data["additional_messages"]
            ]) + "</table>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # ROW 2: Travel Details (JP | PY | SY) | Vehicle Bookings | Staff Responsibilities
    # ════════════════════════════════════════════════════════
    t1, t2, t3, t4, t5 = st.columns([2, 2, 2, 1.5, 2])

    def render_travel(col, key_prefix, label, color):
        with col:
            st.markdown(f'<div class="section-header" style="background:{color};">{label} – Attendance & Travel</div>', unsafe_allow_html=True)
            rows = bulletin_data[key_prefix]
            if edit:
                new_rows = []
                for i, row in enumerate(rows):
                    with st.expander(f"Student {i+1}", expanded=False):
                        new_rows.append({
                            "student": st.text_input("Student", row.get("student",""), key=f"{key_prefix}_s_{i}"),
                            "transport_to": st.text_input("Transport To", row.get("transport_to",""), key=f"{key_prefix}_tt_{i}"),
                            "transport_from": st.text_input("Transport From", row.get("transport_from",""), key=f"{key_prefix}_tf_{i}"),
                            "times": st.text_input("Times", row.get("times",""), key=f"{key_prefix}_tm_{i}"),
                        })
                bulletin_data[key_prefix] = new_rows
            else:
                st.markdown("""
                <table class="bulletin-table">
                <tr><th>Student</th><th>To</th><th>From</th><th>Times</th></tr>
                """ + "".join([
                    f"<tr><td>{r.get('student','')}</td><td>{r.get('transport_to','')}</td><td>{r.get('transport_from','')}</td><td>{r.get('times','')}</td></tr>"
                    for r in rows
                ]) + "</table>", unsafe_allow_html=True)

    render_travel(t1, "travel_jp", "Junior Primary", "#4a7fb5")
    render_travel(t2, "travel_py", "Primary Years", "#6a4fb5")
    render_travel(t3, "travel_sy", "Senior Years", "#8c6a4f")

    # ── Vehicle Room Booking ──
    with t4:
        st.markdown('<div class="section-header navy">Vehicle Room Booking</div>', unsafe_allow_html=True)
        vb = bulletin_data["vehicle_bookings"]
        times = ["9:00","10:00","11:00","12:00","1:00","2:00","3:00"]
        if edit:
            new_vb = {}
            for t in times:
                st.markdown(f"**{t}**")
                cols = st.columns(2)
                new_vb[t] = {
                    "van": cols[0].text_input("VAN", vb.get(t, {}).get("van",""), key=f"vb_van_{t}"),
                    "kia": cols[1].text_input("KIA", vb.get(t, {}).get("kia",""), key=f"vb_kia_{t}"),
                }
            bulletin_data["vehicle_bookings"] = new_vb
        else:
            rows_html = "".join([
                f"<tr><td><strong>{t}</strong></td><td>{vb.get(t,{}).get('van','')}</td><td>{vb.get(t,{}).get('kia','')}</td></tr>"
                for t in times
            ])
            st.markdown(f"""
            <table class="bulletin-table">
            <tr><th>Time</th><th>VAN</th><th>KIA</th></tr>
            {rows_html}
            </table>""", unsafe_allow_html=True)

    # ── Staff Responsibilities ──
    with t5:
        st.markdown('<div class="section-header amber">Staff Responsibilities</div>', unsafe_allow_html=True)
        sr = bulletin_data["staff_responsibilities"]
        if edit:
            bulletin_data["staff_responsibilities"] = {
                "kitchen_duties": st.text_input("🍳 Kitchen Duties", sr.get("kitchen_duties",""), key="sr_kitchen"),
                "meeting_pd_focus": st.text_input("📌 Staff Meeting PD Focus", sr.get("meeting_pd_focus",""), key="sr_pd"),
                "chair": st.text_input("🪑 Staff Member – CHAIR", sr.get("chair",""), key="sr_chair"),
                "minutes": st.text_input("📝 Staff Member – MINUTES", sr.get("minutes",""), key="sr_minutes"),
            }
        else:
            kitchen = sr.get("kitchen_duties","")
            st.markdown(f"""
            <table class="bulletin-table">
            <tr><td class="kitchen-highlight" colspan="2">🍳 KITCHEN DUTIES</td><td class="kitchen-highlight"><strong>{kitchen}</strong></td></tr>
            <tr><td colspan="2">Staff Meeting PD Focus</td><td>{sr.get('meeting_pd_focus','')}</td></tr>
            <tr><td colspan="2">Staff Member – CHAIR</td><td>{sr.get('chair','')}</td></tr>
            <tr><td colspan="2">Staff Member – MINUTES</td><td>{sr.get('minutes','')}</td></tr>
            </table>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # ROW 3: Additional NIT Booking
    # ════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">Additional NIT Booking</div>', unsafe_allow_html=True)
    if edit:
        bulletin_data["nit_booking"] = st.text_area("Additional NIT Booking", value=bulletin_data.get("nit_booking",""), height=60, label_visibility="collapsed")
    else:
        nit = bulletin_data.get("nit_booking","")
        st.markdown(f'<div style="background:white;border:1px solid #ddd;border-radius:0 0 6px 6px;padding:0.5rem 0.75rem;min-height:40px;font-size:0.85rem;margin-bottom:1rem;">{nit}</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # ROW 4: Program Changes
    # ════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">Program Changes</div>', unsafe_allow_html=True)

    time_slots = ["9:00–9:30","9:30–10:00","10:00–10:30","10:30–11:00","11:00–11:30",
                  "11:30–12:00","12:00–12:30","12:30–1:00","1:00–1:30","1:30–2:00",
                  "2:00–2:30","2:30–2:45"]
    slot_keys = ["t0900","t0930","t1000","t1030","t1100","t1130","t1200","t1230","t1300","t1330","t1400","t1430"]

    pc_rows = bulletin_data["program_changes"]
    if edit:
        new_pc = []
        for i, row in enumerate(pc_rows):
            st.markdown(f"**Program Change {i+1}**")
            cols = st.columns([1,1,1,1,0.5,0.5,0.5,0.5])
            entry = {
                "trt": cols[0].text_input("TRT", row.get("trt",""), key=f"pc_trt_{i}"),
                "clc_responsibility": cols[1].text_input("CLC Responsibility", row.get("clc_responsibility",""), key=f"pc_clc_{i}"),
                "type": cols[2].selectbox("Type", ["","Lunch break","NIT change","Addition NIT","Program Teacher"], index=["","Lunch break","NIT change","Addition NIT","Program Teacher"].index(row.get("type","")) if row.get("type","") in ["","Lunch break","NIT change","Addition NIT","Program Teacher"] else 0, key=f"pc_type_{i}"),
                "clc_staff_absent": cols[3].text_input("CLC Staff Absent", row.get("clc_staff_absent",""), key=f"pc_absent_{i}"),
                "jp": cols[4].text_input("JP", row.get("jp",""), key=f"pc_jp_{i}"),
                "py": cols[5].text_input("PY", row.get("py",""), key=f"pc_py_{i}"),
                "sy": cols[6].text_input("SY", row.get("sy",""), key=f"pc_sy_{i}"),
                "nit": cols[7].text_input("NIT", row.get("nit",""), key=f"pc_nit_{i}"),
            }
            ts_cols = st.columns(len(slot_keys))
            for j, (sk, sl) in enumerate(zip(slot_keys, time_slots)):
                entry[sk] = ts_cols[j].text_input(sl, row.get(sk,""), key=f"pc_{sk}_{i}")
            new_pc.append(entry)
            st.markdown("---")
        bulletin_data["program_changes"] = new_pc
    else:
        # Display as scrollable table
        header_cells = "<th>TRT</th><th>CLC Resp.</th><th>Type</th><th>CLC Absent</th><th>JP</th><th>PY</th><th>SY</th><th>NIT</th>" + "".join([f"<th>{sl}</th>" for sl in time_slots])
        rows_html = ""
        for row in pc_rows:
            cells = f"<td>{row.get('trt','')}</td><td>{row.get('clc_responsibility','')}</td><td>{row.get('type','')}</td><td>{row.get('clc_staff_absent','')}</td><td>{row.get('jp','')}</td><td>{row.get('py','')}</td><td>{row.get('sy','')}</td><td>{row.get('nit','')}</td>"
            cells += "".join([f"<td>{row.get(sk,'')}</td>" for sk in slot_keys])
            rows_html += f"<tr>{cells}</tr>"
        st.markdown(f"""
        <div style="overflow-x:auto;">
        <table class="bulletin-table">
        <tr>{header_cells}</tr>
        {rows_html}
        </table>
        </div>""", unsafe_allow_html=True)

    # ── Save button ──────────────────────────────────────────
    if edit:
        st.markdown("---")
        col_save, col_cancel = st.columns([1, 3])
        with col_save:
            if st.button("💾 Save Bulletin", type="primary", use_container_width=True):
                save_data = {k: v for k, v in bulletin_data.items() if k != "id"}
                db.save_bulletin(current_date, save_data)
                st.session_state.edit_mode = False
                st.success("✅ Bulletin saved successfully!")
                st.rerun()
        with col_cancel:
            if st.button("✖ Cancel", use_container_width=True):
                st.session_state.edit_mode = False
                st.rerun()

    # ── Footer ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f'<div style="text-align:center;color:#999;font-size:0.75rem;">Cowandilla Learning Centre · Daily Bulletin · {term_label(current_date)}</div>',
        unsafe_allow_html=True
    )
