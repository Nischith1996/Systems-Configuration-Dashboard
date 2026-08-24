import os
import re
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & MODERN SAAS CSS
# ==========================================
st.set_page_config(
    page_title="Systems Configuration Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inline SVG Logo Component (Scaled to match workforcejunction.com proportions)
SVG_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 60" width="100%" height="auto">
<path d="M 18 8 L 34 8 L 34 32 C 34 40 41 46 50 46 C 59 46 66 40 66 32 L 66 8 L 82 8 L 82 32 C 82 48 68 58 50 58 C 32 58 18 48 18 32 Z" fill="#0b3866"/>
<path d="M 56 8 L 72 8 L 72 32 C 72 40 79 46 88 46 C 97 46 104 40 104 32 L 104 8 L 120 8 L 120 32 C 120 48 106 58 88 58 C 70 58 56 48 56 32 Z" fill="#71757a"/>
<line x1="134" y1="6" x2="134" y2="54" stroke="#b0b5bc" stroke-width="2.2" stroke-linecap="round"/>
<text x="146" y="27" font-family="'Plus Jakarta Sans', Arial, sans-serif" font-size="18" font-weight="800" fill="#0b3866" letter-spacing="1.2">WORKFORCE</text>
<text x="146" y="47" font-family="'Plus Jakarta Sans', Arial, sans-serif" font-size="17" font-weight="700" fill="#71757a" letter-spacing="3.2">JUNCTION</text>
</svg>"""

# Initialize navigation session state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Overview"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background-color: #0b0f19;
    color: #f1f5f9;
}

.dashboard-header {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 22px 26px;
    margin-bottom: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.dashboard-title {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.dashboard-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-top: 6px;
}

.sidebar-logo-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
}

.kpi-card {
    background: linear-gradient(145deg, #131b2e, #0f172a);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
}

.kpi-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.kpi-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94a3b8;
}

.kpi-icon-badge {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}

.kpi-pill {
    display: inline-flex;
    align-items: center;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
}

.pill-green {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.25);
}

.pill-red {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

.pill-blue {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.25);
}

.pill-yellow {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.25);
}

.pill-purple {
    background: rgba(168, 85, 247, 0.15);
    color: #c084fc;
    border: 1px solid rgba(168, 85, 247, 0.25);
}

.chart-container {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
}

.chart-header {
    font-size: 16px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

div.stButton > button {
    width: 100%;
    background: rgba(99, 102, 241, 0.15);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    padding: 6px 12px;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: rgba(99, 102, 241, 0.3);
    color: #ffffff;
    border-color: #818cf8;
}
</style>
""", unsafe_allow_html=True)


# Helper function to convert raw column names into Title Case
def format_col_header(col_name: str) -> str:
    custom_names = {
        "sno": "S.No",
        "sl_no": "S.No",
        "crm": "CRM Lead",
        "oe_type": "OE Type",
        "oe_effective": "OE Effective Date",
        "oe_setup_status": "Setup Status",
        "oe_closure": "OE Closure",
        "oe_finalization_date": "OE Finalization Date",
        "reviewtesting_status": "Review & Testing Status",
        "finalization_rules_status": "Finalization Rules Status",
        "config_analyst": "Config Analyst",
        "configuration_analyst": "Configuration Analyst",
    }
    col_str = str(col_name).strip()
    if col_str.lower() in custom_names:
        return custom_names[col_str.lower()]
    return re.sub(r'[\s_]+', ' ', col_str).title().replace("Oe ", "OE ").replace("Crm", "CRM").replace("Edi", "EDI")


# ==========================================
# 2. ETL HELPERS: PARSE MULTI-YEAR SHEETS
# ==========================================
def clean_col_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all", axis=1).dropna(how="all", axis=0).copy()
    cleaned = []
    seen = {}
    for i, col in enumerate(df.columns):
        c_str = str(col).strip()
        if not c_str or c_str.lower().startswith("unnamed"):
            c_str = f"extra_col_{i}"
        else:
            c_str = re.sub(r'[\r\n]+', ' ', c_str)
            c_str = re.sub(r'[^\w\s]', '', c_str)
            c_str = re.sub(r'\s+', '_', c_str).strip().lower()
            if not c_str:
                c_str = f"col_{i}"
        if c_str in seen:
            seen[c_str] += 1
            c_str = f"{c_str}_{seen[c_str]}"
        else:
            seen[c_str] = 0
        cleaned.append(c_str)
    df.columns = cleaned
    drop_cols = [c for c in df.columns if c.startswith("extra_col")]
    if drop_cols:
        df = df.drop(columns=drop_cols)
    return df


def parse_yearly_implemented_terminated(df_raw: pd.DataFrame, year: int):
    df_raw = df_raw.dropna(how="all").copy()
    df_left = df_raw.iloc[2:, 0:7].copy()
    df_left.columns = [
        "sl_no", "client_name", "broker", "design_guide_received_date",
        "implementation_completion_date", "client_go_live_date", "headcount"
    ]
    yet_to_live_idx = None
    for idx, val in df_left["client_name"].items():
        if isinstance(val, str) and "yet to live" in val.lower():
            yet_to_live_idx = idx
            break
            
    if yet_to_live_idx is not None:
        df_live = df_left.loc[:yet_to_live_idx - 1].copy()
        df_yet = df_left.loc[yet_to_live_idx + 1:].copy()
    else:
        df_live = df_left.copy()
        df_yet = pd.DataFrame(columns=df_left.columns)
        
    def clean_client_data(df_subset, status_label):
        df_subset = df_subset.dropna(subset=["client_name"]).copy()
        df_subset = df_subset[~df_subset["client_name"].astype(str).str.lower().str.contains("total|client name|clients|all clients", na=False)]
        df_subset["client_name"] = df_subset["client_name"].astype(str).str.strip()
        df_subset = df_subset[df_subset["client_name"] != ""]
        df_subset["status"] = status_label
        df_subset["year"] = int(year)
        df_subset["headcount"] = pd.to_numeric(df_subset["headcount"], errors="coerce").fillna(0).astype(int)
        for date_col in ["design_guide_received_date", "implementation_completion_date", "client_go_live_date"]:
            if date_col in df_subset.columns:
                df_subset[date_col] = df_subset[date_col].astype(str).replace("nan", "")
        return df_subset

    df_impl = pd.concat([clean_client_data(df_live, "Implemented"), clean_client_data(df_yet, "Yet to Live")], ignore_index=True)
    df_right = df_raw.iloc[2:, 8:14].copy()
    df_right.columns = ["sl_no", "client_name", "broker", "termination_effective_date", "headcount", "reason"]
    df_term = clean_client_data(df_right, "Terminated")
    return df_impl, df_term


# ==========================================
# 3. DATABASE INITIALIZATION & SHAREPOINT LOADER
# ==========================================
@st.cache_data(ttl=300) # Caches data for 5 minutes, allowing auto-refresh from SharePoint
def load_and_sync_db():
    conn = sqlite3.connect("operations_analytics.db")

    # You can substitute these local file strings with direct SharePoint file URLs if hosted publicly/shared via OneDrive link
    crf_excel_files = [f for f in os.listdir(".") if f.endswith((".xlsx", ".xls")) and "CRF" in f]
    all_crf_dfs = []

    if crf_excel_files:
        xls_crf = pd.ExcelFile(crf_excel_files[0])
        crf_sheets = [s for s in xls_crf.sheet_names if "CRF Source Data" in s or any(y in s for y in ["2024", "2025", "2026"])]
        for sheet in crf_sheets:
            year_match = re.search(r'(20\d\d)', sheet)
            sheet_year = int(year_match.group(1)) if year_match else 2026
            df_crf_sheet = pd.read_excel(xls_crf, sheet_name=sheet, header=1)
            df_crf_sheet = clean_col_names(df_crf_sheet)
            df_crf_sheet["year"] = sheet_year
            all_crf_dfs.append(df_crf_sheet)
    elif os.path.exists("CRF Config Master Tracker (Pivots and Charts).csv"):
        df_crf_csv = pd.read_csv("CRF Config Master Tracker (Pivots and Charts).csv", encoding="latin1", header=1)
        df_crf_csv = clean_col_names(df_crf_csv)
        df_crf_csv["year"] = 2026
        all_crf_dfs.append(df_crf_csv)

    if all_crf_dfs:
        combined_crf = pd.concat(all_crf_dfs, ignore_index=True)
        for col in combined_crf.columns:
            if combined_crf[col].dtype == "object":
                combined_crf[col] = combined_crf[col].astype(str).replace("nan", "")
        combined_crf.to_sql("crf_master_tracker_multiyear", conn, if_exists="replace", index=False)

    # B. Implemented & Terminated Multi-Year Sheets (2024, 2025, 2026)
    client_excel_files = [f for f in os.listdir(".") if f.endswith((".xlsx", ".xls")) and "Implemented and Terminated" in f]
    all_impl, all_term = [], []

    if client_excel_files:
        xls_clients = pd.ExcelFile(client_excel_files[0])
        target_sheets = [s for s in xls_clients.sheet_names if str(s).strip() in ["2026", "2025", "2024"]]
        for sheet in target_sheets:
            df_raw = pd.read_excel(xls_clients, sheet_name=sheet, header=None)
            impl, term = parse_yearly_implemented_terminated(df_raw, year=int(sheet))
            all_impl.append(impl)
            all_term.append(term)
    elif os.path.exists("2026_Client Implemented and Terminated.csv"):
        df_raw = pd.read_csv("2026_Client Implemented and Terminated.csv", encoding="latin1", header=None)
        impl, term = parse_yearly_implemented_terminated(df_raw, year=2026)
        all_impl.append(impl)
        all_term.append(term)

    if all_impl:
        final_impl = pd.concat(all_impl, ignore_index=True)
        final_term = pd.concat(all_term, ignore_index=True)
        final_impl.to_sql("clients_implemented_multiyear", conn, if_exists="replace", index=False)
        final_term.to_sql("clients_terminated_multiyear", conn, if_exists="replace", index=False)

    # C. Open Enrollment Tabs (2024, 2025, 2026)
    oe_excel_files = [f for f in os.listdir(".") if f.endswith((".xlsx", ".xls")) and "Open Enrollment" in f]
    all_oe_dfs = []

    if oe_excel_files:
        xls_oe = pd.ExcelFile(oe_excel_files[0])
        oe_sheets = [s for s in xls_oe.sheet_names if "OE Tracker" in s or any(y in s for y in ["2024", "2025", "2026"])]
        for sheet in oe_sheets:
            year_match = re.search(r'(20\d\d)', sheet)
            sheet_year = int(year_match.group(1)) if year_match else 2026
            df_oe_sheet = pd.read_excel(xls_oe, sheet_name=sheet)
            df_oe_sheet = clean_col_names(df_oe_sheet)
            df_oe_sheet["year"] = sheet_year
            all_oe_dfs.append(df_oe_sheet)
    elif os.path.exists("Open Enrollment Tracker.csv"):
        oe_raw = pd.read_csv("Open Enrollment Tracker.csv", encoding="latin1")
        oe_clean = clean_col_names(oe_raw)
        oe_clean["year"] = 2026
        all_oe_dfs.append(oe_clean)

    if all_oe_dfs:
        combined_oe = pd.concat(all_oe_dfs, ignore_index=True)
        for col in combined_oe.columns:
            if combined_oe[col].dtype == "object":
                combined_oe[col] = combined_oe[col].astype(str).replace("nan", "")
        combined_oe.to_sql("open_enrollment_tracker_multiyear", conn, if_exists="replace", index=False)

    # D. Lumber Benefits Tracker
    if os.path.exists("Lumber Benefits Tracker.csv"):
        lumber_raw = pd.read_csv("Lumber Benefits Tracker.csv")
        lumber_clean = clean_col_names(lumber_raw)
        if "client" in lumber_clean.columns:
            lumber_clean = lumber_clean.dropna(subset=["client"]).copy()
        for col in lumber_clean.columns:
            if lumber_clean[col].dtype == "object":
                lumber_clean[col] = lumber_clean[col].astype(str).replace("nan", "")
        lumber_clean.to_sql("lumber_benefits_tracker", conn, if_exists="replace", index=False)

    crf_df = pd.read_sql("SELECT * FROM crf_master_tracker_multiyear", conn)
    oe_df = pd.read_sql("SELECT * FROM open_enrollment_tracker_multiyear", conn)
    impl_df = pd.read_sql("SELECT * FROM clients_implemented_multiyear", conn)
    term_df = pd.read_sql("SELECT * FROM clients_terminated_multiyear", conn)
    lumber_df = pd.read_sql("SELECT * FROM lumber_benefits_tracker", conn) if "lumber_benefits_tracker" in [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")] else pd.DataFrame()

    conn.close()
    return crf_df, oe_df, impl_df, term_df, lumber_df

crf_raw, oe_raw, impl_raw, term_raw, lumber_raw = load_and_sync_db()


# ==========================================
# 4. SIDEBAR LOGO & FILTERS
# ==========================================
st.sidebar.markdown(f'<div class="sidebar-logo-card">{SVG_LOGO}</div>', unsafe_allow_html=True)
st.sidebar.markdown("### 🎛️ Navigation & Filters")

if st.sidebar.button("🔄 Refresh Data from Source"):
    st.cache_data.clear()
    st.rerun()

all_years = sorted(
    list(
        set(crf_raw["year"].dropna().unique())
        .union(set(impl_raw["year"].dropna().unique()))
        .union(set(oe_raw["year"].dropna().unique()))
        .union(set(term_raw["year"].dropna().unique()))
    ),
    reverse=True
)
selected_year = st.sidebar.selectbox("📅 Reporting Year Tab", options=all_years, index=0)

crf_year_scoped = crf_raw[crf_raw["year"] == selected_year].copy()
oe_curr = oe_raw[oe_raw["year"] == selected_year].copy()
impl_curr = impl_raw[impl_raw["year"] == selected_year].copy()
term_curr = term_raw[term_raw["year"] == selected_year].copy()
lumber_curr = lumber_raw.copy()

INVALID_NAME_PATTERNS = {
    'all clients', 'clients', 'client name', 'total', 'grand total',
    'nan', 'none', 'null', 'n/a', 'select all', 'unknown', ''
}

def build_canonical_map(values_list):
    name_map = {}
    for item in values_list:
        s = str(item).strip()
        if not s:
            continue
        s_norm = ' '.join(s.split())
        key = s_norm.lower()
        if key in INVALID_NAME_PATTERNS or key.startswith("unnamed"):
            continue
        if key not in name_map:
            name_map[key] = s_norm.title() if s_norm.islower() else s_norm
        else:
            if any(c.isupper() for c in s_norm[1:]):
                name_map[key] = s_norm
    return name_map

# 1. Partner Filter (Deduplicated)
partner_col = "partner_name" if "partner_name" in crf_year_scoped.columns else "partner"
partner_map = {}
all_partners = []

if partner_col in crf_year_scoped.columns:
    partner_map = build_canonical_map(crf_year_scoped[partner_col].dropna().unique())
    crf_year_scoped[partner_col] = crf_year_scoped[partner_col].astype(str).str.strip().str.lower().map(partner_map).fillna(crf_year_scoped[partner_col])
    all_partners = sorted(list(set(partner_map.values())))

selected_partners = st.sidebar.multiselect(
    "Partner Name",
    options=all_partners,
    placeholder="Showing All Partners..."
)

# 2. Cascading Clients Filter (Deduplicated)
client_col = "client_name" if "client_name" in crf_year_scoped.columns else "client"

if selected_partners and partner_col in crf_year_scoped.columns:
    partner_scoped_df = crf_year_scoped[crf_year_scoped[partner_col].isin(selected_partners)]
    raw_clients = partner_scoped_df[client_col].dropna().unique() if client_col in partner_scoped_df.columns else []
else:
    raw_clients = crf_year_scoped[client_col].dropna().unique() if client_col in crf_year_scoped.columns else []

client_map = build_canonical_map(raw_clients)
if client_col in crf_year_scoped.columns:
    crf_year_scoped[client_col] = crf_year_scoped[client_col].astype(str).str.strip().str.lower().map(client_map).fillna(crf_year_scoped[client_col])

available_clients = sorted(list(set(client_map.values())))

selected_clients = st.sidebar.multiselect(
    "Clients",
    options=available_clients,
    placeholder="Showing All Clients..."
)

# 3. Apply Filter across all tables safely
filtered_crf = crf_year_scoped.copy()
filtered_oe = oe_curr.copy()
filtered_impl = impl_curr.copy()
filtered_term = term_curr.copy()
filtered_lumber = lumber_curr.copy()

if selected_partners and partner_col in filtered_crf.columns:
    filtered_crf = filtered_crf[filtered_crf[partner_col].isin(selected_partners)]

if selected_clients:
    selected_clients_lower = [c.lower() for c in selected_clients]
    if client_col in filtered_crf.columns:
        filtered_crf = filtered_crf[filtered_crf[client_col].astype(str).str.strip().str.lower().isin(selected_clients_lower)]
    if "client" in filtered_oe.columns:
        filtered_oe = filtered_oe[filtered_oe["client"].astype(str).str.strip().str.lower().isin(selected_clients_lower)]
    if "client_name" in filtered_impl.columns:
        filtered_impl = filtered_impl[filtered_impl["client_name"].astype(str).str.strip().str.lower().isin(selected_clients_lower)]
    if "client_name" in filtered_term.columns:
        filtered_term = filtered_term[filtered_term["client_name"].astype(str).str.strip().str.lower().isin(selected_clients_lower)]
    if "client" in filtered_lumber.columns:
        filtered_lumber = filtered_lumber[filtered_lumber["client"].astype(str).str.strip().str.lower().isin(selected_clients_lower)]


# ==========================================
# 5. SCREEN 1: OVERVIEW DASHBOARD
# ==========================================
month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

if st.session_state["current_page"] == "Overview":
    st.markdown(f'<div class="dashboard-header"><h1 class="dashboard-title">⚡ Systems Configuration</h1><div class="dashboard-subtitle">Real-time Open Enrollment tracking, Change Request resolution velocity, Lumber Benefits, and Client Retention Analytics for <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    total_crf_tickets = len(filtered_crf)
    implemented_live = len(filtered_impl[filtered_impl["status"] == "Implemented"])
    yet_to_live_count = len(filtered_impl[filtered_impl["status"] == "Yet to Live"])
    terminated_count = len(filtered_term)

    total_oe = len(filtered_oe[filtered_oe["client"].notna() & (filtered_oe["client"] != "")])
    completed_oe = len(filtered_oe[filtered_oe["oe_setup_status"].astype(str).str.lower() == "completed"])
    oe_rate = (completed_oe / total_oe * 100) if total_oe > 0 else 0
    total_lumber = len(filtered_lumber)

    # Row 1: KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(99, 102, 241, 0.4);"><div class="kpi-top-row"><span class="kpi-label">Change Request Form</span><div class="kpi-icon-badge" style="background: rgba(99, 102, 241, 0.15); color: #818cf8;">📑</div></div><div class="kpi-value">{total_crf_tickets:,}</div><div class="kpi-pill pill-blue">Active Scope</div></div>', unsafe_allow_html=True)
        if st.button("🔍 View Change Requests →", key="btn_goto_crf"):
            st.session_state["current_page"] = "CRF_Tickets"
            st.rerun()

    with k2:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(168, 85, 247, 0.4);"><div class="kpi-top-row"><span class="kpi-label">Open Enrollment</span><div class="kpi-icon-badge" style="background: rgba(168, 85, 247, 0.15); color: #34d399;">🎯</div></div><div class="kpi-value">{oe_rate:.1f}%</div><div class="kpi-pill pill-green">↑ {completed_oe}/{total_oe} Clients</div></div>', unsafe_allow_html=True)
        if st.button("🎯 View OE Details →", key="btn_goto_oe"):
            st.session_state["current_page"] = "OE_Setup"
            st.rerun()

    with k3:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(56, 189, 248, 0.4);"><div class="kpi-top-row"><span class="kpi-label">Live Clients</span><div class="kpi-icon-badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8;">🚀</div></div><div class="kpi-value">{implemented_live:,}</div><div class="kpi-pill pill-green">{yet_to_live_count} Pipeline</div></div>', unsafe_allow_html=True)
        if st.button("🚀 View Live Clients →", key="btn_goto_live"):
            st.session_state["current_page"] = "Live_Clients"
            st.rerun()

    with k4:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(244, 63, 94, 0.4);"><div class="kpi-label">Terminations</div><div class="kpi-icon-badge" style="background: rgba(244, 63, 94, 0.15); color: #fb7185;">⚠️</div></div><div class="kpi-value">{terminated_count:,}</div><div class="kpi-pill pill-red">↓ {filtered_term["headcount"].sum():,} Headcount</div></div>', unsafe_allow_html=True)
        if st.button("⚠️ View Terminations →", key="btn_goto_term"):
            st.session_state["current_page"] = "Terminations"
            st.rerun()

    with k5:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(168, 85, 247, 0.4);"><div class="kpi-label">Lumber Benefits</div><div class="kpi-icon-badge" style="background: rgba(168, 85, 247, 0.15); color: #c084fc;">🌲</div></div><div class="kpi-value">{total_lumber:,}</div><div class="kpi-pill pill-purple">Flores Services</div></div>', unsafe_allow_html=True)
        if st.button("🌲 View Benefits →", key="btn_goto_lumber"):
            st.session_state["current_page"] = "Lumber_Benefits"
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Row 2: Charts
    c1, c2 = st.columns([6, 4])

    with c1:
        st.markdown('<div class="chart-container"><div class="chart-header">📈 Monthly Change Request Ticket Velocity</div>', unsafe_allow_html=True)
        if not filtered_crf.empty:
            trend_df = (
                filtered_crf.groupby("month", as_index=False)
                .agg(ticket_count=("client_name", "count"))
            )
            trend_df["month"] = pd.Categorical(trend_df["month"], categories=month_order, ordered=True)
            trend_df = trend_df.sort_values("month")

            fig_trend = px.area(trend_df, x="month", y="ticket_count", markers=True, labels={"month": "", "ticket_count": "Tickets"})
            fig_trend.update_traces(
                line=dict(color="#6366f1", width=3.5),
                marker=dict(size=8, color="#a855f7", line=dict(color="#ffffff", width=1.5)),
                fillcolor="rgba(99, 102, 241, 0.2)"
            )
            fig_trend.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=320,
                hovermode="x unified",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No Change Request data found for the active filter selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-container"><div class="chart-header">🎯 OE Setup Target Health</div>', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=oe_rate,
            number={"suffix": "%", "font": {"size": 42, "color": "#f8fafc", "family": "Plus Jakarta Sans"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748b", "tickwidth": 1},
                "bar": {"color": "#10b981", "thickness": 0.28},
                "bgcolor": "rgba(255, 255, 255, 0.03)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [50, 80], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [80, 100], "color": "rgba(16, 185, 129, 0.15)"}
                ],
                "threshold": {"line": {"color": "#f43f5e", "width": 4}, "thickness": 0.75, "value": 80}
            }
        ))
        fig_gauge.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 6. SCREEN 2: DEDICATED CHANGE REQUEST FORM SCREEN
# ==========================================
elif st.session_state["current_page"] == "CRF_Tickets":
    top_col1, top_col2 = st.columns([2, 8])
    with top_col1:
        if st.button("← Back to Overview"):
            st.session_state["current_page"] = "Overview"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">📑 Change Request Forms (CRF) - Detailed Screen</h1><div class="dashboard-subtitle">Complete ticket logs, category distributions, and resolution records for <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(99, 102, 241, 0.4);"><div class="kpi-label">Total Filtered Tickets</div><div class="kpi-value">{len(filtered_crf):,}</div><div class="kpi-pill pill-blue">{selected_year} Data</div></div>', unsafe_allow_html=True)
        if st.button("📑 All Tickets Log →", key="btn_crf_all_tickets"):
            st.session_state["current_page"] = "CRF_All_Tickets"
            st.rerun()

    with m2:
        top_cat = filtered_crf["category"].value_counts().index[0] if not filtered_crf.empty and "category" in filtered_crf.columns else "N/A"
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(168, 85, 247, 0.4);"><div class="kpi-label">Top Request Category</div><div class="kpi-value" style="font-size: 20px;">{top_cat}</div><div class="kpi-pill pill-green">High Volume</div></div>', unsafe_allow_html=True)
        if st.button("🏷️ Category Drilldown →", key="btn_crf_category"):
            st.session_state["current_page"] = "CRF_Category_Detail"
            st.rerun()

    with m3:
        unique_clients = filtered_crf["client_name"].nunique() if "client_name" in filtered_crf.columns else 0
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(56, 189, 248, 0.4);"><div class="kpi-label">Clients Requesting Changes</div><div class="kpi-value">{unique_clients}</div><div class="kpi-pill pill-blue">Active Accounts</div></div>', unsafe_allow_html=True)
        if st.button("👥 Client Requests →", key="btn_crf_clients"):
            st.session_state["current_page"] = "CRF_Client_Detail"
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    crf_c1, crf_c2 = st.columns([5, 5])
    with crf_c1:
        st.markdown('<div class="chart-container"><div class="chart-header">📊 All Categories Distribution</div>', unsafe_allow_html=True)
        if not filtered_crf.empty and "category" in filtered_crf.columns:
            cat_full_df = filtered_crf["category"].value_counts().reset_index()
            cat_full_df.columns = ["category", "count"]
            fig_full_cat = px.pie(cat_full_df, names="category", values="count", hole=0.45, color_discrete_sequence=px.colors.sequential.Purples_r)
            fig_full_cat.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(t=10, b=10))
            st.plotly_chart(fig_full_cat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with crf_c2:
        st.markdown('<div class="chart-container"><div class="chart-header">👥 Change Request Form worked by Configuration Analyst</div>', unsafe_allow_html=True)
        if not filtered_crf.empty and "configuration_analyst" in filtered_crf.columns:
            analyst_df = filtered_crf["configuration_analyst"].value_counts().reset_index()
            analyst_df.columns = ["analyst", "count"]
            fig_analyst = px.bar(analyst_df, x="analyst", y="count", color="count", color_continuous_scale="Blues", labels={"analyst": "Analyst", "count": "Tickets"})
            fig_analyst.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(t=10, b=10))
            st.plotly_chart(fig_analyst, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="chart-container"><div class="chart-header">📋 Complete {selected_year} Change Request Audit Log</div>', unsafe_allow_html=True)
    detail_cols = ["month", "client_name", "partner_name", "category"]
    available_detail_cols = [c for c in detail_cols if c in filtered_crf.columns]
    
    sorted_crf_df = filtered_crf.copy()
    if "month" in sorted_crf_df.columns:
        sorted_crf_df["_month_order"] = pd.Categorical(sorted_crf_df["month"], categories=month_order, ordered=True)
        sorted_crf_df = sorted_crf_df.sort_values("_month_order")
        sorted_crf_df["month"] = sorted_crf_df["month"].astype(str) + f" {selected_year}"
    
    table_display_df = sorted_crf_df[available_detail_cols].rename(columns={
        "month": "Month",
        "client_name": "Client Name",
        "partner_name": "Partner Name",
        "category": "Category"
    })
    st.dataframe(table_display_df, use_container_width=True, hide_index=True, height=380)
    
    csv_data = table_display_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download Filtered Change Request Records (CSV)", data=csv_data, file_name=f"CRF_Audit_Log_{selected_year}.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 6A. SUB-SCREEN: TOTAL FILTERED TICKETS DEEP-DIVE
# =========================================================
elif st.session_state["current_page"] == "CRF_All_Tickets":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Change Requests"):
            st.session_state["current_page"] = "CRF_Tickets"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">📑 All Change Request Forms - Detailed Audit Log</h1><div class="dashboard-subtitle">Granular view of all {len(filtered_crf)} change requests raised in <b>{selected_year}</b>. <i>Click on any bar to see Client Name, Partner Name, and Category details for that month.</i></div></div>', unsafe_allow_html=True)

    selected_month = None

    if not filtered_crf.empty:
        trend_m = (
            filtered_crf.groupby("month", as_index=False)
            .agg(tickets=("client_name", "count"))
        )
        trend_m["month"] = pd.Categorical(trend_m["month"], categories=month_order, ordered=True)
        trend_m = trend_m.sort_values("month").dropna(subset=["month"])

        fig_tm = px.bar(
            trend_m,
            x="month",
            y="tickets",
            text="tickets",
            color="tickets",
            color_continuous_scale="Blues",
            labels={"month": "Month", "tickets": "Total Tickets"}
        )
        fig_tm.update_traces(
            textposition="outside",
            textfont=dict(size=13, color="#ffffff", family="Plus Jakarta Sans"),
            hovertemplate="<b>%{x}</b><br>Tickets Worked: <b>%{y}</b><extra></extra>"
        )
        fig_tm.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320,
            clickmode="event+select",
            margin=dict(t=30, b=10, l=10, r=10),
            yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
        )

        chart_selection = st.plotly_chart(
            fig_tm,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="crf_monthly_chart"
        )

        if chart_selection and "selection" in chart_selection and chart_selection["selection"]["points"]:
            selected_point = chart_selection["selection"]["points"][0]
            selected_month = selected_point.get("x")

    if selected_month:
        display_crf = filtered_crf[filtered_crf["month"].astype(str).str.lower() == str(selected_month).lower()].copy()
        if "month" in display_crf.columns:
            display_crf["month"] = display_crf["month"].astype(str) + f" {selected_year}"
        target_cols = ["client_name", "partner_name", "category"]
        available_target_cols = [c for c in target_cols if c in display_crf.columns]
        
        st.markdown(f'<div class="kpi-card" style="margin-top: 10px; border-color: rgba(99, 102, 241, 0.6); display: flex; justify-content: space-between; align-items: center; padding: 16px 24px;"><div><span class="kpi-label">Selected Month</span><div style="font-size: 24px; font-weight: 800; color: #60a5fa;">{selected_month} {selected_year}</div></div><div style="text-align: right;"><span class="kpi-label">CRFs Worked</span><div style="font-size: 28px; font-weight: 800; color: #ffffff;">{len(display_crf):,} <span style="font-size: 15px; font-weight: 500; color: #94a3b8;">tickets</span></div></div></div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="chart-container"><div class="chart-header">📋 {selected_month} {selected_year} CRF Breakdown (Client Name, Partner Name, Category)</div>', unsafe_allow_html=True)
        st.dataframe(
            display_crf[available_target_cols].rename(columns={
                "client_name": "Client Name",
                "partner_name": "Partner Name",
                "category": "Category"
            }),
            use_container_width=True,
            hide_index=True,
            height=320
        )
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 6B. SUB-SCREEN: CATEGORY BREAKDOWN DEEP-DIVE
# =========================================================
elif st.session_state["current_page"] == "CRF_Category_Detail":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Change Requests"):
            st.session_state["current_page"] = "CRF_Tickets"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">🏷️ Change Request Categories - Deep Dive</h1><div class="dashboard-subtitle">Volume analysis and category distribution for <b>{selected_year}</b>. <i>Click on any bar or pie slice to see Client Name, Partner Name, and Category details.</i></div></div>', unsafe_allow_html=True)

    selected_category = None

    if not filtered_crf.empty and "category" in filtered_crf.columns:
        cat_stats = filtered_crf.groupby("category").agg(
            total_tickets=("client_name", "count"),
            unique_clients=("client_name", "nunique")
        ).reset_index().sort_values(by="total_tickets", ascending=False)

        col_c1, col_c2 = st.columns([6, 4])
        with col_c1:
            fig_cat_bar = px.bar(
                cat_stats,
                x="total_tickets",
                y="category",
                orientation="h",
                text="total_tickets",
                color="total_tickets",
                color_continuous_scale="Purples",
                labels={"total_tickets": "Tickets", "category": "Category"}
            )
            fig_cat_bar.update_traces(
                textposition="outside",
                textfont=dict(size=12, color="#ffffff", family="Plus Jakarta Sans"),
                hovertemplate="<b>%{y}</b><br>Tickets: <b>%{x}</b><extra></extra>"
            )
            fig_cat_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed"),
                height=350,
                clickmode="event+select",
                margin=dict(t=20, b=10, l=10, r=20)
            )
            bar_selection = st.plotly_chart(
                fig_cat_bar,
                use_container_width=True,
                on_select="rerun",
                selection_mode="points",
                key="crf_cat_bar_chart"
            )

        with col_c2:
            fig_cat_pie = px.pie(
                cat_stats,
                names="category",
                values="total_tickets",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_cat_pie.update_traces(
                hovertemplate="<b>%{label}</b><br>Tickets: <b>%{value}</b> (%{percent})<extra></extra>"
            )
            fig_cat_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=350,
                clickmode="event+select",
                margin=dict(t=20, b=10, l=10, r=10)
            )
            pie_selection = st.plotly_chart(
                fig_cat_pie,
                use_container_width=True,
                on_select="rerun",
                selection_mode="points",
                key="crf_cat_pie_chart"
            )

        if bar_selection and "selection" in bar_selection and bar_selection["selection"]["points"]:
            selected_category = bar_selection["selection"]["points"][0].get("y")
        elif pie_selection and "selection" in pie_selection and pie_selection["selection"]["points"]:
            selected_category = pie_selection["selection"]["points"][0].get("label")

        if selected_category:
            display_cat_df = filtered_crf[filtered_crf["category"].astype(str).str.lower() == str(selected_category).lower()].copy()
            target_cols = ["client_name", "partner_name", "category"]
            available_target_cols = [c for c in target_cols if c in display_cat_df.columns]

            st.markdown(f'<div class="kpi-card" style="margin-top: 10px; border-color: rgba(168, 85, 247, 0.6); display: flex; justify-content: space-between; align-items: center; padding: 16px 24px;"><div><span class="kpi-label">Selected Category</span><div style="font-size: 22px; font-weight: 800; color: #c084fc;">{selected_category}</div></div><div style="text-align: right;"><span class="kpi-label">Total Requests</span><div style="font-size: 28px; font-weight: 800; color: #ffffff;">{len(display_cat_df):,} <span style="font-size: 15px; font-weight: 500; color: #94a3b8;">tickets</span></div></div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="chart-container"><div class="chart-header">📋 {selected_category} Requests Breakdown (Client Name, Partner Name, Category)</div>', unsafe_allow_html=True)
            st.dataframe(
                display_cat_df[available_target_cols].rename(columns={
                    "client_name": "Client Name",
                    "partner_name": "Partner Name",
                    "category": "Category"
                }),
                use_container_width=True,
                hide_index=True,
                height=320
            )
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 6C. SUB-SCREEN: CLIENT REQUESTS DEEP-DIVE
# =========================================================
elif st.session_state["current_page"] == "CRF_Client_Detail":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Change Requests"):
            st.session_state["current_page"] = "CRF_Tickets"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">👥 Client Request Volume & Activity</h1><div class="dashboard-subtitle">Ranking clients by Change Request ticket volume for <b>{selected_year}</b>. <i>Click on any bar to see details.</i></div></div>', unsafe_allow_html=True)

    selected_client = None

    if not filtered_crf.empty and "client_name" in filtered_crf.columns:
        client_stats = filtered_crf.groupby("client_name").agg(
            total_requests=("category", "count"),
            primary_category=("category", lambda x: x.mode()[0] if not x.empty else "N/A"),
            partner=("partner_name", lambda x: x.iloc[0] if "partner_name" in filtered_crf.columns and not x.empty else "N/A")
        ).reset_index().sort_values(by="total_requests", ascending=False)

        fig_cli = px.bar(
            client_stats.head(15),
            x="client_name",
            y="total_requests",
            text="total_requests",
            color="total_requests",
            color_continuous_scale="Blues",
            labels={"client_name": "Client", "total_requests": "Tickets"}
        )
        fig_cli.update_traces(
            textposition="outside",
            textfont=dict(size=12, color="#ffffff", family="Plus Jakarta Sans"),
            hovertemplate="<b>%{x}</b><br>Tickets: <b>%{y}</b><extra></extra>"
        )
        fig_cli.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            clickmode="event+select",
            margin=dict(t=25, b=10, l=10, r=10),
            yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
        )

        client_selection = st.plotly_chart(
            fig_cli,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="crf_client_bar_chart"
        )

        if client_selection and "selection" in client_selection and client_selection["selection"]["points"]:
            selected_client = client_selection["selection"]["points"][0].get("x")

    if selected_client:
        display_cli_df = filtered_crf[filtered_crf["client_name"].astype(str).str.lower() == str(selected_client).lower()].copy()
        partner_val = display_cli_df["partner_name"].iloc[0] if "partner_name" in display_cli_df.columns and not display_cli_df.empty else "N/A"

        k_c1, k_c2, k_c3 = st.columns(3)
        with k_c1:
            st.markdown(f'<div class="kpi-card" style="border-color: rgba(56, 189, 248, 0.5);"><div class="kpi-label">Selected Client</div><div style="font-size: 18px; font-weight: 800; color: #38bdf8; word-break: break-word;">{selected_client}</div><div class="kpi-pill pill-blue">Active Account</div></div>', unsafe_allow_html=True)
        with k_c2:
            st.markdown(f'<div class="kpi-card" style="border-color: rgba(99, 102, 241, 0.5);"><div class="kpi-label">Partner Name</div><div style="font-size: 18px; font-weight: 800; color: #818cf8; word-break: break-word;">{partner_val}</div><div class="kpi-pill pill-blue">Associated Partner</div></div>', unsafe_allow_html=True)
        with k_c3:
            st.markdown(f'<div class="kpi-card" style="border-color: rgba(168, 85, 247, 0.5);"><div class="kpi-label">Total CRF Tickets</div><div class="kpi-value">{len(display_cli_df):,}</div><div class="kpi-pill pill-purple">Total Requests</div></div>', unsafe_allow_html=True)


# ==========================================
# 7. SCREEN 3: DEDICATED OE SETUP SCREEN
# ==========================================
elif st.session_state["current_page"] == "OE_Setup":
    top_col1, top_col2 = st.columns([2, 8])
    with top_col1:
        if st.button("← Back to Overview"):
            st.session_state["current_page"] = "Overview"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">🎯 Open Enrollment (OE) Tracker - Detailed Screen</h1><div class="dashboard-subtitle">Client renewal progress, setup statuses, review workflows, and timeline milestones for <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    total_oe_clients = len(filtered_oe[filtered_oe["client"].notna() & (filtered_oe["client"] != "")])
    completed_oe_clients = len(filtered_oe[filtered_oe["oe_setup_status"].astype(str).str.lower() == "completed"])
    pending_oe_clients = total_oe_clients - completed_oe_clients
    oe_rate_detail = (completed_oe_clients / total_oe_clients * 100) if total_oe_clients > 0 else 0
    
    o1, o2, o3 = st.columns(3)
    with o1:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(59, 130, 246, 0.4);"><div class="kpi-label">Total OE Clients</div><div class="kpi-value">{total_oe_clients:,}</div><div class="kpi-pill pill-blue">{selected_year} Pipeline</div></div>', unsafe_allow_html=True)
        if st.button("📋 All OE Clients →", key="btn_oe_all_clients"):
            st.session_state["current_page"] = "OE_All_Clients"
            st.rerun()

    with o2:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(168, 85, 247, 0.4);"><div class="kpi-label">Setup Completed</div><div class="kpi-value">{completed_oe_clients:,}</div><div class="kpi-pill pill-purple">{oe_rate_detail:.1f}% Completed</div></div>', unsafe_allow_html=True)
        if st.button("✅ Completed Setups →", key="btn_oe_completed"):
            st.session_state["current_page"] = "OE_Completed_Clients"
            st.rerun()

    with o3:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(239, 68, 68, 0.4);"><div class="kpi-label">Setup In-Progress / Pending</div><div class="kpi-value">{pending_oe_clients:,}</div><div class="kpi-pill pill-red">Active Workflows</div></div>', unsafe_allow_html=True)
        if st.button("⏳ Pending Workflows →", key="btn_oe_pending"):
            st.session_state["current_page"] = "OE_Pending_Clients"
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    selected_status = None

    st.markdown(
        '<div class="chart-container"><div class="chart-header">📊 OE Setup Status Distribution</div>'
        '<div style="color: #94a3b8; font-size: 13px; margin-bottom: 10px;"><i>Click on any status bar to view all matching clients.</i></div>',
        unsafe_allow_html=True
    )
    
    if not filtered_oe.empty and "oe_setup_status" in filtered_oe.columns:
        status_df = filtered_oe["oe_setup_status"].fillna("Pending/Not Started").value_counts().reset_index()
        status_df.columns = ["Status", "Clients"]
        
        fig_status_bar = px.bar(
            status_df,
            x="Clients",
            y="Status",
            orientation="h",
            color="Status",
            text="Clients",
            color_discrete_map={
                "Completed": "#10b981",
                "Pending/Not Started": "#f59e0b",
                "In-Progress": "#6366f1"
            }
        )
        fig_status_bar.update_traces(
            textposition="outside",
            textfont=dict(size=13, color="#ffffff", family="Plus Jakarta Sans"),
            hovertemplate="<b>Status: %{y}</b><br>Clients: <b>%{x}</b><extra></extra>"
        )
        fig_status_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=260,
            clickmode="event+select",
            showlegend=False,
            margin=dict(t=20, b=10, l=10, r=20),
            xaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
        )

        status_selection = st.plotly_chart(
            fig_status_bar,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="oe_setup_status_chart"
        )

        if status_selection and "selection" in status_selection and status_selection["selection"]["points"]:
            selected_status = str(status_selection["selection"]["points"][0].get("y")).strip()

    if selected_status:
        status_matched_df = filtered_oe[
            filtered_oe["oe_setup_status"].fillna("Pending/Not Started").astype(str).str.lower() == selected_status.lower()
        ].copy()

        st.markdown(
            f'<div class="kpi-card" style="margin-top: 10px; margin-bottom: 20px; border-color: rgba(16, 185, 129, 0.6); '
            f'display: flex; justify-content: space-between; align-items: center; padding: 16px 24px;">'
            f'<div><span class="kpi-label">Selected Status</span>'
            f'<div style="font-size: 22px; font-weight: 800; color: #34d399;">{selected_status}</div></div>'
            f'<div style="text-align: right;"><span class="kpi-label">Client Count</span>'
            f'<div style="font-size: 26px; font-weight: 800; color: #ffffff;">{len(status_matched_df):,} <span style="font-size: 14px; font-weight: 500; color: #94a3b8;">clients</span></div></div></div>',
            unsafe_allow_html=True
        )

        display_cols = [
            "client", "crm", "config_analyst", "oe_type", "oe_effective",
            "oe_setup_status", "reviewtesting_status", "oe_closure"
        ]
        available_cols = [c for c in display_cols if c in status_matched_df.columns]

        st.markdown(
            f'<div class="chart-container"><div class="chart-header">📋 Clients with Setup Status: {selected_status}</div>',
            unsafe_allow_html=True
        )
        st.dataframe(
            status_matched_df[available_cols].rename(columns={c: format_col_header(c) for c in available_cols}),
            use_container_width=True,
            hide_index=True,
            height=320
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 7A. SUB-SCREEN: ALL OE CLIENTS MASTER AUDIT LOG
# =========================================================
elif st.session_state["current_page"] == "OE_All_Clients":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to OE Screen"):
            st.session_state["current_page"] = "OE_Setup"
            st.rerun()

    st.markdown(
        f'<div class="dashboard-header" style="margin-top: 10px;">'
        f'<h1 class="dashboard-title">📋 All Open Enrollment Clients - Master Audit Log</h1>'
        f'<div class="dashboard-subtitle">Master records for all {len(filtered_oe)} OE client accounts in <b>{selected_year}</b>. '
        f'<i>Click on any bar to view the clients and respective CRM breakdown for that OE Effective Date.</i></div></div>',
        unsafe_allow_html=True
    )

    selected_effective_date = None

    if not filtered_oe.empty and "oe_effective" in filtered_oe.columns:
        oe_copy = filtered_oe.copy()
        oe_copy["oe_effective_clean"] = (
            oe_copy["oe_effective"]
            .astype(str)
            .str.split("T").str[0]
            .str.split(" ").str[0]
            .str.strip()
        )
        oe_copy["oe_effective_clean"] = oe_copy["oe_effective_clean"].replace({"nan": "Unknown", "None": "Unknown", "": "Unknown"})

        oe_copy["status_category"] = oe_copy["oe_setup_status"].apply(
            lambda x: "Completed" if str(x).strip().lower() == "completed" else "In-Progress / Pending"
        )

        eff_df = (
            oe_copy.groupby(["oe_effective_clean", "status_category"], as_index=False)
            .agg(client_count=("client", "count"))
            .sort_values(by=["oe_effective_clean", "status_category"])
        )

        fig_eff = px.bar(
            eff_df,
            x="oe_effective_clean",
            y="client_count",
            color="status_category",
            text="client_count",
            barmode="stack",
            color_discrete_map={
                "Completed": "#10b981",              
                "In-Progress / Pending": "#f59e0b"     
            },
            labels={
                "oe_effective_clean": "OE Effective Date",
                "client_count": "Client Count",
                "status_category": "Setup Status"
            }
        )
        fig_eff.update_xaxes(type="category")
        fig_eff.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=12, color="#ffffff", family="Plus Jakarta Sans"),
            hovertemplate="<b>OE Date: %{x}</b><br>Status: %{fullData.name}<br>Clients: <b>%{y}</b><extra></extra>"
        )
        fig_eff.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            clickmode="event+select",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=dict(text="")
            ),
            margin=dict(t=30, b=10, l=10, r=10),
            yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
        )

        chart_selection = st.plotly_chart(
            fig_eff,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="oe_effective_bar_chart"
        )

        if chart_selection and "selection" in chart_selection and chart_selection["selection"]["points"]:
            selected_effective_date = str(chart_selection["selection"]["points"][0].get("x")).strip()

        if selected_effective_date:
            matched_clients_df = oe_copy[
                oe_copy["oe_effective_clean"].str.lower() == selected_effective_date.lower()
            ].copy()

            comp_count = len(matched_clients_df[matched_clients_df["status_category"] == "Completed"])
            pend_count = len(matched_clients_df[matched_clients_df["status_category"] != "Completed"])

            st.markdown(
                f'<div class="kpi-card" style="margin-top: 10px; margin-bottom: 20px; border-color: rgba(56, 189, 248, 0.6); '
                f'display: flex; justify-content: space-between; align-items: center; padding: 16px 24px;">'
                f'<div><span class="kpi-label">Selected OE Effective Date</span>'
                f'<div style="font-size: 22px; font-weight: 800; color: #38bdf8;">{selected_effective_date}</div></div>'
                f'<div style="display: flex; gap: 12px; align-items: center;">'
                f'<div class="kpi-pill pill-green">✅ {comp_count} Completed</div>'
                f'<div class="kpi-pill pill-yellow">⏳ {pend_count} Pending</div>'
                f'<div style="text-align: right; margin-left: 10px;"><span class="kpi-label">Total</span>'
                f'<div style="font-size: 24px; font-weight: 800; color: #ffffff;">{len(matched_clients_df):,}</div></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

            crm_breakdown_col1, crm_breakdown_col2 = st.columns([5, 5])
            with crm_breakdown_col1:
                if "crm" in matched_clients_df.columns:
                    st.markdown('<div class="chart-container"><div class="chart-header">📊 Breakdown by Respective CRM</div>', unsafe_allow_html=True)
                    crm_stats = matched_clients_df["crm"].fillna("Unassigned").value_counts().reset_index()
                    crm_stats.columns = ["CRM Lead", "Client Count"]
                    fig_crm_sub = px.bar(
                        crm_stats,
                        x="CRM Lead",
                        y="Client Count",
                        color="Client Count",
                        color_continuous_scale="Teal",
                        text="Client Count"
                    )
                    fig_crm_sub.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=280,
                        margin=dict(t=10, b=10, l=10, r=10)
                    )
                    st.plotly_chart(fig_crm_sub, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            display_cols = [
                "client", "crm", "config_analyst", "oe_type",
                "oe_effective", "oe_setup_status", "reviewtesting_status", "oe_closure"
            ]
            available_cols = [c for c in display_cols if c in matched_clients_df.columns]

            st.markdown(
                f'<div class="chart-container"><div class="chart-header">📋 Clients Enrolled for {selected_effective_date} (with Respective CRM)</div>',
                unsafe_allow_html=True
            )
            st.dataframe(
                matched_clients_df[available_cols].rename(columns={c: format_col_header(c) for c in available_cols}),
                use_container_width=True,
                hide_index=True,
                height=320
            )
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 7B. SUB-SCREEN: COMPLETED OE SETUPS
# =========================================================
elif st.session_state["current_page"] == "OE_Completed_Clients":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to OE Screen"):
            st.session_state["current_page"] = "OE_Setup"
            st.rerun()

    completed_df = filtered_oe[filtered_oe["oe_setup_status"].astype(str).str.lower() == "completed"]

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">✅ Completed Open Enrollment Setups</h1><div class="dashboard-subtitle">Detailed records for all {len(completed_df)} completed OE clients in <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(168, 85, 247, 0.4);"><div class="kpi-label">Completed Clients</div><div class="kpi-value">{len(completed_df):,}</div><div class="kpi-pill pill-green">Ready & Live</div></div>', unsafe_allow_html=True)
    with c_col2:
        finalized_count = len(completed_df[completed_df["oe_closure"].astype(str).str.lower() == "completed"]) if "oe_closure" in completed_df.columns else 0
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(34, 197, 94, 0.4);"><div class="kpi-label">Fully Closed / Finalized</div><div class="kpi-value">{finalized_count:,}</div><div class="kpi-pill pill-green">Closure Achieved</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="chart-container"><div class="chart-header">📋 Completed OE Client Log</div>', unsafe_allow_html=True)
    
    completed_display_df = completed_df.rename(columns={c: format_col_header(c) for c in completed_df.columns})
    st.dataframe(completed_display_df, use_container_width=True, hide_index=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 7C. SUB-SCREEN: PENDING / IN-PROGRESS OE WORKFLOWS
# =========================================================
elif st.session_state["current_page"] == "OE_Pending_Clients":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to OE Screen"):
            st.session_state["current_page"] = "OE_Setup"
            st.rerun()

    pending_df = filtered_oe[filtered_oe["oe_setup_status"].astype(str).str.lower() != "completed"].copy()

    st.markdown(
        f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">⏳ In-Progress & Pending OE Setups</h1>'
        f'<div class="dashboard-subtitle">Active pipeline tracking for {len(pending_df)} pending OE accounts in <b>{selected_year}</b>. '
        f'<i>Click on any bar to view pending clients for that CRM Lead.</i></div></div>',
        unsafe_allow_html=True
    )

    selected_crm = None

    if not pending_df.empty and "crm" in pending_df.columns:
        p_crm = pending_df["crm"].fillna("Unassigned").value_counts().reset_index()
        p_crm.columns = ["CRM Lead", "Pending Setups"]
        fig_pcrm = px.bar(
            p_crm,
            x="CRM Lead",
            y="Pending Setups",
            color="Pending Setups",
            color_continuous_scale="Reds",
            text="Pending Setups"
        )
        fig_pcrm.update_traces(
            textposition="outside",
            textfont=dict(size=13, color="#ffffff", family="Plus Jakarta Sans"),
            hovertemplate="<b>CRM Lead: %{x}</b><br>Pending Setups: <b>%{y}</b><extra></extra>"
        )
        fig_pcrm.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320,
            clickmode="event+select",
            margin=dict(t=30, b=10, l=10, r=10),
            yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
        )
        
        crm_chart_selection = st.plotly_chart(
            fig_pcrm,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="oe_pending_crm_chart"
        )

        if crm_chart_selection and "selection" in crm_chart_selection and crm_chart_selection["selection"]["points"]:
            selected_crm = str(crm_chart_selection["selection"]["points"][0].get("x")).strip()

    if selected_crm:
        crm_matched_df = pending_df[
            pending_df["crm"].fillna("Unassigned").astype(str).str.lower() == selected_crm.lower()
        ].copy()

        st.markdown(
            f'<div class="kpi-card" style="margin-top: 10px; margin-bottom: 20px; border-color: rgba(239, 68, 68, 0.6); '
            f'display: flex; justify-content: space-between; align-items: center; padding: 16px 24px;">'
            f'<div><span class="kpi-label">Selected CRM Lead</span>'
            f'<div style="font-size: 22px; font-weight: 800; color: #f87171;">{selected_crm}</div></div>'
            f'<div style="text-align: right;"><span class="kpi-label">Pending Workflows</span>'
            f'<div style="font-size: 26px; font-weight: 800; color: #ffffff;">{len(crm_matched_df):,} <span style="font-size: 14px; font-weight: 500; color: #94a3b8;">accounts</span></div></div></div>',
            unsafe_allow_html=True
        )

        display_cols = [
            "client", "crm", "config_analyst", "oe_type", "oe_effective",
            "oe_setup_status", "reviewtesting_status", "oe_closure"
        ]
        available_cols = [c for c in display_cols if c in crm_matched_df.columns]

        st.markdown(
            f'<div class="chart-container"><div class="chart-header">📋 Pending Clients for CRM: {selected_crm}</div>',
            unsafe_allow_html=True
        )
        st.dataframe(
            crm_matched_df[available_cols].rename(columns={c: format_col_header(c) for c in available_cols}),
            use_container_width=True,
            hide_index=True,
            height=320
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 8. SCREEN 4: DEDICATED LIVE CLIENTS SCREEN
# ==========================================
elif st.session_state["current_page"] == "Live_Clients":
    top_col1, top_col2 = st.columns([2, 8])
    with top_col1:
        if st.button("← Back to Overview"):
            st.session_state["current_page"] = "Overview"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">🚀 Client Implementation & Go-Live Detailed Screen</h1><div class="dashboard-subtitle">Active implementations, Go-Live timelines, Yet-to-Live pipeline, and Employee Headcount tracking for <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    live_df = filtered_impl[filtered_impl["status"] == "Implemented"]
    yet_df = filtered_impl[filtered_impl["status"] == "Yet to Live"]
    
    total_live = len(live_df)
    total_yet = len(yet_df)
    total_headcount_live = live_df["headcount"].sum()
    total_headcount_yet = yet_df["headcount"].sum()

    l1, l2, l3, l4 = st.columns(4)
    with l1:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(34, 197, 94, 0.4);"><div class="kpi-label">Implemented (Live) Clients</div><div class="kpi-value">{total_live:,}</div><div class="kpi-pill pill-green">Active on Platform</div></div>', unsafe_allow_html=True)
        if st.button("🚀 Live Clients Log →", key="btn_impl_live"):
            st.session_state["current_page"] = "Impl_Live_Clients"
            st.rerun()

    with l2:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(59, 130, 246, 0.4);"><div class="kpi-label">Yet-to-Live Pipeline</div><div class="kpi-value">{total_yet:,}</div><div class="kpi-pill pill-blue">In Implementation</div></div>', unsafe_allow_html=True)
        if st.button("⏳ Pipeline Drilldown →", key="btn_impl_pipeline"):
            st.session_state["current_page"] = "Impl_Yet_To_Live"
            st.rerun()

    with l3:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(168, 85, 247, 0.4);"><div class="kpi-label">Live Client Headcount</div><div class="kpi-value">{total_headcount_live:,}</div><div class="kpi-pill pill-purple">Employees Covered</div></div>', unsafe_allow_html=True)
        if st.button("👥 Live Client Headcount →", key="btn_impl_live_hc"):
            st.session_state["current_page"] = "Impl_Live_Headcount"
            st.rerun()

    with l4:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(99, 102, 241, 0.4);"><div class="kpi-label">Pending Client Headcount</div><div class="kpi-value">{total_headcount_yet:,}</div><div class="kpi-pill pill-blue">Employees Pending</div></div>', unsafe_allow_html=True)
        if st.button("📈 Pending Client Headcount →", key="btn_impl_pipe_hc"):
            st.session_state["current_page"] = "Pending_Client_Headcount"
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    live_c1, live_c2 = st.columns([6, 4])
    with live_c1:
        st.markdown('<div class="chart-container"><div class="chart-header">📊 Headcount by Live Client</div>', unsafe_allow_html=True)
        if not live_df.empty:
            headcount_sorted = live_df[live_df["headcount"] > 0].sort_values(by="headcount", ascending=True)
            if not headcount_sorted.empty:
                fig_hc = px.bar(
                    headcount_sorted,
                    x="headcount",
                    y="client_name",
                    orientation="h",
                    color="headcount",
                    color_continuous_scale="Blues",
                    labels={"headcount": "Employee Headcount", "client_name": "Client"}
                )
                fig_hc.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    height=320,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_hc, use_container_width=True)
            else:
                st.info("No headcount data logged for live clients.")
        else:
            st.info("No live clients available.")
        st.markdown('</div>', unsafe_allow_html=True)

    with live_c2:
        st.markdown('<div class="chart-container"><div class="chart-header">🎯 Implementation Stage Split</div>', unsafe_allow_html=True)
        if not filtered_impl.empty:
            stage_df = filtered_impl["status"].value_counts().reset_index()
            stage_df.columns = ["Stage", "Count"]
            fig_stage = px.pie(
                stage_df,
                names="Stage",
                values="Count",
                hole=0.45,
                color="Stage",
                color_discrete_map={"Implemented": "#38bdf8", "Yet to Live": "#f59e0b"}
            )
            fig_stage.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                margin=dict(t=10, b=10)
            )
            st.plotly_chart(fig_stage, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 8A. SUB-SCREEN: IMPLEMENTED (LIVE) CLIENTS MASTER SCREEN
# =========================================================
elif st.session_state["current_page"] == "Impl_Live_Clients":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Implementation"):
            st.session_state["current_page"] = "Live_Clients"
            st.rerun()

    live_df = filtered_impl[filtered_impl["status"] == "Implemented"].copy()

    st.markdown(
        f'<div class="dashboard-header" style="margin-top: 10px;">'
        f'<h1 class="dashboard-title">🚀 Implemented & Live Clients - Master Log</h1>'
        f'<div class="dashboard-subtitle">Complete records of {len(live_df)} clients successfully transitioned to Live status in <b>{selected_year}</b>. '
        f'<i>Click on any bar to see the client list for that Go-Live Date.</i></div></div>',
        unsafe_allow_html=True
    )

    selected_golive_date = None

    if not live_df.empty and "client_go_live_date" in live_df.columns:
        live_df["clean_go_live"] = (
            live_df["client_go_live_date"]
            .astype(str)
            .str.split("T").str[0]
            .str.split(" ").str[0]
            .str.strip()
        )
        live_df["clean_go_live"] = live_df["clean_go_live"].replace({"nan": "Unknown", "None": "Unknown", "": "Unknown"})

        gl_counts = (
            live_df.groupby("clean_go_live", as_index=False)
            .agg(client_count=("client_name", "count"))
            .sort_values(by="clean_go_live")
        )

        fig_gl = px.bar(
            gl_counts,
            x="clean_go_live",
            y="client_count",
            text="client_count",
            color="client_count",
            color_continuous_scale="Blues",
            labels={"clean_go_live": "Go Live Date", "client_count": "Live Clients"}
        )
        fig_gl.update_xaxes(type="category")
        fig_gl.update_traces(
            textposition="outside",
            textfont=dict(size=12, color="#ffffff", family="Plus Jakarta Sans"),
            hovertemplate="<b>Go Live Date: %{x}</b><br>Clients: <b>%{y}</b><extra></extra>"
        )
        fig_gl.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320,
            clickmode="event+select",
            coloraxis_showscale=False,
            margin=dict(t=30, b=10, l=10, r=10),
            yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
        )

        chart_selection = st.plotly_chart(
            fig_gl,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="impl_live_chart"
        )

        if chart_selection and "selection" in chart_selection and chart_selection["selection"]["points"]:
            selected_golive_date = str(chart_selection["selection"]["points"][0].get("x")).strip()

        if selected_golive_date:
            display_live_df = live_df[live_df["clean_go_live"].str.lower() == selected_golive_date.lower()].copy()

            st.markdown(
                f'<div class="kpi-card" style="margin-top: 10px; margin-bottom: 20px; border-color: rgba(56, 189, 248, 0.6); '
                f'display: flex; justify-content: space-between; align-items: center; padding: 16px 24px;">'
                f'<div><span class="kpi-label">Selected Go-Live Date</span>'
                f'<div style="font-size: 22px; font-weight: 800; color: #38bdf8;">{selected_golive_date}</div></div>'
                f'<div style="text-align: right;"><span class="kpi-label">Live Clients</span>'
                f'<div style="font-size: 26px; font-weight: 800; color: #ffffff;">{len(display_live_df):,} <span style="font-size: 14px; font-weight: 500; color: #94a3b8;">accounts</span></div></div></div>',
                unsafe_allow_html=True
            )

            display_cols = [
                "client_name", "broker", "design_guide_received_date",
                "implementation_completion_date", "client_go_live_date", "headcount"
            ]
            available_cols = [c for c in display_cols if c in display_live_df.columns]

            st.markdown(
                f'<div class="chart-container"><div class="chart-header">📋 Clients Live on {selected_golive_date}</div>',
                unsafe_allow_html=True
            )
            st.dataframe(
                display_live_df[available_cols].rename(columns={c: format_col_header(c) for c in available_cols}),
                use_container_width=True,
                hide_index=True,
                height=320
            )
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 8B. SUB-SCREEN: YET-TO-LIVE PIPELINE
# =========================================================
elif st.session_state["current_page"] == "Impl_Yet_To_Live":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Implementation"):
            st.session_state["current_page"] = "Live_Clients"
            st.rerun()

    yet_df = filtered_impl[filtered_impl["status"] == "Yet to Live"].copy()

    st.markdown(
        f'<div class="dashboard-header" style="margin-top: 10px;">'
        f'<h1 class="dashboard-title">⏳ Yet-To-Live Implementation Pipeline</h1>'
        f'<div class="dashboard-subtitle">Tracking {len(yet_df)} clients currently moving through configuration towards Go-Live in <b>{selected_year}</b></div></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="kpi-card" style="border-color: rgba(59, 130, 246, 0.4); margin-bottom: 20px;">'
        f'<div class="kpi-label">Clients in Pipeline</div>'
        f'<div class="kpi-value">{len(yet_df):,}</div>'
        f'<div class="kpi-pill pill-blue">In Progress</div></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="chart-container"><div class="chart-header">📋 Pipeline Clients Tracker Table</div>', unsafe_allow_html=True)
    
    pipeline_cols = [
        "client_name", "broker", "design_guide_received_date",
        "implementation_completion_date", "client_go_live_date",
        "headcount", "status", "year"
    ]
    available_cols = [c for c in pipeline_cols if c in yet_df.columns]
    
    yet_display_df = yet_df[available_cols].rename(columns={c: format_col_header(c) for c in available_cols})
    st.dataframe(yet_display_df, use_container_width=True, hide_index=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 8C. SUB-SCREEN: LIVE HEADCOUNT ANALYTICS
# =========================================================
elif st.session_state["current_page"] == "Impl_Live_Headcount":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Implementation"):
            st.session_state["current_page"] = "Live_Clients"
            st.rerun()

    live_df = filtered_impl[filtered_impl["status"] == "Implemented"]
    total_live_hc = live_df["headcount"].sum()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">👥 Live Employee Headcount Analytics</h1><div class="dashboard-subtitle">Total of <b>{total_live_hc:,}</b> employees covered across all live implementations in <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    if not live_df.empty:
        hc_c1, hc_c2 = st.columns([6, 4])
        with hc_c1:
            st.markdown('<div class="chart-container"><div class="chart-header">📊 Headcount Ranking by Client</div>', unsafe_allow_html=True)
            fig_lhc = px.bar(
                live_df.sort_values(by="headcount", ascending=True),
                x="headcount",
                y="client_name",
                orientation="h",
                color="headcount",
                color_continuous_scale="Teal",
                labels={"headcount": "Employees", "client_name": "Client"}
            )
            fig_lhc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340)
            st.plotly_chart(fig_lhc, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with hc_c2:
            st.markdown('<div class="chart-container"><div class="chart-header">🏢 Headcount Share by Broker</div>', unsafe_allow_html=True)
            if "broker" in live_df.columns:
                broker_hc = live_df.groupby("broker")["headcount"].sum().reset_index()
                fig_bhc = px.pie(broker_hc, names="broker", values="headcount", hole=0.45, color_discrete_sequence=px.colors.sequential.Teal)
                fig_bhc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340)
                st.plotly_chart(fig_bhc, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 8D. SUB-SCREEN: PIPELINE HEADCOUNT ANALYTICS
# =========================================================
elif st.session_state["current_page"] == "Pending_Client_Headcount":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Implementation"):
            st.session_state["current_page"] = "Live_Clients"
            st.rerun()

    yet_df = filtered_impl[filtered_impl["status"] == "Yet to Live"].copy()
    total_pipe_hc = yet_df["headcount"].sum()

    st.markdown(
        f'<div class="dashboard-header" style="margin-top: 10px;">'
        f'<h1 class="dashboard-title">📈 Pipeline Headcount & Capacity Forecast</h1>'
        f'<div class="dashboard-subtitle">Forecast of <b>{total_pipe_hc:,}</b> upcoming employees currently in the onboarding pipeline for <b>{selected_year}</b></div></div>',
        unsafe_allow_html=True
    )

    if not yet_df.empty:
        phc_df = yet_df[yet_df["headcount"] > 0].sort_values(by="headcount", ascending=True)
        if not phc_df.empty:
            fig_phc = px.bar(
                phc_df,
                x="headcount",
                y="client_name",
                orientation="h",
                color="headcount",
                color_continuous_scale="Purples",
                labels={"headcount": "Pipeline Employees", "client_name": "Client"}
            )
            fig_phc.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320
            )
            st.plotly_chart(fig_phc, use_container_width=True)

    st.markdown('<div class="chart-container"><div class="chart-header">📋 Pipeline Clients Headcount Breakdown</div>', unsafe_allow_html=True)
    
    pipeline_cols = [
        "client_name", "broker", "design_guide_received_date",
        "implementation_completion_date", "client_go_live_date",
        "headcount", "status", "year"
    ]
    available_cols = [c for c in pipeline_cols if c in yet_df.columns]
    
    pipeline_display_df = yet_df[available_cols].rename(columns={c: format_col_header(c) for c in available_cols})
    st.dataframe(pipeline_display_df, use_container_width=True, hide_index=True, height=350)
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 9. SCREEN 5: DEDICATED TERMINATIONS SCREEN
# ==========================================
elif st.session_state["current_page"] == "Terminations":
    top_col1, top_col2 = st.columns([2, 8])
    with top_col1:
        if st.button("← Back to Overview"):
            st.session_state["current_page"] = "Overview"
            st.rerun()

    st.markdown(
        f'<div class="dashboard-header" style="margin-top: 10px;">'
        f'<h1 class="dashboard-title">⚠️ Client Terminations & Churn Detailed Screen</h1>'
        f'<div class="dashboard-subtitle">Account churn logs, termination reasons breakdown, lost employee headcount, and broker impact for <b>{selected_year}</b></div></div>',
        unsafe_allow_html=True
    )

    total_terminated = len(filtered_term)
    total_lost_headcount = filtered_term["headcount"].sum() if "headcount" in filtered_term.columns else 0

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            f'<div class="kpi-card" style="border-color: rgba(239, 68, 68, 0.4);">'
            f'<div class="kpi-label">Terminated Accounts</div>'
            f'<div class="kpi-value">{total_terminated:,}</div>'
            f'<div class="kpi-pill pill-red">Lost Clients</div></div>',
            unsafe_allow_html=True
        )
        if st.button("📋 All Terminations Log →", key="btn_term_all"):
            st.session_state["current_page"] = "Term_All_Clients"
            st.rerun()

    with t2:
        st.markdown(
            f'<div class="kpi-card" style="border-color: rgba(244, 63, 94, 0.4);">'
            f'<div class="kpi-label">Total Lost Headcount</div>'
            f'<div class="kpi-value">{total_lost_headcount:,}</div>'
            f'<div class="kpi-pill pill-red">Employees Lost</div></div>',
            unsafe_allow_html=True
        )
        if st.button("👥 Lost Headcount Drilldown →", key="btn_term_hc"):
            st.session_state["current_page"] = "Term_Headcount_Detail"
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    term_c1, term_c2 = st.columns([5, 5])
    with term_c1:
        st.markdown('<div class="chart-container"><div class="chart-header">📊 Termination Reasons Breakdown</div>', unsafe_allow_html=True)
        if not filtered_term.empty and "reason" in filtered_term.columns and not filtered_term["reason"].dropna().empty:
            reasons_df = filtered_term["reason"].dropna().value_counts().reset_index()
            reasons_df.columns = ["reason", "count"]
            fig_reasons = px.pie(
                reasons_df,
                names="reason",
                values="count",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            fig_reasons.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                margin=dict(t=10, b=10)
            )
            st.plotly_chart(fig_reasons, use_container_width=True)
        else:
            st.info("No churn reasons logged for this selection.")
        st.markdown('</div>', unsafe_allow_html=True)

    with term_c2:
        st.markdown('<div class="chart-container"><div class="chart-header">👥 Lost Headcount by Terminated Client</div>', unsafe_allow_html=True)
        if not filtered_term.empty and "headcount" in filtered_term.columns:
            term_sorted = filtered_term[filtered_term["headcount"] > 0].sort_values(by="headcount", ascending=True)
            if not term_sorted.empty:
                fig_term_hc = px.bar(
                    term_sorted,
                    x="headcount",
                    y="client_name",
                    orientation="h",
                    color="headcount",
                    color_continuous_scale="Reds",
                    labels={"headcount": "Lost Headcount", "client_name": "Client"}
                )
                fig_term_hc.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    height=320,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_term_hc, use_container_width=True)
            else:
                st.info("No headcount data logged for terminated clients.")
        else:
            st.info("No terminated clients available.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="chart-container"><div class="chart-header">📋 {selected_year} Terminated Clients Master Audit Log</div>', unsafe_allow_html=True)
    term_display_cols = ["sl_no", "client_name", "broker", "termination_effective_date", "headcount", "reason"]
    avail_term_cols = [c for c in term_display_cols if c in filtered_term.columns]
    
    table_term_df = filtered_term[avail_term_cols].rename(columns={c: format_col_header(c) for c in avail_term_cols})
    st.dataframe(table_term_df, use_container_width=True, hide_index=True, height=380)

    term_csv = table_term_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Terminations Master Records (CSV)",
        data=term_csv,
        file_name=f"Terminated_Clients_{selected_year}.csv",
        mime="text/csv"
    )
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 9A. SUB-SCREEN: ALL TERMINATED ACCOUNTS AUDIT LOG
# =========================================================
elif st.session_state["current_page"] == "Term_All_Clients":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Terminations"):
            st.session_state["current_page"] = "Terminations"
            st.rerun()

    term_df_clean = filtered_term.copy()

    st.markdown(
        f'<div class="dashboard-header" style="margin-top: 10px;">'
        f'<h1 class="dashboard-title">📋 Terminated Accounts - Master Audit Log</h1>'
        f'<div class="dashboard-subtitle">Complete records for all {len(term_df_clean)} terminated client accounts in <b>{selected_year}</b>. '
        f'<i>Click on any bar to view the terminated clients for that effective date.</i></div></div>',
        unsafe_allow_html=True
    )

    selected_term_date = None

    if not term_df_clean.empty and "termination_effective_date" in term_df_clean.columns:
        term_df_clean["clean_term_date"] = (
            term_df_clean["termination_effective_date"]
            .astype(str)
            .str.split("T").str[0]
            .str.split(" ").str[0]
            .str.strip()
        )
        term_df_clean["clean_term_date"] = term_df_clean["clean_term_date"].replace(
            {"nan": "Unknown", "None": "Unknown", "": "Unknown"}
        )

        term_counts = (
            term_df_clean.groupby("clean_term_date", as_index=False)
            .agg(client_count=("client_name", "count"))
            .sort_values(by="clean_term_date")
        )

        fig_term = px.bar(
            term_counts,
            x="clean_term_date",
            y="client_count",
            text="client_count",
            color="client_count",
            color_continuous_scale="Reds",
            labels={"clean_term_date": "Termination Date", "client_count": "Terminations"}
        )
        fig_term.update_xaxes(type="category")
        fig_term.update_traces(
            textposition="outside",
            textfont=dict(size=12, color="#ffffff", family="Plus Jakarta Sans"),
            hovertemplate="<b>Termination Date: %{x}</b><br>Terminated Clients: <b>%{y}</b><extra></extra>"
        )
        fig_term.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320,
            clickmode="event+select",
            coloraxis_showscale=False,
            margin=dict(t=30, b=10, l=10, r=10),
            yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)")
        )

        chart_selection = st.plotly_chart(
            fig_term,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="term_date_chart"
        )

        if chart_selection and "selection" in chart_selection and chart_selection["selection"]["points"]:
            selected_term_date = str(chart_selection["selection"]["points"][0].get("x")).strip()

        if selected_term_date:
            display_term_df = term_df_clean[
                term_df_clean["clean_term_date"].str.lower() == selected_term_date.lower()
            ].copy()

            st.markdown(
                f'<div class="kpi-card" style="margin-top: 10px; margin-bottom: 20px; border-color: rgba(239, 68, 68, 0.6); '
                f'display: flex; justify-content: space-between; align-items: center; padding: 16px 24px;">'
                f'<div><span class="kpi-label">Selected Termination Date</span>'
                f'<div style="font-size: 22px; font-weight: 800; color: #f87171;">{selected_term_date}</div></div>'
                f'<div style="text-align: right;"><span class="kpi-label">Terminated Clients</span>'
                f'<div style="font-size: 26px; font-weight: 800; color: #ffffff;">{len(display_term_df):,} <span style="font-size: 14px; font-weight: 500; color: #94a3b8;">accounts</span></div></div></div>',
                unsafe_allow_html=True
            )

            term_cols = [
                "client_name", "broker", "termination_effective_date",
                "headcount", "reason", "status", "year"
            ]
            available_term_cols = [c for c in term_cols if c in display_term_df.columns]

            st.markdown(
                f'<div class="chart-container"><div class="chart-header">📋 Clients Terminated on {selected_term_date}</div>',
                unsafe_allow_html=True
            )
            st.dataframe(
                display_term_df[available_term_cols].rename(columns={c: format_col_header(c) for c in available_term_cols}),
                use_container_width=True,
                hide_index=True,
                height=320
            )
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 9B. SUB-SCREEN: LOST HEADCOUNT DEEP-DIVE
# =========================================================
elif st.session_state["current_page"] == "Term_Headcount_Detail":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Terminations"):
            st.session_state["current_page"] = "Terminations"
            st.rerun()

    total_lost_hc = filtered_term["headcount"].sum()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">👥 Lost Headcount Impact Analytics</h1><div class="dashboard-subtitle">Total employee loss of <b>{total_lost_hc:,}</b> across churned clients in <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    if not filtered_term.empty and "headcount" in filtered_term.columns:
        thc_c1, thc_c2 = st.columns([6, 4])
        with thc_c1:
            st.markdown('<div class="chart-container"><div class="chart-header">📊 Headcount Loss Ranking</div>', unsafe_allow_html=True)
            fig_tlhc = px.bar(
                filtered_term.sort_values(by="headcount", ascending=True),
                x="headcount",
                y="client_name",
                orientation="h",
                color="headcount",
                color_continuous_scale="Reds",
                labels={"headcount": "Lost Employees", "client_name": "Client"}
            )
            fig_tlhc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340)
            st.plotly_chart(fig_tlhc, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with thc_c2:
            st.markdown('<div class="chart-container"><div class="chart-header">🏢 Lost Headcount by Broker</div>', unsafe_allow_html=True)
            if "broker" in filtered_term.columns:
                broker_thc = filtered_term.groupby("broker")["headcount"].sum().reset_index()
                fig_bthc = px.pie(broker_thc, names="broker", values="headcount", hole=0.45, color_discrete_sequence=px.colors.sequential.Reds_r)
                fig_bthc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340)
                st.plotly_chart(fig_bthc, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 9C. SUB-SCREEN: AVG HEADCOUNT / SIZING ANALYTICS
# =========================================================
elif st.session_state["current_page"] == "Term_Avg_Headcount":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Terminations"):
            st.session_state["current_page"] = "Terminations"
            st.rerun()

    avg_hc = (filtered_term["headcount"].sum() / len(filtered_term)) if len(filtered_term) > 0 else 0

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">📊 Average Account Size & Sizing Impact</h1><div class="dashboard-subtitle">Average churned client had <b>{avg_hc:.0f}</b> covered employees in <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    if not filtered_term.empty and "headcount" in filtered_term.columns:
        fig_box = px.box(
            filtered_term, 
            y="headcount", 
            points="all", 
            color_discrete_sequence=["#60a5fa"],
            labels={"headcount": "Employee Headcount Distribution"}
        )
        fig_box.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown('<div class="chart-container"><div class="chart-header">📋 Account Size Distribution Table</div>', unsafe_allow_html=True)
    table_sizing_df = filtered_term[["client_name", "headcount", "broker", "reason"]].rename(columns={
        "client_name": "Client Name",
        "headcount": "Headcount",
        "broker": "Broker",
        "reason": "Reason"
    })
    st.dataframe(table_sizing_df, use_container_width=True, hide_index=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 9D. SUB-SCREEN: CHURN REASONS BREAKDOWN
# =========================================================
elif st.session_state["current_page"] == "Term_Reasons_Detail":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Terminations"):
            st.session_state["current_page"] = "Terminations"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">🏷️ Termination & Churn Reasons Breakdown</h1><div class="dashboard-subtitle">Detailed root cause analysis across all churned client accounts in <b>{selected_year}</b></div></div>', unsafe_allow_html=True)

    if not filtered_term.empty and "reason" in filtered_term.columns:
        reason_summary = filtered_term.groupby("reason").agg(
            total_accounts=("client_name", "count"),
            lost_headcount=("headcount", "sum")
        ).reset_index().sort_values(by="total_accounts", ascending=False)

        r_c1, r_c2 = st.columns([5, 5])
        with r_c1:
            fig_rpie = px.pie(reason_summary, names="reason", values="total_accounts", hole=0.45, color_discrete_sequence=px.colors.sequential.Reds_r)
            fig_rpie.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340)
            st.plotly_chart(fig_rpie, use_container_width=True)
        with r_c2:
            fig_rbar = px.bar(reason_summary, x="reason", y="lost_headcount", color="lost_headcount", color_continuous_scale="Reds", labels={"reason": "Reason", "lost_headcount": "Lost Headcount"})
            fig_rbar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340)
            st.plotly_chart(fig_rbar, use_container_width=True)

        st.markdown('<div class="chart-container"><div class="chart-header">📊 Churn Reason Summary Matrix</div>', unsafe_allow_html=True)
        reason_summary_display = reason_summary.rename(columns={
            "reason": "Reason",
            "total_accounts": "Total Accounts",
            "lost_headcount": "Lost Headcount"
        })
        st.dataframe(reason_summary_display, use_container_width=True, hide_index=True, height=280)
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 10. SCREEN 6: DEDICATED LUMBER BENEFITS SCREEN
# ==========================================
elif st.session_state["current_page"] == "Lumber_Benefits":
    top_col1, top_col2 = st.columns([2, 8])
    with top_col1:
        if st.button("← Back to Overview"):
            st.session_state["current_page"] = "Overview"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">🌲 Lumber Benefits & Flores Services Detailed Screen</h1><div class="dashboard-subtitle">COBRA, FSA, HSA, Direct Billing service initiation and Flores system setup tracking</div></div>', unsafe_allow_html=True)

    total_lum_clients = len(filtered_lumber)
    completed_lum = len(filtered_lumber[filtered_lumber["status"].astype(str).str.lower() == "completed"]) if "status" in filtered_lumber.columns else 0
    cobra_services = len(filtered_lumber[filtered_lumber["flores_services"].astype(str).str.contains("COBRA", na=False)]) if "flores_services" in filtered_lumber.columns else 0

    if "lum_service_selection" not in st.session_state:
        st.session_state["lum_service_selection"] = None

    lb1, lb2, lb3 = st.columns(3)
    with lb1:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(168, 85, 247, 0.4);"><div class="kpi-label">Total Lumber Clients</div><div class="kpi-value">{total_lum_clients:,}</div><div class="kpi-pill pill-purple">Tracked Accounts</div></div>', unsafe_allow_html=True)
        if st.button("🌲 All Lumber Clients →", key="btn_lum_all"):
            st.session_state["current_page"] = "Lum_All_Clients"
            st.rerun()

    with lb2:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(34, 197, 94, 0.4);"><div class="kpi-label">Completed Setups</div><div class="kpi-value">{completed_lum:,}</div><div class="kpi-pill pill-green">Initiation Done</div></div>', unsafe_allow_html=True)
        if st.button("✅ Completed Setups →", key="btn_lum_completed"):
            st.session_state["current_page"] = "Lum_Completed"
            st.rerun()

    with lb3:
        st.markdown(f'<div class="kpi-card" style="border-color: rgba(245, 158, 11, 0.4);"><div class="kpi-label">COBRA Admin Active</div><div class="kpi-value">{cobra_services:,}</div><div class="kpi-pill pill-green">Active Service</div></div>', unsafe_allow_html=True)
        if st.button("🛡️ COBRA Services →", key="btn_lum_cobra"):
            st.session_state["current_page"] = "Lum_Cobra_Services"
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    lum_c1, lum_c2 = st.columns([5, 5])
    with lum_c1:
        st.markdown('<div class="chart-container"><div class="chart-header">📊 Flores Services Breakdown</div><div style="color: #94a3b8; font-size: 13px; margin-bottom: 10px;"><i>Click on any donut slice to view matching clients.</i></div>', unsafe_allow_html=True)
        if not filtered_lumber.empty and "flores_services" in filtered_lumber.columns:
            service_counts = filtered_lumber["flores_services"].value_counts().reset_index()
            service_counts.columns = ["Service Type", "Count"]

            fig_serv = go.Figure(data=[go.Pie(
                labels=service_counts["Service Type"],
                values=service_counts["Count"],
                hole=0.45,
                marker=dict(colors=px.colors.sequential.Purples_r)
            )])
            fig_serv.update_traces(
                hovertemplate="<b>%{label}</b><br>Count: <b>%{value}</b> (%{percent})<extra></extra>"
            )
            fig_serv.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                clickmode="event+select",
                margin=dict(t=10, b=10, l=10, r=10)
            )
            serv_selection = st.plotly_chart(
                fig_serv,
                use_container_width=True,
                on_select="rerun",
                selection_mode="points",
                key="lum_services_donut_chart"
            )

            if serv_selection and "selection" in serv_selection and serv_selection["selection"]["points"]:
                point = serv_selection["selection"]["points"][0]
                if "pointIndex" in point:
                    idx = point["pointIndex"]
                    st.session_state["lum_service_selection"] = service_counts.iloc[idx]["Service Type"]

        st.markdown('</div>', unsafe_allow_html=True)

    with lum_c2:
        st.markdown('<div class="chart-container"><div class="chart-header">⚙️ System Setup Milestones</div>', unsafe_allow_html=True)
        if not filtered_lumber.empty:
            milestones = {
                "Service Request": (filtered_lumber["service_initiation_request"].astype(str).str.lower() == "true").sum() if "service_initiation_request" in filtered_lumber.columns else 0,
                "SOW / MSA": (filtered_lumber["statement_of_workmaster_services_agreement"].astype(str).str.lower() == "true").sum() if "statement_of_workmaster_services_agreement" in filtered_lumber.columns else 0,
                "System Initiation": (filtered_lumber["flores_system_initiation"].astype(str).str.lower() == "true").sum() if "flores_system_initiation" in filtered_lumber.columns else 0,
                "EDI Active": (filtered_lumber["edi_status"].astype(str).str.lower() == "true").sum() if "edi_status" in filtered_lumber.columns else 0,
            }
            m_df = pd.DataFrame(list(milestones.items()), columns=["Milestone", "Completed"])
            fig_m = px.bar(m_df, x="Milestone", y="Completed", color="Completed", color_continuous_scale="Purples")
            fig_m.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(t=10, b=10))
            st.plotly_chart(fig_m, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["lum_service_selection"]:
        selected_service_type = st.session_state["lum_service_selection"]
        
        c_head1, c_head2 = st.columns([8, 2])
        with c_head1:
            st.markdown(
                f'<div class="kpi-card" style="margin-top: 15px; margin-bottom: 20px; border-color: rgba(168, 85, 247, 0.6); '
                f'display: flex; justify-content: space-between; align-items: center; padding: 16px 24px;">'
                f'<div><span class="kpi-label">Selected Service Type</span>'
                f'<div style="font-size: 22px; font-weight: 800; color: #c084fc;">{selected_service_type}</div></div>'
                f'<div style="text-align: right;"><span class="kpi-label">Client Count</span>'
                f'<div style="font-size: 26px; font-weight: 800; color: #ffffff;">{len(filtered_lumber[filtered_lumber["flores_services"].astype(str).str.strip().str.lower() == str(selected_service_type).strip().lower()]):,} <span style="font-size: 14px; font-weight: 500; color: #94a3b8;">clients</span></div></div></div>',
                unsafe_allow_html=True
            )
        with c_head2:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            if st.button("✖ Clear Selection"):
                st.session_state["lum_service_selection"] = None
                st.rerun()

        matched_service_df = filtered_lumber[
            filtered_lumber["flores_services"].astype(str).str.strip().str.lower() == str(selected_service_type).strip().lower()
        ].copy()

        st.markdown(f'<div class="chart-container"><div class="chart-header">📋 Clients with Service: {selected_service_type}</div>', unsafe_allow_html=True)
        lumber_cols = [c for c in matched_service_df.columns if c.lower() != "edi_status"]
        lum_service_display = matched_service_df[lumber_cols].rename(columns={c: format_col_header(c) for c in lumber_cols})
        st.dataframe(lum_service_display, use_container_width=True, hide_index=True, height=320)
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 10A. SUB-SCREEN: ALL LUMBER CLIENTS LOG
# =========================================================
elif st.session_state["current_page"] == "Lum_All_Clients":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Lumber Benefits"):
            st.session_state["current_page"] = "Lumber_Benefits"
            st.rerun()

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">🌲 All Lumber Benefits Clients - Master Log</h1><div class="dashboard-subtitle">Master records of all {len(filtered_lumber)} clients enrolled in Flores Benefits administration</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container"><div class="chart-header">📋 Complete Lumber Clients Master Table</div>', unsafe_allow_html=True)
    
    lumber_cols = [c for c in filtered_lumber.columns if c.lower() != "edi_status"]
    lum_all_display = filtered_lumber[lumber_cols].rename(columns={c: format_col_header(c) for c in lumber_cols})
    
    st.dataframe(lum_all_display, use_container_width=True, hide_index=True, height=450)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 10B. SUB-SCREEN: COMPLETED SETUPS DRILLDOWN
# =========================================================
elif st.session_state["current_page"] == "Lum_Completed":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Lumber Benefits"):
            st.session_state["current_page"] = "Lumber_Benefits"
            st.rerun()

    completed_lum_df = filtered_lumber[filtered_lumber["status"].astype(str).str.lower() == "completed"]

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">✅ Completed Flores Benefits Setups</h1><div class="dashboard-subtitle">Full details on {len(completed_lum_df)} accounts with fully completed service initiation</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container"><div class="chart-header">📋 Completed Accounts Records</div>', unsafe_allow_html=True)
    
    lumber_cols = [c for c in completed_lum_df.columns if c.lower() != "edi_status"]
    lum_comp_display = completed_lum_df[lumber_cols].rename(columns={c: format_col_header(c) for c in lumber_cols})
    
    st.dataframe(lum_comp_display, use_container_width=True, hide_index=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 10C. SUB-SCREEN: EDI ACTIVE DRILLDOWN
# =========================================================
elif st.session_state["current_page"] == "Lum_EDI_Active":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Lumber Benefits"):
            st.session_state["current_page"] = "Lumber_Benefits"
            st.rerun()

    edi_df = filtered_lumber[filtered_lumber["edi_status"].astype(str).str.lower() == "true"]

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">🔄 Active Automated EDI Feeds</h1><div class="dashboard-subtitle">Active carrier and payroll EDI automated pipelines for {len(edi_df)} client accounts</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container"><div class="chart-header">📋 Active EDI Pipeline Accounts</div>', unsafe_allow_html=True)
    
    lumber_cols = [c for c in edi_df.columns if c.lower() != "edi_status"]
    lum_edi_display = edi_df[lumber_cols].rename(columns={c: format_col_header(c) for c in lumber_cols})
    
    st.dataframe(lum_edi_display, use_container_width=True, hide_index=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 10D. SUB-SCREEN: COBRA & MULTI-BENEFIT ADMIN
# =========================================================
elif st.session_state["current_page"] == "Lum_Cobra_Services":
    b1, b2 = st.columns([2.5, 7.5])
    with b1:
        if st.button("← Back to Lumber Benefits"):
            st.session_state["current_page"] = "Lumber_Benefits"
            st.rerun()

    cobra_df = filtered_lumber[filtered_lumber["flores_services"].astype(str).str.contains("COBRA", na=False)]

    st.markdown(f'<div class="dashboard-header" style="margin-top: 10px;"><h1 class="dashboard-title">🛡️ COBRA Administration & Multi-Benefit Services</h1><div class="dashboard-subtitle">Detailed tracking of {len(cobra_df)} accounts with active COBRA, FSA, and HSA benefits administration</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container"><div class="chart-header">📋 COBRA Active Client Accounts</div>', unsafe_allow_html=True)
    
    lumber_cols = [c for c in cobra_df.columns if c.lower() != "edi_status"]
    lum_cobra_display = cobra_df[lumber_cols].rename(columns={c: format_col_header(c) for c in lumber_cols})
    
    st.dataframe(lum_cobra_display, use_container_width=True, hide_index=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)