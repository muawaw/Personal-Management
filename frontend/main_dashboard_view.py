import sys
from datetime import date
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.dashboard import (
    DASHBOARD_FILTER_PRESETS,
    get_dashboard_data,
    get_dashboard_date_filter_range,
    get_dashboard_summary,
)
from backend.master_data import (
    get_all_categories,
    get_all_locations,
    get_all_materials,
)
from constant.error_handling import handle_ui_exception
from frontend import master_data_input
from frontend.inventory_menu import inventory_input, stock_opname
from frontend.operational_menu import purchase_input, sales_input

PRESET_LABELS = {
    "current_month": "Current Month",
    "previous_month": "Previous Month",
    "last_3_months": "Last 3 Months",
    "last_6_months": "Last 6 Months",
    "last_year": "Last Year",
    "all_time": "All Time",
    "custom": "Custom Range",
}

INITIAL_FILTER_STATE = {
    "preset": "current_month",
    "start_date": None,
    "end_date": None,
    "category_id": None,
    "material_id": None,
    "location_id": None,
}


def reset_dashboard_filters():
    """Callback function to safely reset widget states before rerun."""
    st.session_state.f_preset = "current_month"
    st.session_state.f_start_date = date.today()
    st.session_state.f_end_date = date.today()
    st.session_state.f_cat = "All Categories"
    st.session_state.f_mat = "All Materials"
    st.session_state.f_loc = "All Locations"
    st.session_state.dashboard_filters = dict(INITIAL_FILTER_STATE)


def render_dashboard_page():
    st.title("Personal Use Management System")
    st.caption("Manage personal sales, purchases, and inventory")
    st.subheader("Dashboard")

    # Fetch filter dropdown options
    try:
        categories = get_all_categories() or []
        materials = get_all_materials() or []
        locations = get_all_locations() or []
    except Exception as exc:
        st.error(handle_ui_exception(exc))
        categories, materials, locations = [], [], []

    cat_options = {c["category_name"]: c["category_id"] for c in categories}
    mat_options = {m["material_name"]: m["material_id"] for m in materials}
    loc_options = {l["location_name"]: l["location_id"] for l in locations}

    # Applied filter query state
    if "dashboard_filters" not in st.session_state:
        st.session_state.dashboard_filters = dict(INITIAL_FILTER_STATE)

    # Initialize widget session states
    if "f_preset" not in st.session_state:
        st.session_state.f_preset = "current_month"
        st.session_state.f_start_date = date.today()
        st.session_state.f_end_date = date.today()
        st.session_state.f_cat = "All Categories"
        st.session_state.f_mat = "All Materials"
        st.session_state.f_loc = "All Locations"

    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            st.selectbox(
                "Date range",
                DASHBOARD_FILTER_PRESETS + ["custom"],
                key="f_preset",
                format_func=lambda x: PRESET_LABELS.get(
                    x, x.replace("_", " ").title()
                ),
            )

        preset_range = (
            get_dashboard_date_filter_range(st.session_state.f_preset)
            if st.session_state.f_preset not in ("all_time", "custom")
            else {}
        )
        default_start = preset_range.get("start_date") or date.today()
        default_end = preset_range.get("end_date") or date.today()

        with col2:
            st.date_input(
                "Start date",
                value=(
                    default_start
                    if st.session_state.f_preset != "custom"
                    else st.session_state.f_start_date
                ),
                key="f_start_date",
                format="YYYY-MM-DD",
            )
        with col3:
            st.date_input(
                "End date",
                value=(
                    default_end
                    if st.session_state.f_preset != "custom"
                    else st.session_state.f_end_date
                ),
                key="f_end_date",
                format="YYYY-MM-DD",
            )

        # Entity Filters Row
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            st.selectbox(
                "Category",
                ["All Categories"] + list(cat_options.keys()),
                key="f_cat",
            )
        with f_col2:
            st.selectbox(
                "Material",
                ["All Materials"] + list(mat_options.keys()),
                key="f_mat",
            )
        with f_col3:
            st.selectbox(
                "Location",
                ["All Locations"] + list(loc_options.keys()),
                key="f_loc",
            )

        st.markdown(
            '<link rel="stylesheet" href="styles.css">',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="dashboard-action-row">', unsafe_allow_html=True
        )
        button_cols = st.columns([1, 0.22, 0.18])

        with button_cols[1]:
            # Use on_click callback to execute state reset safely
            st.button(
                "Refresh Dashboard",
                key="refresh_dashboard_btn",
                use_container_width=True,
                on_click=reset_dashboard_filters,
            )

        with button_cols[2]:
            if st.button(
                "Apply Filters",
                key="apply_dashboard_filters_btn",
                use_container_width=True,
            ):
                st.session_state.dashboard_filters = {
                    "preset": st.session_state.f_preset,
                    "start_date": (
                        st.session_state.f_start_date
                        if st.session_state.f_preset == "custom"
                        else None
                    ),
                    "end_date": (
                        st.session_state.f_end_date
                        if st.session_state.f_preset == "custom"
                        else None
                    ),
                    "category_id": cat_options.get(st.session_state.f_cat),
                    "material_id": mat_options.get(st.session_state.f_mat),
                    "location_id": loc_options.get(st.session_state.f_loc),
                }
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.caption(
            "Use a preset or choose custom dates and entities, then apply the"
            " filter."
        )

    # Determine date query parameters
    active_preset = st.session_state.dashboard_filters["preset"]
    if active_preset == "all_time":
        query_start, query_end = None, None
    elif active_preset == "custom":
        query_start = st.session_state.dashboard_filters["start_date"]
        query_end = st.session_state.dashboard_filters["end_date"]
    else:
        resolved_range = get_dashboard_date_filter_range(active_preset)
        query_start = resolved_range.get("start_date")
        query_end = resolved_range.get("end_date")

    start_str = (
        query_start.isoformat()
        if hasattr(query_start, "isoformat")
        else query_start
    )
    end_str = (
        query_end.isoformat()
        if hasattr(query_end, "isoformat")
        else query_end
    )

    cat_id = st.session_state.dashboard_filters.get("category_id")
    mat_id = st.session_state.dashboard_filters.get("material_id")
    loc_id = st.session_state.dashboard_filters.get("location_id")

    # Fetch Metrics
    try:
        summary = (
            get_dashboard_summary(
                start_date=start_str,
                end_date=end_str,
                category_id=cat_id,
                material_id=mat_id,
                location_id=loc_id,
            )
            or {}
        )
    except Exception as exc:
        st.error(handle_ui_exception(exc))
        summary = {}

    # Metric Row 1: Volume & Revenue/Spend
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Purchased Qty", f"{summary.get('total_purchased_qty', 0) or 0:,.0f}"
    )
    c2.metric("Sales Qty", f"{summary.get('total_sold_qty', 0) or 0:,.0f}")
    c3.metric(
        "Purchased Amount",
        f"Rp {summary.get('total_purchased_amount', 0) or 0:,.0f}",
    )
    c4.metric(
        "Sales Amount", f"Rp {summary.get('total_sales_amount', 0) or 0:,.0f}"
    )

    # Metric Row 2: Profit/Loss and Inventory Status
    m1, m2 = st.columns(2)

    sales_amt = float(summary.get("total_sales_amount", 0) or 0)
    purchased_amt = float(summary.get("total_purchased_amount", 0) or 0)
    profit_loss = sales_amt - purchased_amt

    m1.metric(
        label="Profit / Loss",
        value=f"Rp {profit_loss:,.0f}",
        delta=f"Rp {profit_loss:,.0f}",
        delta_color="normal",
    )
    m2.metric(
        label="Total Inventory Qty",
        value=f"{summary.get('total_inventory_qty', 0) or 0:,.0f}",
    )

    st.markdown("---")

    # Fetch Table Records
    try:
        rows = (
            get_dashboard_data(
                start_date=start_str,
                end_date=end_str,
                category_id=cat_id,
                material_id=mat_id,
                location_id=loc_id,
            )
            or []
        )
    except Exception as exc:
        st.error(handle_ui_exception(exc))
        rows = []

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No data found for the selected range.")


def render_master_data_page():
    master_data_input.render()


# Native Streamlit navigation page targets
dashboard_page = st.Page(
    render_dashboard_page,
    title="Dashboard",
    default=True,
    url_path="dashboard",
)
purchase_page = st.Page(
    purchase_input.render,
    title="Purchase Input",
    url_path="purchase",
)
sales_page = st.Page(
    sales_input.render,
    title="Sales Input",
    url_path="sales",
)
inventory_page = st.Page(
    inventory_input.render,
    title="Inventory Monitoring",
    url_path="inventory",
)
stock_opname_page = st.Page(
    stock_opname.render,
    title="Stock Opname",
    url_path="stock-opname",
)
master_data_page = st.Page(
    render_master_data_page,
    title="Master Data",
    url_path="master-data",
)