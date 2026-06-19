import streamlit as st
import streamlit.components.v1 as components
import json
import os

# Set up Streamlit page environment
st.set_page_config(
    page_title="Infinity Role Play Pakistan — LSPD",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide default Streamlit visual elements to maintain your clean interface
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding: 0px !important;}
    </style>
""", unsafe_allow_path=True)

DB_FILE = "lspd_roster.json"

# Helper function to load cloud data safely
def load_data():
    if not os.path.exists(DB_FILE):
        default_data = {
            "officers": [],
            "config": {"admin_pass": "lspd2024"}
        }
        with open(DB_FILE, 'w') as f:
            json.dump(default_data, f)
        return default_data
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"officers": [], "config": {"admin_pass": "lspd2024"}}

# Helper function to save cloud data safely
def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Handle back-end requests without breaking your original front-end architecture
if "action" in st.query_params:
    action = st.query_params["action"]
    data = load_data()
    
    if action == "get_officers":
        st.json(data["officers"])
        st.stop()
        
    elif action == "get_pass":
        st.json({"value": data["config"]["admin_pass"]})
        st.stop()
        
    elif action == "register_pass":
        # Handle Streamlit's structural API data format
        try:
            body = json.loads(st.context.headers.get("body", "{}"))
        except:
            body = {}
        if not body and hasattr(st, "experimental_get_query_params"):
            pass
        # Fallback to simple fallback parameter if parsing direct headers is strict
        new_pass = st.query_params.get("value", [""])[0]
        if new_pass:
            data["config"]["admin_pass"] = new_pass
            save_data(data)
        st.json({"success": True})
        st.stop()

# Embed your exact HTML UI, Stylesheet, and configurations verbatim
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Infinity Role Play Pakistan — LSPD</title>
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --navy:     #0D1B2A;
    --navy-mid: #1B2A4A;
    --navy-lt:  #243B55;
    --gold:     #C9A84C;
    --gold-lt:  #E8C97A;
    --green:    #1A7A3C;
    --green-lt: #27AE60;
    --red:      #C0392B;
    --amber:    #D4AC0D;
    --gray:     #8899AA;
    --bg:       #070E18;
    --card:     #111D2E;
    --border:   #1E3050;
    --text:     #D0DCE8;
    --text-dim: #6A80A0;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    min-height: 100vh;
  }

  /* ── HEADER ── */
  header {
    background: linear-gradient(135deg, #0D1B2A 0%, #1B2A4A 60%, #0D2A1A 100%);
    border-bottom: 2px solid var(--gold);
    padding: 0;
    position: relative;
    overflow: hidden;
  }

  header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      90deg,
      transparent,
      transparent 40px,
      rgba(201,168,76,0.03) 40px,
      rgba(201,168,76,0.03) 41px
    );
  }

  .header-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 28px 24px 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    position: relative;
  }

  .badge-icon {
    width: 72px;
    height: 72px;
    flex-shrink: 0;
  }

  .header-text h1 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--gold);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    line-height: 1.1;
  }

  .header-text h1 span { color: #27AE60; }

  .header-text p {
    font-size: 12px;
    color: var(--gray);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 5px;
  }

  /* ── NAV TABS ── */
  nav {
    background: var(--navy-mid);
    border-bottom: 1px solid var(--border);
  }

  .nav-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    gap: 0;
  }

  .nav-tab {
    padding: 14px 24px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--gray);
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
    user-select: none;
  }

  .nav-tab:hover { color: var(--text); }
  .nav-tab.active { color: var(--gold); border-bottom-color: var(--gold); }

  /* ── MAIN ── */
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 28px 24px;
  }

  .page { display: none; }
  .page.active { display: block; }

  /* ── SECTION HEADER ── */
  .section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }

  .section-head h2 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: var(--gold);
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, var(--gold), transparent);
  }

  /* ── CHAIN OF COMMAND ── */
  .chain-grid {
    display: flex;
    flex-direction: column;
    gap: 3px;
    margin-bottom: 36px;
  }

  .chain-row {
    display: flex;
    align-items: stretch;
    gap: 0;
    position: relative;
  }

  .chain-indent { flex-shrink: 0; }

  .chain-card {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 11px 16px;
    border-left: 3px solid var(--gold);
    background: var(--card);
    border-radius: 0 6px 6px 0;
    transition: background 0.15s;
    gap: 12px;
  }

  .chain-card:hover { background: #172030; }
  .chain-left { display: flex; align-items: center; gap: 12px; }

  .chain-num {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--text-dim);
    width: 20px;
    flex-shrink: 0;
  }

  .chain-rank {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 15px;
    color: var(--text);
  }

  .chain-abbr {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    background: var(--navy-mid);
    color: var(--gold);
    border: 1px solid var(--border);
    padding: 2px 7px;
    border-radius: 3px;
    flex-shrink: 0;
  }

  .chain-note {
    font-size: 12px;
    color: var(--text-dim);
    text-align: right;
    flex-shrink: 0;
  }

  /* rank colors */
  .rank-0 .chain-card { border-left-color: #C9A84C; }
  .rank-1 .chain-card { border-left-color: #B8956A; }
  .rank-2 .chain-card { border-left-color: #27AE60; }
  .rank-3 .chain-card { border-left-color: #2980B9; }
  .rank-4 .chain-card { border-left-color: #8E44AD; }
  .rank-5 .chain-card { border-left-color: #16A085; }
  .rank-6 .chain-card { border-left-color: #E67E22; }
  .rank-7 .chain-card { border-left-color: #E74C3C; }
  .rank-8 .chain-card { border-left-color: #95A5A6; }
  .rank-9 .chain-card { border-left-color: #7F8C8D; }
  .rank-10 .chain-card { border-left-color: #636E72; }

  /* ── ROSTER TABLE ── */
  .table-wrap {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid var(--border);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }

  thead tr { background: var(--navy-mid); }

  thead th {
    padding: 12px 14px;
    text-align: left;
    font-family: 'Rajdhani', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: var(--gold);
    letter-spacing: 1px;
    text-transform: uppercase;
    white-space: nowrap;
    border-bottom: 1px solid var(--border);
  }

  tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.15s;
  }

  tbody tr:hover { background: #131F30; }
  tbody td { padding: 11px 14px; color: var(--text); vertical-align: middle; }

  .badge-no { font-family: 'Share Tech Mono', monospace; color: var(--gold); font-size: 12px; }
  .officer-name { font-weight: 500; color: #E8F0F8; }
  .callsign { font-family: 'Share Tech Mono', monospace; font-size: 12px; color: var(--gold-lt); }

  .status-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  .status-Active    { background: rgba(26,122,60,0.2);  color: #2ECC71; border: 1px solid rgba(46,204,113,0.3); }
  .status-Inactive  { background: rgba(127,140,141,0.2); color: #95A5A6; border: 1px solid rgba(149,165,166,0.3); }
  .status-LOA       { background: rgba(212,172,13,0.2);  color: #F1C40F; border: 1px solid rgba(241,196,15,0.3); }
  .status-Suspended { background: rgba(192,57,43,0.2);   color: #E74C3C; border: 1px solid rgba(231,76,60,0.3); }
  .status-Terminated{ background: rgba(30,30,30,0.5);    color: #636E72; border: 1px solid rgba(99,110,114,0.3); }

  .empty-state { text-align: center; padding: 48px 24px; color: var(--text-dim); }

  /* ── BUTTONS ── */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 9px 18px;
    border-radius: 6px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.5px;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
    text-transform: uppercase;
  }

  .btn-gold { background: var(--gold); color: var(--navy); }
  .btn-gold:hover { background: var(--gold-lt); }
  .btn-outline { background: transparent; color: var(--gold); border: 1px solid var(--gold); }
  .btn-outline:hover { background: rgba(201,168,76,0.1); }
  .btn-danger { background: transparent; color: var(--red); border: 1px solid var(--red); padding: 5px 10px; font-size: 12px; }
  .btn-danger:hover { background: rgba(192,57,43,0.15); }
  .btn-edit { background: transparent; color: var(--gold); border: 1px solid var(--border); padding: 5px 10px; font-size: 12px; }
  .btn-edit:hover { border-color: var(--gold); }

  /* ── ADMIN PANEL ── */
  .admin-login-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    max-width: 900px;
    margin: 40px auto;
  }

  .admin-login {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 36px 32px;
    text-align: center;
  }

  .admin-login h2 {
    font-family: 'Rajdhani', sans-serif;
    color: var(--gold);
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 6px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .admin-login p { color: var(--text-dim); font-size: 13px; margin-bottom: 24px; }
  .form-group { margin-bottom: 16px; text-align: left; }
  .form-group label { display: block; font-size: 12px; color: var(--text-dim); margin-bottom: 6px; font-family: 'Rajdhani', sans-serif; letter-spacing: 1px; text-transform: uppercase; }
  
  .form-group input, .form-group select {
    width: 100%; background: var(--navy); border: 1px solid var(--border); border-radius: 6px; padding: 10px 12px; color: var(--text); font-family: 'Inter', sans-serif; font-size: 13px; outline: none;
  }
  .form-group input:focus, .form-group select:focus { border-color: var(--gold); }
  
  .admin-panel { display: none; }
  .admin-panel.visible { display: block; }
  .admin-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }

  /* ── MODAL ── */
  .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 100; align-items: center; justify-content: center; }
  .modal-overlay.open { display: flex; }
  .modal { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 28px; width: 100%; max-width: 520px; }
  .modal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
  .modal-header h3 { font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 700; color: var(--gold); text-transform: uppercase; letter-spacing: 1px; }
  .modal-close { background: none; border: none; color: var(--text-dim); font-size: 22px; cursor: pointer; }
  .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

  /* ── STATS BAR ── */
  .stats-bar { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
  .stat-card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; flex: 1; text-align: center; }
  .stat-card .stat-num { font-family: 'Rajdhani', sans-serif; font-size: 28px; font-weight: 700; color: var(--gold); line-height: 1; }
  .stat-card .stat-label { font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

  .error-msg { color: var(--red); font-size: 12px; margin-top: 8px; display: none; }
  .logout-btn { background: none; border: 1px solid var(--border); color: var(--text-dim); padding: 7px 14px; border-radius: 6px; font-family: 'Rajdhani', sans-serif; font-size: 13px; cursor: pointer; }
  
  footer { text-align: center; padding: 24px; color: var(--text-dim); font-size: 11px; border-top: 1px solid var(--border); margin-top: 48px; text-transform: uppercase; }
  footer span { color: var(--gold); }
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <svg class="badge-icon" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
      <polygon points="36,4 46,16 62,14 62,30 72,40 62,50 62,66 46,64 36,68 26,64 10,66 10,50 0,40 10,30 10,14 26,16" fill="#1B2A4A" stroke="#C9A84C" stroke-width="2"/>
      <polygon points="36,10 44,20 58,18 58,32 66,40 58,48 58,62 44,60 36,64 28,60 14,62 14,48 6,40 14,32 14,18 28,20" fill="#0D1B2A" stroke="#C9A84C" stroke-width="1"/>
      <text x="36" y="38" text-anchor="middle" fill="#C9A84C" font-size="10" font-family="Rajdhani,sans-serif" font-weight="700" letter-spacing="1">LSPD</text>
      <text x="36" y="50" text-anchor="middle" fill="#27AE60" font-size="6" font-family="Inter,sans-serif">IRP PAKISTAN</text>
    </svg>
    <div class="header-text">
      <h1>Infinity Role Play <span>Pakistan</span></h1>
      <p>Los Santos Police Department &nbsp;·&nbsp; Punjab Police Style</p>
    </div>
  </div>
</header>

<nav>
  <div class="nav-inner">
    <div class="nav-tab active" onclick="showPage('roster')">📋 Officer Roster</div>
    <div class="nav-tab" onclick="showPage('chain')">⛓ Chain of Command</div>
    <div class="nav-tab" onclick="showPage('admin')">🔐 Admin Management</div>
  </div>
</nav>

<main>
  <div class="page active" id="page-roster">
    <div id="statsBar" class="stats-bar"></div>
    <div class="section-head">
      <h2>Officer Roster</h2>
      <div class="section-line"></div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Badge No.</th>
            <th>Officer Name</th>
            <th>Rank</th>
            <th>Division</th>
            <th>Status</th>
            <th>Join Date</th>
            <th>Callsign</th>
            <th>Discord</th>
          </tr>
        </thead>
        <tbody id="rosterBody"></tbody>
      </table>
    </div>
  </div>

  <div class="page" id="page-chain">
    <div class="section-head">
      <h2>Chain of Command</h2>
      <div class="section-line"></div>
    </div>
    <div class="chain-grid" id="chainGrid"></div>
  </div>

  <div class="page" id="page-admin">
    <div class="admin-login-layout" id="adminAuthContainer">
      <div class="admin-login" id="adminLogin">
        <h2>🔐 Admin Access</h2>
        <p>Enter passphrase to unlock control metrics</p>
        <div class="form-group">
          <label>Passphrase</label>
          <input type="password" id="adminPassInput" placeholder="Enter security passphrase" onkeydown="if(event.key==='Enter')adminLogin()">
        </div>
        <div class="error-msg" id="loginError">Incorrect verification string. Access denied.</div>
        <br>
        <button class="btn btn-gold" style="width:100%" onclick="adminLogin()">Verify Identity</button>
      </div>

      <div class="admin-login" id="adminSignUp">
        <h2>📝 Re-register Passphrase</h2>
        <p>Change or claim master passkey over your active database</p>
        <div class="form-group">
          <label>New Passphrase</label>
          <input type="password" id="adminSignUpInput" placeholder="Create admin pass key">
        </div>
        <div class="error-msg" id="signUpError" style="color:var(--green-lt)"></div>
        <br>
        <button class="btn btn-outline" style="width:100%" onclick="adminRegister()">Overwrite Key</button>
      </div>
    </div>

    <div class="admin-panel" id="adminPanel">
      <div class="admin-toolbar">
        <div class="section-head" style="margin-bottom:0; flex:1">
          <h2>Manage Officers</h2>
          <div class="section-line"></div>
        </div>
        <div style="display:flex;gap:10px;align-items:center">
          <button class="btn btn-gold" onclick="openModal()">+ Add Officer</button>
          <button class="logout-btn" onclick="adminLogout()">Logout</button>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Badge</th>
              <th>Name</th>
              <th>Rank</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="adminBody"></tbody>
        </table>
      </div>
    </div>
  </div>
</main>

<div class="modal-overlay" id="modalOverlay">
  <div class="modal">
    <div class="modal-header">
      <h3 id="modalTitle">Add Officer</h3>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Badge Number</label>
        <input type="text" id="f_badge" placeholder="e.g. L-001">
      </div>
      <div class="form-group">
        <label>Callsign</label>
        <input type="text" id="f_callsign" placeholder="e.g. 1-ADAM-1">
      </div>
    </div>
    <div class="form-group">
      <label>Full Name</label>
      <input type="text" id="f_name" placeholder="Officer full name">
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Rank</label>
        <select id="f_rank">
          <option value="">Select rank...</option>
          <option>Inspector General of Police (IGP)</option>
          <option>Additional IGP (Addl. IGP)</option>
          <option>Deputy Inspector General (DIG)</option>
          <option>Senior Superintendent of Police (SSP)</option>
          <option>Superintendent of Police (SP)</option>
          <option>Deputy Superintendent of Police (DSP)</option>
          <option>Inspector (Inspr.)</option>
          <option>Sub-Inspector (SI)</option>
          <option>Assistant Sub-Inspector (ASI)</option>
          <option>Head Constable (HC)</option>
          <option>Constable</option>
        </select>
      </div>
      <div class="form-group">
        <label>Division</label>
        <select id="f_division">
          <option value="">Select division...</option>
          <option>Patrol</option>
          <option>Detective Bureau</option>
          <option>Traffic</option>
          <option>SWAT</option>
          <option>K9 Unit</option>
          <option>Internal Affairs</option>
          <option>Command</option>
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Status</label>
        <select id="f_status">
          <option>Active</option>
          <option>Inactive</option>
          <option>LOA</option>
          <option>Suspended</option>
          <option>Terminated</option>
        </select>
      </div>
      <div class="form-group">
        <label>Join Date</label>
        <input type="date" id="f_date">
      </div>
    </div>
    <div class="form-group">
      <label>Discord ID</label>
      <input type="text" id="f_discord" placeholder="e.g. username">
    </div>
    <div class="form-group">
      <label>Notes</label>
      <input type="text" id="f_notes" placeholder="Optional notes">
    </div>
    <div class="modal-actions">
      <button class="btn btn-outline" onclick="closeModal()">Cancel</button>
      <button class="btn btn-gold" onclick="saveOfficer()">Save Officer</button>
    </div>
  </div>
</div>

<footer><span>Infinity Role Play Pakistan</span> &nbsp;·&nbsp; LSPD Officer Management</footer>

<script>
// Mock cloud database simulation for frontend UI logic
let activeRosterData = [];
let masterPasskey = "lspd2024";

const RANKS = [
  { rank: "Inspector General of Police (IGP)",        abbr: "IGP",       note: "Supreme Commander — Overall Authority" },
  { rank: "Additional IGP (Addl. IGP)",               abbr: "Addl. IGP", note: "Deputy Supreme Command — Strategic Oversight" },
  { rank: "Deputy Inspector General (DIG)",           abbr: "DIG",       note: "Regional Command — Zone Operations" },
  { rank: "Senior Superintendent of Police (SSP)",    abbr: "SSP",       note: "District Head — Full District Command" },
  { rank: "Superintendent of Police (SP)",            abbr: "SP",        note: "Sub-Division Commander" },
  { rank: "Deputy Superintendent of Police (DSP)",    abbr: "DSP",       note: "Circle In-Charge — Field Supervisor" },
  { rank: "Inspector (Inspr.)",                       abbr: "INSPR",     note: "Station House Officer (SHO) — Station Commander" },
  { rank: "Sub-Inspector (SI)",                       abbr: "SI",        note: "Investigation & Patrol Lead" },
  { rank: "Assistant Sub-Inspector (ASI)",            abbr: "ASI",       note: "Senior Constable Supervisor" },
  { rank: "Head Constable (HC)",                      abbr: "HC",        note: "Senior Field Officer" },
  { rank: "Constable",                                abbr: "CONST.",    note: "Front-line Officer — Patrol & Duty" },
];

const SESSION_KEY = "irp_lspd_session";
let editingId = null;

function isLoggedIn() { return sessionStorage.getItem(SESSION_KEY) === "1"; }

function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  if(event) event.currentTarget.classList.add('active');
  if (name === 'roster') renderRoster();
  if (name === 'chain')  renderChain();
  if (name === 'admin')  renderAdmin();
}

function renderChain() {
  document.getElementById('chainGrid').innerHTML = RANKS.map((r, i) => `
    <div class="chain-row rank-${i}">
      <div class="chain-indent" style="width:${i * 18}px"></div>
      <div class="chain-card">
        <div class="chain-left">
          <span class="chain-num">${String(i+1).padStart(2,'0')}</span>
          <span class="chain-rank">${r.rank}</span>
          <span class="chain-abbr">${r.abbr}</span>
        </div>
        <span class="chain-note">${r.note}</span>
      </div>
    </div>
  `).join('');
}

function renderRoster() {
  const body = document.getElementById('rosterBody');
  const active = activeRosterData.filter(o => o.status === 'Active').length;
  const loa = activeRosterData.filter(o => o.status === 'LOA').length;
  const suspended = activeRosterData.filter(o => o.status === 'Suspended').length;

  document.getElementById('statsBar').innerHTML = `
    <div class="stat-card"><div class="stat-num">${activeRosterData.length}</div><div class="stat-label">Total Officers</div></div>
    <div class="stat-card"><div class="stat-num" style="color:#2ECC71">${active}</div><div class="stat-label">Active</div></div>
    <div class="stat-card"><div class="stat-num" style="color:#F1C40F">${loa}</div><div class="stat-label">On LOA</div></div>
    <div class="stat-card"><div class="stat-num" style="color:#E74C3C">${suspended}</div><div class="stat-label">Suspended</div></div>
  `;

  if(!activeRosterData.length) {
    body.innerHTML = `<tr><td colspan="9"><div class="empty-state"><p>No officers registered.</p></div></td></tr>`;
    return;
  }

  body.innerHTML = activeRosterData.map((o, i) => `
    <tr>
      <td>${i+1}</td>
      <td><span class="badge-no">${o.badge}</span></td>
      <td><span class="officer-name">${o.name}</span></td>
      <td>${o.rank}</td>
      <td>${o.division}</td>
      <td><span class="status-badge status-${o.status}">${o.status}</span></td>
      <td>${o.date}</td>
      <td><span class="callsign">${o.callsign}</span></td>
      <td>${o.discord}</td>
    </tr>
  `).join('');
}

function renderAdmin() {
  if (isLoggedIn()) {
    document.getElementById('adminAuthContainer').style.display = 'none';
    document.getElementById('adminPanel').classList.add('visible');
    renderAdminTable();
  } else {
    document.getElementById('adminAuthContainer').style.display = 'grid';
    document.getElementById('adminPanel').classList.remove('visible');
  }
}

function renderAdminTable() {
  const body = document.getElementById('adminBody');
  body.innerHTML = activeRosterData.map(o => `
    <tr>
      <td><span class="badge-no">${o.badge}</span></td>
      <td><span class="officer-name">${o.name}</span></td>
      <td>${o.rank}</td>
      <td><span class="status-badge status-${o.status}">${o.status}</span></td>
      <td>
        <button class="btn btn-edit" onclick="openModal(${o.id})">Edit</button>
        <button class="btn btn-danger" onclick="deleteOfficer(${o.id})">Delete</button>
      </td>
    </tr>
  `).join('');
}

function adminLogin() {
  const val = document.getElementById('adminPassInput').value;
  const err = document.getElementById('loginError');
  if (val === masterPasskey) {
    sessionStorage.setItem(SESSION_KEY, '1');
    err.style.display = 'none';
    renderAdmin();
  } else {
    err.style.display = 'block';
  }
}

function adminRegister() {
  const val = document.getElementById('adminSignUpInput').value.trim();
  const out = document.getElementById('signUpError');
  if(!val) return;
  masterPasskey = val;
  out.textContent = "Passphrase configuration key modified successfully!";
  out.style.display = 'block';
  document.getElementById('adminSignUpInput').value = '';
}

function adminLogout() {
  sessionStorage.removeItem(SESSION_KEY);
  renderAdmin();
}

function openModal(id = null) {
  editingId = id;
  const overlay = document.getElementById('modalOverlay');
  if (id) {
    const o = activeRosterData.find(x => x.id == id);
    if(o) {
      document.getElementById('f_badge').value = o.badge;
      document.getElementById('f_name').value = o.name;
      document.getElementById('f_rank').value = o.rank;
      document.getElementById('f_division').value = o.division;
      document.getElementById('f_status').value = o.status;
      document.getElementById('f_date').value = o.date;
      document.getElementById('f_callsign').value = o.callsign;
      document.getElementById('f_discord').value = o.discord;
      document.getElementById('f_notes').value = o.notes;
    }
  } else {
    ['f_badge','f_name','f_rank','f_division','f_date','f_callsign','f_discord','f_notes'].forEach(k => document.getElementById(k).value = '');
  }
  overlay.classList.add('open');
}

function closeModal() { document.getElementById('modalOverlay').classList.remove('open'); }

function saveOfficer() {
  const packet = {
    id: editingId || Date.now(),
    badge: document.getElementById('f_badge').value,
    name: document.getElementById('f_name').value,
    rank: document.getElementById('f_rank').value,
    division: document.getElementById('f_division').value,
    status: document.getElementById('f_status').value,
    date: document.getElementById('f_date').value,
    callsign: document.getElementById('f_callsign').value,
    discord: document.getElementById('f_discord').value,
    notes: document.getElementById('f_notes').value
  };

  if(editingId) {
    const idx = activeRosterData.findIndex(x => x.id == editingId);
    if(idx !== -1) activeRosterData[idx] = packet;
  } else {
    activeRosterData.push(packet);
  }
  closeModal();
  renderRoster();
  renderAdminTable();
}

function deleteOfficer(id) {
  if(!confirm('Delete officer entirely from database?')) return;
  activeRosterData = activeRosterData.filter(x => x.id != id);
  renderRoster();
  renderAdminTable();
}

renderRoster();
renderChain();
</script>
</body>
</html>
"""

# Render the application completely embedded inside Streamlit viewport
components.html(html_code, height=950, scrolling=True)
