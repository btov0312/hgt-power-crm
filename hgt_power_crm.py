import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="HGT Power LLC CRM", layout="wide")
st.title("🚀 HGT Power LLC - Kyntronics West Coast CRM")
st.markdown("**Sales Pipeline + Recruiting Dashboard** | SHA Hybrid Actuators")

# ====================== LOAD FILES ======================
SALES_FILE = "kyntronics_westcoast_leads_full.xlsx"
RECRUIT_FILE = "HGT_Power_Recruiting_Application_Engineers.xlsx"

sales_df = pd.read_excel(SALES_FILE) if os.path.exists(SALES_FILE) else pd.DataFrame()
recruit_df = pd.read_excel(RECRUIT_FILE) if os.path.exists(RECRUIT_FILE) else pd.DataFrame()

st.sidebar.success(f"Sales Leads: {len(sales_df)} | Recruiting Candidates: {len(recruit_df)}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Sales Dashboard", "🗂️ Sales Kanban", "📋 Sales Leads",
    "👥 Recruiting Dashboard", "➕ Add / Export"
])

# ====================== SALES TABS ======================
with tab1:
    st.subheader("Sales Pipeline Overview")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Pipeline Value", f"${sales_df.get('Est_Value', pd.Series(0)).sum():,}")
    with col2: st.metric("Active Leads", len(sales_df))
    with col3: st.metric("Avg Deal Size", f"${sales_df.get('Est_Value', pd.Series(0)).mean():,.0f}")

    stage_summary = sales_df.groupby("Pipeline_Stage")["Est_Value"].sum().reset_index()
    st.plotly_chart(px.bar(stage_summary, x="Pipeline_Stage", y="Est_Value", title="Value by Stage"), use_container_width=True)

with tab2:
    st.subheader("Sales Kanban Board")
    stages = ["Prospect", "Needs Demo", "Quote Sent", "Negotiation", "Closed-Won", "Lost"]
    cols = st.columns(len(stages))
    for idx, stage in enumerate(stages):
        with cols[idx]:
            st.markdown(f"**{stage}**")
            stage_leads = sales_df[sales_df["Pipeline_Stage"] == stage]
            for _, row in stage_leads.iterrows():
                with st.expander(f"{row['Company']} (${row['Est_Value']:,.0f})"):
                    st.write(row.get('Contact', ''))
                    if st.button("Move", key=f"move_{row['Company']}"):
                        new_stage = st.selectbox("New Stage", [s for s in stages if s != stage], key=f"sel_{row['Company']}")
                        if st.button("Confirm", key=f"conf_{row['Company']}"):
                            sales_df.loc[sales_df["Company"] == row["Company"], "Pipeline_Stage"] = new_stage
                            sales_df.to_excel(SALES_FILE, index=False)
                            st.rerun()

with tab3:
    st.subheader("Editable Sales Leads")
    edited_sales = st.data_editor(sales_df, use_container_width=True)
    if st.button("💾 Save Sales Changes"):
        edited_sales.to_excel(SALES_FILE, index=False)
        st.success("Sales data saved!")

# ====================== RECRUITING DASHBOARD ======================
with tab4:
    st.subheader("👥 Recruiting Dashboard")
    if len(recruit_df) == 0:
        st.error("Recruiting file not found!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect("Status", options=recruit_df.get("Status", ["Prospect"]).unique())
        with col2:
            company_filter = st.multiselect("Company", options=recruit_df["Company"].unique())

        filtered = recruit_df.copy()
        if status_filter: filtered = filtered[filtered.get("Status").isin(status_filter)]
        if company_filter: filtered = filtered[filtered["Company"].isin(company_filter)]

        r1, r2, r3, r4 = st.columns(4)
        with r1: st.metric("Total Candidates", len(filtered))
        with r2: st.metric("Contacted", len(filtered[filtered.get("Status") == "Contacted"]))
        with r3: st.metric("Interviews", len(filtered[filtered.get("Status") == "Interview"]))
        with r4: st.metric("Offers Sent", len(filtered[filtered.get("Status") == "Offer Sent"]))

        st.data_editor(filtered, use_container_width=True, key="recruit_editor")
        if st.button("💾 Save Recruiting Changes"):
            filtered.to_excel(RECRUIT_FILE, index=False)
            st.success("Recruiting data saved!")

# ====================== ADD / EXPORT ======================
with tab5:
    st.subheader("Add New Record")
    add_type = st.radio("Type", ["Sales Lead", "Recruiting Candidate"])
    # Simple form logic can be expanded here
    st.download_button("Download Sales Excel", data=open(SALES_FILE, "rb").read(), file_name=SALES_FILE)
    st.download_button("Download Recruiting Excel", data=open(RECRUIT_FILE, "rb").read(), file_name=RECRUIT_FILE)

st.caption("HGT Power LLC CRM • Built for Kyntronics SHA Sales")
