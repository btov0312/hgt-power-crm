import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Kyntronics Pipeline", layout="wide")
st.title("🚀 Kyntronics SHA West Coast - Interactive Pipeline Dashboard")
st.markdown("**Real-time Pipeline • Hybrid Electro-Hydraulic Actuators**")

# ====================== LOAD / INIT DATA ======================
DATA_FILE = "kyntronics_leads.csv"

if not os.path.exists(DATA_FILE):
    # Same high-quality 24 leads as before
    data = { ... }  # (truncated for brevity - same as previous version)
    df = pd.DataFrame(data)
    df.to_csv(DATA_FILE, index=False)
else:
    df = pd.read_csv(DATA_FILE)

# Ensure required columns
required_cols = ["Pipeline_Stage", "Est_Value", "Last_Contact"]
for col in required_cols:
    if col not in df.columns:
        df[col] = "" if col == "Last_Contact" else 0

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("🔍 Filters")
search = st.sidebar.text_input("Search Company/Contact")
state_filter = st.sidebar.multiselect("State", sorted(df["State"].dropna().unique()), default=[])
stage_filter = st.sidebar.multiselect("Stage", sorted(df["Pipeline_Stage"].unique()), default=[])

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[filtered_df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
if state_filter:
    filtered_df = filtered_df[filtered_df["State"].isin(state_filter)]
if stage_filter:
    filtered_df = filtered_df[filtered_df["Pipeline_Stage"].isin(stage_filter)]

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Interactive Dashboard", "🗂️ Kanban Board", "📋 All Leads", "➕ Add / Export"])

# ==================== TAB 1: INTERACTIVE DASHBOARD ====================
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pipeline", f"${filtered_df['Est_Value'].sum():,}")
    with col2:
        st.metric("Active Leads", len(filtered_df))
    with col3:
        won = filtered_df[filtered_df["Pipeline_Stage"] == "Closed-Won"]["Est_Value"].sum()
        st.metric("Closed-Won Value", f"${won:,}")
    with col4:
        avg_value = filtered_df["Est_Value"].mean()
        st.metric("Avg Deal Size", f"${avg_value:,.0f}")

    # Interactive Charts
    st.subheader("Pipeline Visuals")
    c1, c2 = st.columns(2)
    with c1:
        stage_summary = filtered_df.groupby("Pipeline_Stage").agg(
            Count=("Company", "count"), Total_Value=("Est_Value", "sum")
        ).reset_index()
        fig_bar = px.bar(stage_summary, x="Pipeline_Stage", y="Total_Value", 
                         title="Pipeline Value by Stage", color="Total_Value",
                         color_continuous_scale="Blues")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with c2:
        fig_pie = px.pie(stage_summary, names="Pipeline_Stage", values="Count", 
                         title="Lead Distribution by Stage")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Funnel Chart (Classic Sales Funnel)
    stages_order = ["Prospect", "Needs Demo", "Quote Sent", "Negotiation", "Closed-Won", "Lost"]
    funnel_data = filtered_df.groupby("Pipeline_Stage")["Est_Value"].sum().reindex(stages_order).reset_index()
    fig_funnel = px.funnel(funnel_data, x="Est_Value", y="Pipeline_Stage", 
                           title="Sales Funnel (Value Flow)")
    st.plotly_chart(fig_funnel, use_container_width=True)

# ==================== TAB 2: KANBAN BOARD ====================
with tab2:
    st.subheader("Kanban Pipeline Board")
    stages = ["Prospect", "Needs Demo", "Quote Sent", "Negotiation", "Closed-Won", "Lost"]
    cols = st.columns(len(stages))
    
    for idx, stage in enumerate(stages):
        with cols[idx]:
            st.markdown(f"**{stage}**")
            stage_leads = filtered_df[filtered_df["Pipeline_Stage"] == stage]
            for i, row in stage_leads.iterrows():
                with st.expander(f"{row['Company']} (${row['Est_Value']:,.0f})"):
                    st.write(f"**Contact:** {row['Contact']}")
                    st.write(f"**State:** {row['State']} | **Industry:** {row['Industry']}")
                    if st.button("Move →", key=f"move_{i}_{stage}"):
                        new_stage = st.selectbox("New Stage", [s for s in stages if s != stage], key=f"select_{i}")
                        if new_stage:
                            df.loc[df["Company"] == row["Company"], "Pipeline_Stage"] = new_stage
                            df.loc[df["Company"] == row["Company"], "Last_Contact"] = datetime.now().strftime("%Y-%m-%d")
                            df.to_csv(DATA_FILE, index=False)
                            st.rerun()

# ==================== TAB 3: EDITABLE LEADS ====================
with tab3:
    st.subheader("Editable Leads Table")
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Pipeline_Stage": st.column_config.SelectboxColumn("Stage", options=stages),
            "Est_Value": st.column_config.NumberColumn("Est. Value $", min_value=0),
            "Last_Contact": st.column_config.DateColumn("Last Contact")
        }
    )
    if st.button("💾 Save Changes"):
        df.update(edited_df)
        df.to_csv(DATA_FILE, index=False)
        st.success("Changes saved!")

# ==================== TAB 4: ADD / EXPORT ====================
with tab4:
    with st.form("add_lead"):
        st.subheader("Add New Lead")
        c1, c2 = st.columns(2)
        with c1:
            company = st.text_input("Company*")
            contact = st.text_input("Contact")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        with c2:
            state = st.selectbox("State", ["CA","WA","OR","AZ","UT","NV","ID","CO"])
            industry = st.text_input("Industry")
            application = st.text_input("Application")
            value = st.number_input("Est. Value $", value=35000)
            stage = st.selectbox("Stage", stages)
        notes = st.text_area("Notes")
        if st.form_submit_button("Add Lead"):
            new_row = pd.DataFrame([{"Company": company, "Contact": contact, "Email": email, "Phone": phone,
                                     "State": state, "Industry": industry, "Application": application,
                                     "Pipeline_Stage": stage, "Est_Value": value, "Last_Contact": datetime.now().strftime("%Y-%m-%d"),
                                     "Notes": notes}])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Lead added!")

    st.download_button("Export Full Pipeline (CSV)", df.to_csv(index=False).encode(), "kyntronics_westcoast_pipeline.csv")

st.caption("Interactive Kyntronics CRM v2 • All data saved locally • Ready for West Coast sales")
