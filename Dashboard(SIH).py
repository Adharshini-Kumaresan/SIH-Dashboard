import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np

# Page config
st.set_page_config(page_title="SIH 2024 Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("d:/AI_BootCamp/Dashboards/SIH_PS_Winners_2024.csv")
    # Rename columns for consistency with code
    df = df.rename(columns={
        "ID": "Problem Statement ID",
        "Title": "Problem Statement Title",
        "Category": "Category",
        "Technology_Bucket": "Technology Bucket",
        "Organisation": "Organisation Name",
        "MINISTRY/GOVT DEPT/ORGANISATION": "Ministry/Department",
        "TEAM NAME": "Winning Team Name",
        "WINNING STATUS": "Winning Status",
        "NODAL CENTER": "Nodal Center",
        "INSTITUTE": "Institute Name"
    })
    return df

df = load_data()

# Title
st.title("📊 SIH 2024 – From Problem Statements to Winning Solutions")

# Sidebar filters
st.sidebar.title("Filters")
selected_category = st.sidebar.multiselect("Category", df["Category"].unique())
selected_tech = st.sidebar.multiselect("Technology Bucket", df["Technology Bucket"].unique())
selected_org = st.sidebar.multiselect("Organisation Name", df["Organisation Name"].unique())
selected_ministry = st.sidebar.multiselect("Ministry/Department", df["Ministry/Department"].unique())

# Filter application
def filter_data(df):
    if selected_category:
        df = df[df["Category"].isin(selected_category)]
    if selected_tech:
        df = df[df["Technology Bucket"].isin(selected_tech)]
    if selected_org:
        df = df[df["Organisation Name"].isin(selected_org)]
    if selected_ministry:
        df = df[df["Ministry/Department"].isin(selected_ministry)]
    return df

filtered_df = filter_data(df)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", 
    "Problem Statement Analysis",
    "Organisation & Ministry Insights",
    "Nodal Center Performance",
    "Winning Team Insights"
])

# Tab 1: Overview
with tab1:
    # KPI Cards row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Problem Statements", len(filtered_df["Problem Statement ID"].unique()))
    with col2:
        st.metric("Total Winners", len(filtered_df["Winning Team Name"].unique()))
    with col3:
        st.metric("Unique Organisations", len(filtered_df["Organisation Name"].unique()))
    with col4:
        st.metric("Unique Technology Buckets", len(filtered_df["Technology Bucket"].unique()))

    # Category Distribution
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(filtered_df, names="Category", title="Category Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(filtered_df["Winning Status"].value_counts(), 
                    title="Winning Status Distribution",
                    labels={"value": "Count", "index": "Status"})
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Problem Statement Analysis
with tab2:
    # Top 10 Technology Buckets
    tech_counts = filtered_df["Technology Bucket"].value_counts().head(10)
    fig = px.bar(tech_counts, orientation="h", 
                 title="Top 10 Technology Buckets",
                 labels={"value": "Count", "index": "Technology Bucket"})
    st.plotly_chart(fig, use_container_width=True)

    # Treemap (fix: drop rows with empty Category or Technology Bucket)
    treemap_df = filtered_df.dropna(subset=["Category", "Technology Bucket"])
    treemap_df = treemap_df[
        (treemap_df["Category"].astype(str).str.strip() != "") &
        (treemap_df["Technology Bucket"].astype(str).str.strip() != "")
    ]
    if not treemap_df.empty:
        fig = px.treemap(
            treemap_df, 
            path=["Category", "Technology Bucket"],
            title="Category & Technology Bucket Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for treemap.")

    # Word Cloud
    if st.checkbox("Show Problem Statement Word Cloud"):
        text = " ".join(filtered_df["Problem Statement Title"].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
        
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

# Tab 3: Organisation & Ministry Insights
with tab3:
    # Top Organizations
    org_counts = filtered_df["Organisation Name"].value_counts().head(10)
    fig = px.bar(org_counts, 
                 title="Top 10 Organizations by Problem Statements",
                 labels={"value": "Count", "index": "Organisation Name"})
    st.plotly_chart(fig, use_container_width=True)

    # Ministry vs Winning Status
    ministry_wins = pd.crosstab(filtered_df["Ministry/Department"], 
                               filtered_df["Winning Status"])
    fig = px.bar(ministry_wins, 
                 title="Ministry/Department by Winning Status",
                 barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Nodal Center Performance
with tab4:
    # Nodal Center Winners
    nodal_wins = filtered_df[filtered_df["Winning Status"] == "Winner"]["Nodal Center"].value_counts()
    fig = px.bar(nodal_wins.head(10), 
                 title="Top 10 Nodal Centers by Winners",
                 labels={"value": "Number of Winners", "index": "Nodal Center"})
    st.plotly_chart(fig, use_container_width=True)

# Tab 5: Winning Team Insights
with tab5:
    # Top Winning Institutes
    institute_wins = filtered_df[filtered_df["Winning Status"] == "Winner"]["Institute Name"].value_counts()
    fig = px.bar(institute_wins.head(10), 
                 title="Top 10 Institutes by Winners",
                 labels={"value": "Number of Winners", "index": "Institute Name"})
    st.plotly_chart(fig, use_container_width=True)

    # Winners Table
    st.subheader("Winners Details")
    winner_cols = ["Winning Team Name", "Institute Name", "Category", 
                  "Technology Bucket", "Organisation Name"]
    st.dataframe(filtered_df[filtered_df["Winning Status"] == "Winner"][winner_cols],
                use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Dashboard created for SIH 2024 Dataset Analysis")