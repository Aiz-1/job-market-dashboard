"""
app.py — Job Market & Salary Analytics Dashboard
A production-ready Streamlit web app for exploring global job market trends.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, apply_filters, get_key_metrics, get_insights

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Market Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS — Minimal Light Theme ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: #f9f9f9;
        color: #1a1a1a;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e5e5;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #aaaaaa;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #1a1a1a;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 12px;
        color: #cccccc;
        margin-top: 4px;
    }

    .section-header {
        font-size: 15px;
        font-weight: 600;
        color: #333333;
        margin-bottom: 4px;
        padding-bottom: 8px;
        border-bottom: 1px solid #e8e8e8;
    }

    .insight-card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .insight-title {
        font-size: 11px;
        font-weight: 600;
        color: #aaaaaa;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }
    .insight-body {
        font-size: 14px;
        color: #333333;
        line-height: 1.7;
    }

    hr {
        border: none;
        border-top: 1px solid #e8e8e8;
        margin: 24px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Plotly Theme ─────────────────────────────────────────────────────────────
PAPER_BG   = "#ffffff"
PLOT_BG    = "#ffffff"
GRID_COLOR = "#f0f0f0"
BAR_COLOR  = "#4a4a4a"
PIE_COLORS = ["#4a4a4a", "#c0c0c0", "#888888"]


def style_figure(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family="Inter", color="#555555", size=12),
        margin=dict(t=40, b=30, l=10, r=10),
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
                   linecolor="#e8e8e8", tickfont=dict(color="#888888")),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
                   linecolor="#e8e8e8", tickfont=dict(color="#888888")),
        title_font=dict(size=14, color="#333333", family="Inter"),
        legend=dict(bgcolor="#ffffff", bordercolor="#e8e8e8"),
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
    <div style='padding: 12px 0 20px;'>
        <div style='font-size:15px; font-weight:700; color:#1a1a1a;'>Job Market Analytics</div>
        <div style='font-size:12px; color:#aaaaaa; margin-top:2px;'>Filter the dataset below</div>
    </div>
    <hr style='border-color:#e8e8e8; margin:0 0 16px;'>
    """, unsafe_allow_html=True)

    all_titles   = sorted(df_raw["Job_Title"].unique())
    sel_titles   = st.multiselect("Job Title", all_titles, placeholder="All titles")

    all_countries = sorted(df_raw["Country"].unique())
    sel_countries = st.multiselect("Country", all_countries, placeholder="All countries")

    all_exp = sorted(df_raw["Experience_Level"].unique(),
                     key=lambda x: {"Junior": 1, "Mid": 2, "Senior": 3}.get(x, 4))
    sel_exp = st.multiselect("Experience Level", all_exp, placeholder="All levels")

    all_types  = sorted(df_raw["Company_Type"].unique())
    sel_types  = st.multiselect("Company Type", all_types, placeholder="All types")

    all_remote = sorted(df_raw["Remote"].unique())
    sel_remote = st.multiselect("Remote", all_remote, placeholder="All")

    st.markdown("<hr style='border-color:#e8e8e8;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:12px; color:#aaaaaa;'>{len(df_raw)} total records</div>",
                unsafe_allow_html=True)

# ─── Apply Filters ────────────────────────────────────────────────────────────
df = apply_filters(
    df_raw,
    job_titles=sel_titles or None,
    countries=sel_countries or None,
    experience_levels=sel_exp or None,
    company_types=sel_types or None,
    remote_options=sel_remote or None,
)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 4px 0 24px;'>
    <h1 style='font-size:26px; font-weight:700; color:#1a1a1a; margin:0;'>
        Job Market & Salary Analytics
    </h1>
    <p style='font-size:14px; color:#aaaaaa; margin-top:6px; margin-bottom:0;'>
        Global hiring trends, compensation benchmarks, and in-demand skills
    </p>
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards ────────────────────────────────────────────────────────────────
metrics = get_key_metrics(df)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Total Jobs</div>
        <div class='metric-value'>{metrics['total_jobs']:,}</div>
        <div class='metric-sub'>filtered results</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Avg Salary</div>
        <div class='metric-value'>${metrics['avg_salary']:,.0f}</div>
        <div class='metric-sub'>USD per year</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Highest Paying Role</div>
        <div class='metric-value' style='font-size:17px; padding-top:4px;'>{metrics['highest_paying_job']}</div>
        <div class='metric-sub'>by average salary</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Top Skill</div>
        <div class='metric-value' style='font-size:20px; padding-top:4px;'>{metrics['most_common_skill']}</div>
        <div class='metric-sub'>most in demand</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

# ─── Charts Row 1 ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Salary Analysis</div>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    if not df.empty:
        avg_by_title = (
            df.groupby("Job_Title")["Salary_USD"]
            .mean().sort_values(ascending=True).reset_index()
        )
        avg_by_title.columns = ["Job Title", "Average Salary (USD)"]
        fig1 = px.bar(avg_by_title, x="Average Salary (USD)", y="Job Title",
                      orientation="h", title="Avg Salary by Job Title")
        fig1.update_traces(marker_color=BAR_COLOR, marker_line_width=0)
        fig1 = style_figure(fig1)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No data matches the selected filters.")

with col_b:
    if not df.empty:
        avg_by_country = (
            df.groupby("Country")["Salary_USD"]
            .mean().sort_values(ascending=False).head(12).reset_index()
        )
        avg_by_country.columns = ["Country", "Average Salary (USD)"]
        fig2 = px.bar(avg_by_country, x="Country", y="Average Salary (USD)",
                      title="Avg Salary by Country (Top 12)")
        fig2.update_traces(marker_color=BAR_COLOR, marker_line_width=0)
        fig2 = style_figure(fig2)
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

# ─── Charts Row 2 ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Workforce & Skills</div>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

col_c, col_d, col_e = st.columns(3)

with col_c:
    if not df.empty:
        remote_counts = df["Remote"].value_counts().reset_index()
        remote_counts.columns = ["Remote", "Count"]
        fig3 = px.pie(remote_counts, names="Remote", values="Count",
                      title="Remote vs Onsite",
                      color_discrete_sequence=PIE_COLORS, hole=0.45)
        fig3 = style_figure(fig3)
        fig3.update_traces(textfont_color="#333333", textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

with col_d:
    if not df.empty:
        skill_counts = df["Top_Skill"].value_counts().head(10).reset_index()
        skill_counts.columns = ["Skill", "Count"]
        fig4 = px.bar(skill_counts, x="Count", y="Skill", orientation="h",
                      title="Top 10 In-Demand Skills")
        fig4.update_traces(marker_color=BAR_COLOR, marker_line_width=0)
        fig4 = style_figure(fig4)
        st.plotly_chart(fig4, use_container_width=True)

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
                      title="Salary by Experience Level")
        fig5.update_traces(marker_color=BAR_COLOR, marker_line_width=0)
        fig5 = style_figure(fig5)
        fig5.update_layout(showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Insights ─────────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Market Insights</div>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

insights = get_insights(df)

if insights:
    ins1, ins2, ins3 = st.columns(3)

    with ins1:
        top_roles = insights.get("top_paying_roles", pd.Series())
        roles_text = "<br>".join(
            [f"<b>{role}</b> &mdash; ${sal:,.0f}" for role, sal in top_roles.items()]
        )
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>Top Paying Job Roles</div>
            <div class='insight-body'>{roles_text}</div>
        </div>""", unsafe_allow_html=True)

    with ins2:
        top_skills_data = insights.get("top_skills", pd.Series())
        skills_text = "<br>".join(
            [f"<b>{skill}</b> &mdash; {count} listings" for skill, count in top_skills_data.items()]
        )
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>Most In-Demand Skills</div>
            <div class='insight-body'>{skills_text}</div>
        </div>""", unsafe_allow_html=True)

    with ins3:
        top_country_data = insights.get("top_country", pd.Series())
        country_name = top_country_data.index[0] if not top_country_data.empty else "N/A"
        country_sal  = top_country_data.iloc[0]  if not top_country_data.empty else 0
        remote_pct   = insights.get("remote_pct", 0)
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-title'>Geographic Insights</div>
            <div class='insight-body'>
                <b>Highest avg salary:</b> {country_name} (${country_sal:,.0f})<br><br>
                <b>{remote_pct}%</b> of filtered roles offer remote work
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.warning("No data available for insights. Adjust your filters.")

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Data Table ───────────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Filtered Dataset</div>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

display_cols = ["Year", "Job_Title", "Country", "Company_Type",
                "Experience_Level", "Salary_USD", "Remote", "Top_Skill"]
show_cols = [c for c in display_cols if c in df.columns]

if not df.empty:
    st.dataframe(
        df[show_cols].sort_values("Salary_USD", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=360,
    )
    csv_data = df[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_jobs.csv",
        mime="text/csv",
    )
else:
    st.warning("No records match the selected filters. Please adjust your selections.")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style='text-align:center; padding: 12px 0; font-size:12px; color:#cccccc;'>
    Job Market Analytics · Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)