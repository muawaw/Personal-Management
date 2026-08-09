import streamlit as st
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.dashboard import (
    DASHBOARD_FILTER_PRESETS,
    get_dashboard_data,
    get_dashboard_data_paginated,
    get_dashboard_date_filter_range,
    get_dashboard_summary,
)
from frontend.operational_menu import purchase_input, sales_input

st.set_page_config(page_title="Kasir Dashboard", page_icon="📊", layout="wide")

st.title("Kasir")
st.caption("Minimal operations workspace")

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.6rem 0.4rem 0.8rem 0.4rem; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 0.6rem;">
            <div style="font-size: 0.95rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: #8ba3ff;">Navigation</div>
            <div style="font-size: 1.05rem; font-weight: 600; margin-top: 0.2rem;">Kasir Menu</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    if st.button("Dashboard", use_container_width=True, key="nav_dashboard"):
        st.session_state.page = "dashboard"

    with st.expander("Operational Management", expanded=False):
        if st.button("Purchase Input", use_container_width=True, key="nav_purchase"):
            st.session_state.page = "purchase"
        if st.button("Sales Input", use_container_width=True, key="nav_sales"):
            st.session_state.page = "sales"

    with st.expander("Inventory Management", expanded=False):
        if st.button("Inventory Input", use_container_width=True, key="nav_inventory"):
            st.session_state.page = "inventory"
        if st.button("Stock Opname", use_container_width=True, key="nav_stock"):
            st.session_state.page = "stock_opname"

    with st.expander("Configuration", expanded=False):
        if st.button("Master Data", use_container_width=True, key="nav_master"):
            st.session_state.page = "master_data"

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

page = st.session_state.page

if page == "dashboard":
    st.subheader("Dashboard")

    if "dashboard_filters" not in st.session_state:
        st.session_state.dashboard_filters = {
            "preset": "current_month",
            "start_date": None,
            "end_date": None,
        }

    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            preset = st.selectbox(
                "Date range",
                DASHBOARD_FILTER_PRESETS,
                index=DASHBOARD_FILTER_PRESETS.index(st.session_state.dashboard_filters["preset"]),
            )
        with col2:
            start_date = st.date_input(
                "Start date",
                value=st.session_state.dashboard_filters["start_date"] or date.today(),
                format="YYYY-MM-DD",
            )
        with col3:
            end_date = st.date_input(
                "End date",
                value=st.session_state.dashboard_filters["end_date"] or date.today(),
                format="YYYY-MM-DD",
            )

        st.session_state.dashboard_filters = {
            "preset": preset,
            "start_date": start_date,
            "end_date": end_date,
        }

        st.markdown(
            "<link rel=\"stylesheet\" href=\"styles.css\">",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="dashboard-action-row">', unsafe_allow_html=True)
        button_cols = st.columns([1, 0.22, 0.18])
        with button_cols[1]:
            if st.button("Refresh Dashboard", key="refresh_dashboard_btn", use_container_width=True):
                st.session_state.dashboard_filters = {
                    "preset": preset,
                    "start_date": start_date,
                    "end_date": end_date,
                }
                st.rerun()
        with button_cols[2]:
            if st.button("Apply Filters", key="apply_dashboard_filters_btn", use_container_width=True):
                st.session_state.dashboard_filters = {
                    "preset": preset,
                    "start_date": start_date,
                    "end_date": end_date,
                }
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        if preset != "all_time":
            range_params = get_dashboard_date_filter_range(preset)
            if not start_date:
                start_date = range_params.get("start_date") or ""
            if not end_date:
                end_date = range_params.get("end_date") or ""

        st.caption("Use a preset or choose custom dates and apply the filter.")

    applied_start = st.session_state.dashboard_filters["start_date"]
    applied_end = st.session_state.dashboard_filters["end_date"]

    try:
        summary = get_dashboard_summary(
            start_date=applied_start.isoformat() if applied_start else None,
            end_date=applied_end.isoformat() if applied_end else None,
        )
    except Exception as exc:
        st.error(f"Could not load summary: {exc}")
        summary = {}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Purchased Qty", f"{summary.get('total_purchased_qty', 0):,.0f}")
    c2.metric("Sales Qty", f"{summary.get('total_sold_qty', 0):,.0f}")
    c3.metric("Purchased Amount", f"Rp {summary.get('total_purchased_amount', 0):,.0f}")
    c4.metric("Sales Amount", f"Rp {summary.get('total_sales_amount', 0):,.0f}")

    try:
        rows = get_dashboard_data(
            start_date=applied_start.isoformat() if applied_start else None,
            end_date=applied_end.isoformat() if applied_end else None,
        )
    except Exception as exc:
        st.error(f"Could not load dashboard data: {exc}")
        rows = []

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No data found for the selected range.")

elif page == "purchase":
    purchase_input.render()
elif page == "sales":
    sales_input.render()
elif page == "inventory":
    st.subheader("Inventory Input")
    st.info("Inventory form will be added here next.")
elif page == "stock_opname":
    st.subheader("Stock Opname")
    st.info("Stock opname form will be added here next.")
else:
    st.subheader("Master Data")
    st.info("Master data configuration will be added here next.")
