"""
utils.py — Data loading and preprocessing utilities
Job Market & Salary Analytics Dashboard
"""

import pandas as pd
import numpy as np
import os


DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "jobs.csv")


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Load and clean the jobs dataset.
    - Fills missing categorical values with 'Unknown'
    - Ensures correct dtypes
    Returns a clean DataFrame.
    """
    df = pd.read_csv(path)

    # Fill missing categorical columns
    categorical_cols = ["Job_Title", "Country", "Company_Type", "Experience_Level", "Remote", "Top_Skill"]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    # Fill missing numeric columns
    if "Salary_USD" in df.columns:
        df["Salary_USD"] = pd.to_numeric(df["Salary_USD"], errors="coerce")
        df["Salary_USD"] = df["Salary_USD"].fillna(df["Salary_USD"].median())

    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0).astype(int)

    # Standardize Remote column
    df["Remote"] = df["Remote"].str.capitalize()

    # Standardize Experience Level ordering
    exp_order = {"Junior": 1, "Mid": 2, "Senior": 3, "Unknown": 4}
    df["_exp_order"] = df["Experience_Level"].map(exp_order).fillna(4)

    return df


def apply_filters(df: pd.DataFrame, job_titles=None, countries=None,
                  experience_levels=None, company_types=None, remote_options=None) -> pd.DataFrame:
    """Apply sidebar filters to the dataframe."""
    filtered = df.copy()

    if job_titles:
        filtered = filtered[filtered["Job_Title"].isin(job_titles)]
    if countries:
        filtered = filtered[filtered["Country"].isin(countries)]
    if experience_levels:
        filtered = filtered[filtered["Experience_Level"].isin(experience_levels)]
    if company_types:
        filtered = filtered[filtered["Company_Type"].isin(company_types)]
    if remote_options:
        filtered = filtered[filtered["Remote"].isin(remote_options)]

    return filtered


def get_key_metrics(df: pd.DataFrame) -> dict:
    """Compute top-level KPI metrics from filtered dataframe."""
    if df.empty:
        return {
            "total_jobs": 0,
            "avg_salary": 0,
            "highest_paying_job": "N/A",
            "most_common_skill": "N/A",
        }

    avg_salary_by_title = df.groupby("Job_Title")["Salary_USD"].mean()
    skill_counts = df["Top_Skill"].value_counts()

    return {
        "total_jobs": len(df),
        "avg_salary": round(df["Salary_USD"].mean(), 0),
        "highest_paying_job": avg_salary_by_title.idxmax() if not avg_salary_by_title.empty else "N/A",
        "most_common_skill": skill_counts.idxmax() if not skill_counts.empty else "N/A",
    }


def get_insights(df: pd.DataFrame) -> dict:
    """Generate textual insight strings for the Insights section."""
    if df.empty:
        return {}

    top_paying = (
        df.groupby("Job_Title")["Salary_USD"]
        .mean()
        .sort_values(ascending=False)
        .head(3)
    )

    top_skills = df["Top_Skill"].value_counts().head(3)

    top_country = (
        df.groupby("Country")["Salary_USD"]
        .mean()
        .sort_values(ascending=False)
        .head(1)
    )

    remote_pct = round((df["Remote"] == "Yes").mean() * 100, 1)

    return {
        "top_paying_roles": top_paying,
        "top_skills": top_skills,
        "top_country": top_country,
        "remote_pct": remote_pct,
    }