"""
app.py — AI Job Market Trend Analysis Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, apply_filters, get_key_metrics, get_insights

st.set_page_config(
    page_title="AI Job Market Trend Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

.stApp { background: #F0F4FF; color: #1a1a2e; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #1a1a2e; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label { color: #c8d0e8 !important; }
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
    background: #252542 !important;
}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: #6C63FF !important;
}

.sidebar-brand {
    background: linear-gradient(135deg, #6C63FF 0%, #4ECDC4 100%);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 20px;
}
.sidebar-brand-title { font-size: 14px; font-weight: 800; color: #fff !important; margin: 0; }
.sidebar-brand-sub   { font-size: 10px; color: rgba(255,255,255,0.75) !important; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px; }

/* ── Page Banner ── */
.page-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    border-radius: 14px;
    padding: 26px 32px;
    margin-bottom: 28px;
}
.banner-title { font-size: 26px; font-weight: 800; color: #ffffff; margin: 0; }
.banner-sub   { font-size: 13px; color: #a0b4d6; margin-top: 6px; }
.banner-badge {
    display: inline-block;
    background: linear-gradient(135deg, #6C63FF, #4ECDC4);
    color: #fff;
    font-size: 10px; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
    margin-top: 10px; letter-spacing: 0.8px;
}

/* ── KPI Cards ── */
.kpi-card { border-radius: 12px; padding: 20px 16px; text-align: center; }
.kpi-label { font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: rgba(255,255,255,0.7); margin-bottom: 6px; }
.kpi-value { font-size: 26px; font-weight: 800; color: #ffffff; line-height: 1.1; }
.kpi-sub   { font-size: 11px; color: rgba(255,255,255,0.55); margin-top: 4px; }
.kpi-1 { background: linear-gradient(135deg, #6C63FF, #9B59B6); }
.kpi-2 { background: linear-gradient(135deg, #11998e, #38ef7d); }
.kpi-3 { background: linear-gradient(135deg, #f093fb, #f5576c); }
.kpi-4 { background: linear-gradient(135deg, #4facfe, #00f2fe); }

/* ── Section Header ── */
.sec-header {
    font-size: 15px; font-weight: 700; color: #1a1a2e;
    border-bottom: 2px solid #6C63FF;
    padding-bottom: 8px; margin-bottom: 16px;
}

/* ── Chart Card ── */
.chart-card { background: #fff; border-radius: 12px; padding: 4px; box-shadow: 0 2px 10px rgba(108,99,255,0.08); }

/* ── Insight Cards ── */
.insight-card {
    background: #fff; border-radius: 12px; padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(108,99,255,0.07);
    border-left: 4px solid #6C63FF;
}
.insight-card.green { border-left-color: #11998e; }
.insight-card.pink  { border-left-color: #f5576c; }
.insight-label { font-size: 10px; font-weight: 700; color: #6C63FF; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
.insight-label.green { color: #11998e; }
.insight-label.pink  { color: #f5576c; }
.insight-body  { font-size: 13px; color: #333355; line-height: 1.8; }

/* ── Job Fit Section ── */
.fit-box {
    background: #fff; border-radius: 14px;
    padding: 28px 32px;
    box-shadow: 0 2px 16px rgba(108,99,255,0.10);
}
.fit-result-good { background: #e8fdf5; border: 1.5px solid #11998e; border-radius: 10px; padding: 16px 20px; }
.fit-result-mid  { background: #fff8e1; border: 1.5px solid #f5a623; border-radius: 10px; padding: 16px 20px; }
.fit-result-low  { background: #fdecea; border: 1.5px solid #f5576c; border-radius: 10px; padding: 16px 20px; }
.fit-role { font-size: 13px; font-weight: 600; color: #1a1a2e; }
.fit-bar-wrap { background: #eef0fa; border-radius: 20px; height: 8px; margin: 6px 0 2px; }
.fit-bar { height: 8px; border-radius: 20px; }

hr { border: none; border-top: 1px solid #dde4f0; margin: 28px 0; }
</style>
""", unsafe_allow_html=True)

# ── Color palettes ──────────────────────────────────────────────────────────
COLORS_12   = ["#6C63FF","#4ECDC4","#f5576c","#11998e","#f093fb",
               "#4facfe","#fa709a","#43e97b","#fee140","#a18cd1","#fbc2eb","#667eea"]
EXP_COLORS  = {"Junior": "#4ECDC4", "Mid": "#6C63FF", "Senior": "#f5576c"}
PIE_COLORS  = ["#6C63FF", "#4ECDC4", "#f093fb"]
PAPER_BG    = "#ffffff"
PLOT_BG     = "#ffffff"
GRID_COLOR  = "#f0f2fa"

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="Inter", color="#444466", size=12),
        margin=dict(t=44, b=20, l=10, r=10),
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
                   tickfont=dict(color="#888aaa", size=11)),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
                   tickfont=dict(color="#888aaa", size=11)),
        title_font=dict(size=13, color="#1a1a2e", family="Inter"),
        legend=dict(bgcolor="#fff", bordercolor="#eee", font=dict(size=11)),
    )
    return fig

# ── Load data ───────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data()

df_raw = get_data()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">AI Job Market</div>
        <div class="sidebar-brand-sub">Trend Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:11px;color:#7080a0;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;'>Filters</p>", unsafe_allow_html=True)

    all_titles    = sorted(df_raw["Job_Title"].unique())
    sel_titles    = st.multiselect("Job Title", all_titles)

    all_countries = sorted(df_raw["Country"].unique())
    sel_countries = st.multiselect("Country", all_countries)

    all_exp = sorted(df_raw["Experience_Level"].unique(),
                     key=lambda x: {"Junior":1,"Mid":2,"Senior":3}.get(x,4))
    sel_exp   = st.multiselect("Experience Level", all_exp)

    all_types = sorted(df_raw["Company_Type"].unique())
    sel_types = st.multiselect("Company Type", all_types)

    all_remote = sorted(df_raw["Remote"].unique())
    sel_remote = st.multiselect("Remote Work", all_remote)

    st.markdown(f"<hr style='border-color:#2d2d4e;margin:16px 0;'><p style='font-size:11px;color:#505070;text-align:center;'>{len(df_raw)} total records in dataset</p>", unsafe_allow_html=True)

# ── Apply filters — empty list = no filter ──────────────────────────────────
df = apply_filters(df_raw,
    job_titles      = sel_titles    if sel_titles    else None,
    countries       = sel_countries if sel_countries else None,
    experience_levels = sel_exp     if sel_exp       else None,
    company_types   = sel_types     if sel_types     else None,
    remote_options  = sel_remote    if sel_remote    else None,
)

# ── Banner ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-banner">
    <div class="banner-title">AI Job Market Trend Analysis</div>
    <div class="banner-sub">Salary benchmarks, in-demand skills, and global hiring trends</div>
    <div class="banner-badge">Live Analytics Dashboard</div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ───────────────────────────────────────────────────────────────
metrics = get_key_metrics(df)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card kpi-1">
        <div class="kpi-label">Total Jobs</div>
        <div class="kpi-value">{metrics['total_jobs']:,}</div>
        <div class="kpi-sub">filtered results</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card kpi-2">
        <div class="kpi-label">Average Salary</div>
        <div class="kpi-value">${metrics['avg_salary']:,.0f}</div>
        <div class="kpi-sub">USD per year</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card kpi-3">
        <div class="kpi-label">Top Paying Role</div>
        <div class="kpi-value" style="font-size:15px;padding-top:5px;">{metrics['highest_paying_job']}</div>
        <div class="kpi-sub">by average salary</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card kpi-4">
        <div class="kpi-label">Most In-Demand Skill</div>
        <div class="kpi-value" style="font-size:19px;padding-top:4px;">{metrics['most_common_skill']}</div>
        <div class="kpi-sub">across all roles</div></div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)

# ── Charts Row 1 ────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>Salary Analysis</div>", unsafe_allow_html=True)
ca, cb = st.columns(2)

with ca:
    if not df.empty:
        d = (df.groupby("Job_Title")["Salary_USD"].mean()
               .sort_values(ascending=True).reset_index())
        d.columns = ["Job Title","Avg Salary (USD)"]
        fig = px.bar(d, x="Avg Salary (USD)", y="Job Title", orientation="h",
                     title="Average Salary by Job Title",
                     color="Job Title", color_discrete_sequence=COLORS_12)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        fig = style_fig(fig)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No data for current filters.")

with cb:
    if not df.empty:
        d = (df.groupby("Country")["Salary_USD"].mean()
               .sort_values(ascending=False).head(12).reset_index())
        d.columns = ["Country","Avg Salary (USD)"]
        fig = px.bar(d, x="Country", y="Avg Salary (USD)",
                     title="Average Salary by Country (Top 12)",
                     color="Country", color_discrete_sequence=COLORS_12)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        fig = style_fig(fig)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

# ── Charts Row 2 ────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>Workforce and Skills</div>", unsafe_allow_html=True)
cc, cd, ce = st.columns(3)

with cc:
    if not df.empty:
        d = df["Remote"].value_counts().reset_index()
        d.columns = ["Remote","Count"]
        fig = px.pie(d, names="Remote", values="Count", title="Remote vs Onsite",
                     color_discrete_sequence=PIE_COLORS, hole=0.42)
        fig = style_fig(fig)
        fig.update_traces(textposition="outside", textfont_size=12)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with cd:
    if not df.empty:
        d = df["Top_Skill"].value_counts().head(10).reset_index()
        d.columns = ["Skill","Count"]
        fig = px.bar(d, x="Count", y="Skill", orientation="h",
                     title="Top 10 In-Demand Skills",
                     color="Skill", color_discrete_sequence=COLORS_12)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        fig = style_fig(fig)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with ce:
    if not df.empty:
        exp_order = ["Junior","Mid","Senior"]
        d = (df[df["Experience_Level"].isin(exp_order)]
               .groupby("Experience_Level")["Salary_USD"]
               .mean().reindex(exp_order).dropna().reset_index())
        d.columns = ["Experience Level","Avg Salary (USD)"]
        fig = px.bar(d, x="Experience Level", y="Avg Salary (USD)",
                     title="Salary by Experience Level",
                     color="Experience Level", color_discrete_map=EXP_COLORS)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        fig = style_fig(fig)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Market Insights ─────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>Market Insights</div>", unsafe_allow_html=True)
insights = get_insights(df)

if insights:
    i1, i2, i3 = st.columns(3)
    with i1:
        top_roles = insights.get("top_paying_roles", pd.Series())
        body = "<br>".join([f"<b>{r}</b> &mdash; <span style='color:#6C63FF;'>${s:,.0f}</span>"
                            for r, s in top_roles.items()])
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-label'>Top Paying Roles</div>
            <div class='insight-body'>{body}</div></div>""", unsafe_allow_html=True)
    with i2:
        top_sk = insights.get("top_skills", pd.Series())
        body = "<br>".join([f"<b>{sk}</b> &mdash; <span style='color:#11998e;'>{cnt} listings</span>"
                            for sk, cnt in top_sk.items()])
        st.markdown(f"""<div class='insight-card green'>
            <div class='insight-label green'>Most In-Demand Skills</div>
            <div class='insight-body'>{body}</div></div>""", unsafe_allow_html=True)
    with i3:
        tc = insights.get("top_country", pd.Series())
        cn = tc.index[0] if not tc.empty else "N/A"
        cs = tc.iloc[0]  if not tc.empty else 0
        rp = insights.get("remote_pct", 0)
        st.markdown(f"""<div class='insight-card pink'>
            <div class='insight-label pink'>Geographic Insights</div>
            <div class='insight-body'>
                Highest avg salary: <b>{cn}</b><br>
                <span style='color:#f5576c;font-size:15px;font-weight:700;'>${cs:,.0f} / year</span><br><br>
                <b>{rp}%</b> of roles offer remote work
            </div></div>""", unsafe_allow_html=True)
else:
    st.warning("No insights available. Adjust filters.")

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# JOB FIT ANALYZER — User enters their profile, we show match %
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='sec-header'>Job Fit Analyzer</div>", unsafe_allow_html=True)
st.markdown("<p style='font-size:13px;color:#555577;margin-bottom:20px;'>Enter your profile below and we will analyze which job roles you are best suited for based on the current dataset.</p>", unsafe_allow_html=True)

st.markdown("<div class='fit-box'>", unsafe_allow_html=True)

fa, fb = st.columns(2)
with fa:
    user_skill      = st.selectbox("Your Primary Skill", sorted(df_raw["Top_Skill"].unique()))
    user_exp        = st.selectbox("Experience Level",   ["Junior", "Mid", "Senior"])
    user_remote     = st.selectbox("Work Preference",    ["Yes", "No", "Either"])
with fb:
    user_country    = st.selectbox("Target Country",     sorted(df_raw["Country"].unique()))
    user_comp_type  = st.selectbox("Preferred Company",  ["Any"] + sorted(df_raw["Company_Type"].unique()))
    user_salary_exp = st.number_input("Expected Salary (USD / year)", min_value=10000, max_value=500000,
                                      value=80000, step=5000)

analyze_btn = st.button("Analyze My Job Fit", type="primary")

if analyze_btn:
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # ── Score each job title ──────────────────────────────────────────────
    results = []
    for title in df_raw["Job_Title"].unique():
        subset = df_raw[df_raw["Job_Title"] == title]
        score  = 0
        notes  = []

        # Skill match
        skill_match = (subset["Top_Skill"] == user_skill).mean()
        score += skill_match * 35
        if skill_match > 0.5:
            notes.append(f"Strong skill match ({user_skill})")

        # Experience match
        exp_match = (subset["Experience_Level"] == user_exp).mean()
        score += exp_match * 25
        if exp_match > 0.5:
            notes.append(f"{user_exp}-level roles available")

        # Country match
        country_match = (subset["Country"] == user_country).mean()
        score += country_match * 20
        if country_match > 0:
            notes.append(f"Jobs in {user_country}")

        # Remote match
        if user_remote != "Either":
            remote_match = (subset["Remote"] == user_remote).mean()
            score += remote_match * 10
        else:
            score += 10

        # Salary match (within 20% of expected)
        avg_sal = subset["Salary_USD"].mean()
        if avg_sal > 0:
            ratio = min(user_salary_exp, avg_sal) / max(user_salary_exp, avg_sal)
            score += ratio * 10
            if ratio > 0.85:
                notes.append(f"Salary aligned (~${avg_sal:,.0f} avg)")

        # Company type match
        if user_comp_type != "Any":
            ct_match = (subset["Company_Type"] == user_comp_type).mean()
            if ct_match > 0:
                score += 5
                notes.append(f"{user_comp_type} company openings")

        results.append({
            "role":    title,
            "score":   round(min(score, 100), 1),
            "avg_sal": round(avg_sal, 0),
            "notes":   notes if notes else ["Limited matching data"],
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:6]

    st.markdown("<p style='font-size:13px;font-weight:600;color:#1a1a2e;margin-bottom:14px;'>Top matching roles for your profile:</p>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    cols_cycle = [r1, r2]
    for idx, res in enumerate(results):
        s = res["score"]
        bar_color = "#11998e" if s >= 65 else "#f5a623" if s >= 40 else "#f5576c"
        box_class = "fit-result-good" if s >= 65 else "fit-result-mid" if s >= 40 else "fit-result-low"
        notes_html = " &bull; ".join(res["notes"])
        with cols_cycle[idx % 2]:
            st.markdown(f"""
            <div class="{box_class}" style="margin-bottom:14px;">
                <div class="fit-role">{res['role']}</div>
                <div class="fit-bar-wrap"><div class="fit-bar" style="width:{s}%;background:{bar_color};"></div></div>
                <div style="display:flex;justify-content:space-between;font-size:11px;color:#666688;">
                    <span>Match: <b>{s}%</b></span>
                    <span>Avg salary: <b>${res['avg_sal']:,.0f}</b></span>
                </div>
                <div style="font-size:11px;color:#888;margin-top:6px;">{notes_html}</div>
            </div>""", unsafe_allow_html=True)

    # Summary line
    best = results[0]
    st.markdown(f"""
    <div style='background:#f0f4ff;border-radius:10px;padding:14px 18px;margin-top:8px;font-size:13px;color:#333355;'>
        Based on your profile, <b>{best['role']}</b> is your strongest fit at <b>{best['score']}%</b> match.
        Average market salary for this role is <b>${best['avg_sal']:,.0f} / year</b>.
    </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Data Table ──────────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>Filtered Dataset</div>", unsafe_allow_html=True)

cols_show = ["Year","Job_Title","Country","Company_Type","Experience_Level","Salary_USD","Remote","Top_Skill"]
cols_show = [c for c in cols_show if c in df.columns]

if not df.empty:
    st.dataframe(df[cols_show].sort_values("Salary_USD", ascending=False)
                               .reset_index(drop=True),
                 use_container_width=True, height=340)
    st.download_button("Download CSV", df[cols_show].to_csv(index=False).encode(),
                       "filtered_jobs.csv", "text/csv")
else:
    st.warning("No records match the selected filters.")

st.markdown("""
<hr>
<div style='text-align:center;font-size:11px;color:#aab;padding:10px 0;'>
    AI Job Market Trend Analysis &nbsp;·&nbsp; Built with Streamlit and Plotly
</div>""", unsafe_allow_html=True)