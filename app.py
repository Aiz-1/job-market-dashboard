"""
app.py — AI Job Market Trend Analysis Dashboard
Production-ready Streamlit app with vibrant, professional UI.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, apply_filters, get_key_metrics, get_insights

st.set_page_config(
    page_title="AI Job Market Trend Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

/* Page background */
.stApp { background: #F0F4FF; color: #1a1a2e; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1a1a2e;
    border-right: none;
}
section[data-testid="stSidebar"] * { color: #e0e6ff !important; }
section[data-testid="stSidebar"] .stMultiSelect > label,
section[data-testid="stSidebar"] label { color: #a0aec0 !important; font-size: 12px !important; }

/* Logo / brand in sidebar */
.sidebar-logo {
    background: linear-gradient(135deg, #6C63FF, #4ECDC4);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
    text-align: center;
}
.sidebar-logo-icon { font-size: 32px; margin-bottom: 4px; }
.sidebar-logo-title { font-size: 15px; font-weight: 800; color: #ffffff !important; letter-spacing: 0.5px; }
.sidebar-logo-sub { font-size: 10px; color: rgba(255,255,255,0.7) !important; letter-spacing: 1.5px; text-transform: uppercase; }

/* Page header banner */
.page-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.banner-icon { font-size: 48px; }
.banner-title { font-size: 28px; font-weight: 800; color: #ffffff; margin: 0; line-height: 1.2; }
.banner-sub { font-size: 14px; color: #a0b4d6; margin-top: 6px; }
.banner-badge {
    background: linear-gradient(135deg, #6C63FF, #4ECDC4);
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-block;
    margin-top: 8px;
    letter-spacing: 0.5px;
}

/* KPI Cards */
.kpi-card {
    border-radius: 14px;
    padding: 22px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: -20px; right: -20px;
    width: 80px; height: 80px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
}
.kpi-card-1 { background: linear-gradient(135deg, #6C63FF, #9B59B6); }
.kpi-card-2 { background: linear-gradient(135deg, #11998e, #38ef7d); }
.kpi-card-3 { background: linear-gradient(135deg, #f093fb, #f5576c); }
.kpi-card-4 { background: linear-gradient(135deg, #4facfe, #00f2fe); }

.kpi-icon { font-size: 22px; margin-bottom: 6px; }
.kpi-label { font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: rgba(255,255,255,0.75); margin-bottom: 6px; }
.kpi-value { font-size: 28px; font-weight: 800; color: #ffffff; line-height: 1.1; }
.kpi-sub { font-size: 12px; color: rgba(255,255,255,0.6); margin-top: 4px; }

/* Section headers */
.section-header {
    font-size: 17px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 4px;
    padding-bottom: 10px;
    border-bottom: 2px solid #6C63FF;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Chart wrapper */
.chart-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 8px;
    box-shadow: 0 2px 12px rgba(108,99,255,0.07);
}

/* Insight cards */
.insight-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(108,99,255,0.07);
    border-left: 4px solid #6C63FF;
    margin-bottom: 4px;
}
.insight-card-green { border-left-color: #11998e; }
.insight-card-pink  { border-left-color: #f5576c; }

.insight-title { font-size: 11px; font-weight: 700; color: #6C63FF; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
.insight-title-green { color: #11998e; }
.insight-title-pink  { color: #f5576c; }
.insight-body { font-size: 14px; color: #444466; line-height: 1.8; }

hr { border: none; border-top: 1px solid #dde4f0; margin: 28px 0; }
</style>
""", unsafe_allow_html=True)

# ─── Plotly theme ──────────────────────────────────────────────────────────────
PAPER_BG   = "#ffffff"
PLOT_BG    = "#ffffff"
GRID_COLOR = "#f0f2fa"

# Vibrant color palettes
SALARY_COLORS  = ["#6C63FF", "#9B59B6", "#4ECDC4", "#11998e", "#f093fb",
                  "#f5576c", "#4facfe", "#43e97b", "#fa709a", "#fee140",
                  "#a18cd1", "#fbc2eb"]
SKILL_COLORS   = ["#6C63FF", "#4ECDC4", "#f5576c", "#11998e", "#f093fb",
                  "#4facfe", "#fa709a", "#fee140", "#43e97b", "#a18cd1"]
EXP_COLORS     = {"Junior": "#4ECDC4", "Mid": "#6C63FF", "Senior": "#f5576c"}
PIE_COLORS     = ["#6C63FF", "#4ECDC4", "#f093fb"]


def style_figure(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family="Inter", color="#444466", size=12),
        margin=dict(t=44, b=20, l=10, r=10),
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
                   linecolor="#e8ecf8", tickfont=dict(color="#888aaa", size=11)),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
                   linecolor="#e8ecf8", tickfont=dict(color="#888aaa", size=11)),
        title_font=dict(size=14, color="#1a1a2e", family="Inter"),
        legend=dict(bgcolor="#ffffff", bordercolor="#e8ecf8", font=dict(size=11)),
    )
    return fig


# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data()

df_raw = get_data()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🤖</div>
        <div class="sidebar-logo-title">AI Job Market</div>
        <div class="sidebar-logo-sub">Trend Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:12px; color:#a0aec0; font-weight:600; letter-spacing:1px; text-transform:uppercase; margin-bottom:12px;'>🔎 Filters</p>", unsafe_allow_html=True)

    all_titles = sorted(df_raw["Job_Title"].unique())
    sel_titles = st.multiselect("Job Title", all_titles, placeholder="All titles")

    all_countries = sorted(df_raw["Country"].unique())
    sel_countries = st.multiselect("Country", all_countries, placeholder="All countries")

    all_exp = sorted(df_raw["Experience_Level"].unique(),
                     key=lambda x: {"Junior": 1, "Mid": 2, "Senior": 3}.get(x, 4))
    sel_exp = st.multiselect("Experience Level", all_exp, placeholder="All levels")

    all_types = sorted(df_raw["Company_Type"].unique())
    sel_types = st.multiselect("Company Type", all_types, placeholder="All types")

    all_remote = sorted(df_raw["Remote"].unique())
    sel_remote = st.multiselect("Remote", all_remote, placeholder="All")

    st.markdown(f"<hr style='border-color:#2d2d4e; margin:16px 0;'><p style='font-size:12px; color:#606080; text-align:center;'>{len(df_raw)} total records</p>", unsafe_allow_html=True)

# ─── Apply Filters ────────────────────────────────────────────────────────────
df = apply_filters(df_raw,
    job_titles=sel_titles or None, countries=sel_countries or None,
    experience_levels=sel_exp or None, company_types=sel_types or None,
    remote_options=sel_remote or None)

# ─── Page Banner ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-banner">
    <div class="banner-icon">🤖</div>
    <div>
        <div class="banner-title">AI Job Market Trend Analysis</div>
        <div class="banner-sub">Explore salary benchmarks, in-demand skills, and global hiring trends</div>
        <div class="banner-badge">✦ Live Analytics Dashboard</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards ────────────────────────────────────────────────────────────────
metrics = get_key_metrics(df)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="kpi-card kpi-card-1">
        <div class="kpi-icon">💼</div>
        <div class="kpi-label">Total Jobs</div>
        <div class="kpi-value">{metrics['total_jobs']:,}</div>
        <div class="kpi-sub">filtered results</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="kpi-card kpi-card-2">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Avg Salary</div>
        <div class="kpi-value">${metrics['avg_salary']:,.0f}</div>
        <div class="kpi-sub">USD per year</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="kpi-card kpi-card-3">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-label">Top Paying Role</div>
        <div class="kpi-value" style="font-size:16px; padding-top:4px;">{metrics['highest_paying_job']}</div>
        <div class="kpi-sub">by average salary</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="kpi-card kpi-card-4">
        <div class="kpi-icon">🛠️</div>
        <div class="kpi-label">Top Skill</div>
        <div class="kpi-value" style="font-size:20px; padding-top:4px;">{metrics['most_common_skill']}</div>
        <div class="kpi-sub">most in demand</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)

# ─── Charts Row 1: Salary ─────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📊 Salary Analysis</div>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    if not df.empty:
        avg_by_title = (df.groupby("Job_Title")["Salary_USD"]
            .mean().sort_values(ascending=True).reset_index())
        avg_by_title.columns = ["Job Title", "Average Salary (USD)"]
        fig1 = px.bar(avg_by_title, x="Average Salary (USD)", y="Job Title",
                      orientation="h", title="Avg Salary by Job Title",
                      color="Job Title", color_discrete_sequence=SALARY_COLORS)
        fig1.update_traces(marker_line_width=0)
        fig1.update_layout(showlegend=False)
        fig1 = style_figure(fig1)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No data matches the selected filters.")

with col_b:
    if not df.empty:
        avg_by_country = (df.groupby("Country")["Salary_USD"]
            .mean().sort_values(ascending=False).head(12).reset_index())
        avg_by_country.columns = ["Country", "Average Salary (USD)"]
        fig2 = px.bar(avg_by_country, x="Country", y="Average Salary (USD)",
                      title="Avg Salary by Country (Top 12)",
                      color="Country", color_discrete_sequence=SALARY_COLORS)
        fig2.update_traces(marker_line_width=0)
        fig2.update_layout(showlegend=False)
        fig2 = style_figure(fig2)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

# ─── Charts Row 2: Skills & Workforce ─────────────────────────────────────────
st.markdown("<div class='section-header'>🧠 Workforce & Skills</div>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

col_c, col_d, col_e = st.columns(3)

with col_c:
    if not df.empty:
        remote_counts = df["Remote"].value_counts().reset_index()
        remote_counts.columns = ["Remote", "Count"]
        fig3 = px.pie(remote_counts, names="Remote", values="Count",
                      title="Remote vs Onsite",
                      color_discrete_sequence=PIE_COLORS, hole=0.42)
        fig3 = style_figure(fig3)
        fig3.update_traces(textfont_size=13, textposition="outside",
                           pull=[0.03, 0])
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with col_d:
    if not df.empty:
        skill_counts = df["Top_Skill"].value_counts().head(10).reset_index()
        skill_counts.columns = ["Skill", "Count"]
        fig4 = px.bar(skill_counts, x="Count", y="Skill", orientation="h",
                      title="Top 10 In-Demand Skills",
                      color="Skill", color_discrete_sequence=SKILL_COLORS)
        fig4.update_traces(marker_line_width=0)
        fig4.update_layout(showlegend=False)
        fig4 = style_figure(fig4)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with col_e:
    if not df.empty:
        exp_order = ["Junior", "Mid", "Senior"]
        exp_data = (
            df[df["Experience_Level"].isin(exp_order)]
            .groupby("Experience_Level")["Salary_USD"]
            .mean().reindex(exp_order).dropna().reset_index()
        )
        exp_data.columns = ["Experience Level", "Average Salary (USD)"]
        fig5 = px.bar(exp_data, x="Experience Level", y="Average Salary (USD)",
                      title="Salary by Experience Level",
                      color="Experience Level",
                      color_discrete_map=EXP_COLORS)
        fig5.update_traces(marker_line_width=0)
        fig5.update_layout(showlegend=False)
        fig5 = style_figure(fig5)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Insights ─────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📌 Market Insights</div>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

insights = get_insights(df)
if insights:
    ins1, ins2, ins3 = st.columns(3)

    with ins1:
        top_roles = insights.get("top_paying_roles", pd.Series())
        roles_text = "<br>".join(
            [f"<b style='color:#1a1a2e;'>{role}</b> &mdash; <span style='color:#6C63FF;'>${sal:,.0f}</span>"
             for role, sal in top_roles.items()])
        st.markdown(f"""<div class='insight-card'>
            <div class='insight-title'>💰 Top Paying Job Roles</div>
            <div class='insight-body'>{roles_text}</div>
        </div>""", unsafe_allow_html=True)

    with ins2:
        top_skills_data = insights.get("top_skills", pd.Series())
        skills_text = "<br>".join(
            [f"<b style='color:#1a1a2e;'>{skill}</b> &mdash; <span style='color:#11998e;'>{count} listings</span>"
             for skill, count in top_skills_data.items()])
        st.markdown(f"""<div class='insight-card insight-card-green'>
            <div class='insight-title insight-title-green'>🛠️ Most In-Demand Skills</div>
            <div class='insight-body'>{skills_text}</div>
        </div>""", unsafe_allow_html=True)

    with ins3:
        top_country_data = insights.get("top_country", pd.Series())
        country_name = top_country_data.index[0] if not top_country_data.empty else "N/A"
        country_sal  = top_country_data.iloc[0]  if not top_country_data.empty else 0
        remote_pct   = insights.get("remote_pct", 0)
        st.markdown(f"""<div class='insight-card insight-card-pink'>
            <div class='insight-title insight-title-pink'>🌍 Geographic Insights</div>
            <div class='insight-body'>
                <b style='color:#1a1a2e;'>Highest avg salary:</b><br>
                <span style='color:#f5576c; font-size:16px; font-weight:700;'>{country_name}</span>
                &mdash; ${country_sal:,.0f}<br><br>
                <b style='color:#1a1a2e;'>{remote_pct}%</b> of roles offer remote work
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.warning("No data available for insights. Adjust your filters.")

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Data Table ───────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>📋 Filtered Dataset</div>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

display_cols = ["Year", "Job_Title", "Country", "Company_Type",
                "Experience_Level", "Salary_USD", "Remote", "Top_Skill"]
show_cols = [c for c in display_cols if c in df.columns]

if not df.empty:
    st.dataframe(
        df[show_cols].sort_values("Salary_USD", ascending=False).reset_index(drop=True),
        use_container_width=True, height=360)
    csv_data = df[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Filtered Data as CSV", csv_data,
                       "filtered_jobs.csv", "text/csv")
else:
    st.warning("No records match the selected filters.")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style='text-align:center; padding:12px 0; font-size:12px; color:#aaaacc;'>
    🤖 AI Job Market Trend Analysis &nbsp;·&nbsp; Built with Streamlit & Plotly &nbsp;·&nbsp; Portfolio Project
</div>""", unsafe_allow_html=True)