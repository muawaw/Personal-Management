import streamlit as st
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.inventory import get_all_inventory, get_inventory_by_id
from backend.master_data import get_all_materials, get_all_locations


def render():
    st.title("Inventory Stock Monitor")
    st.caption("Read-only stock levels. Inventory updates automatically via Purchasing and Sales transactions.")

    material_options = get_all_materials()
    location_options = get_all_locations()

    material_lookup = {m["material_id"]: m["material_name"] for m in material_options}
    location_lookup = {l["location_id"]: l["location_name"] for l in location_options}

    # Search & Filter controls
    with st.expander("Filter Inventory", expanded=False):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            selected_material = st.selectbox(
                "Filter by Material",
                ["All Materials"] + [m["material_name"] for m in material_options],
            )
        with f_col2:
            selected_location = st.selectbox(
                "Filter by Location",
                ["All Locations"] + [l["location_name"] for l in location_options],
            )

    st.markdown("---")
    st.subheader("Current Stock Levels")

    try:
        inventory_items = get_all_inventory()
        if not inventory_items:
            st.info("No inventory records found.")
            return

        # Apply filtering
        filtered_items = inventory_items
        if selected_material != "All Materials":
            mat_id = next(m["material_id"] for m in material_options if m["material_name"] == selected_material)
            filtered_items = [item for item in filtered_items if item["material_id"] == mat_id]

        if selected_location != "All Locations":
            loc_id = next(l["location_id"] for l in location_options if l["location_name"] == selected_location)
            filtered_items = [item for item in filtered_items if item["location_id"] == loc_id]

        if not filtered_items:
            st.warning("No inventory items match the selected filter criteria.")
            return

        display_inventory_table(filtered_items, material_lookup, location_lookup)

    except Exception as exc:
        st.error(f"Could not fetch inventory records: {exc}")


def display_inventory_table(inventory_items, material_lookup, location_lookup):
    headers = ["ID", "Material", "Location", "Stock Qty", "Actions"]
    cols = st.columns([0.8, 2.5, 2.0, 1.5, 1.2])
    for col, label in zip(cols, headers):
        col.markdown(f"**{label}**")

    st.markdown(
        """
        <style>
        .compact-action-row button {
            min-width: 4.0rem !important;
            max-width: 6rem !important;
            padding: 0.18rem 0.45rem !important;
            font-size: 0.55rem !important;
            white-space: nowrap !important;
        }
        .compact-action-row .stButton {
            margin: 0.25rem 0.06rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    for row in inventory_items:
        cols = st.columns([0.8, 2.5, 2.0, 1.5, 1.2])
        cols[0].write(row["inventory_id"])
        cols[1].write(material_lookup.get(row["material_id"], row["material_id"]))
        cols[2].write(location_lookup.get(row["location_id"], row["location_id"]))

        try:
            qty = float(row["stock_qty"])
            cols[3].write(f"{qty:,.2f}" if qty % 1 != 0 else f"{int(qty):,}")
        except Exception:
            cols[3].write(row["stock_qty"])

        st.markdown('<div class="compact-action-row">', unsafe_allow_html=True)
        if cols[4].button("View", key=f"view_inventory_{row['inventory_id']}", help="View Details"):
            st.session_state.inventory_action = (row["inventory_id"], "view")
        st.markdown('</div>', unsafe_allow_html=True)

    if "inventory_action" in st.session_state:
        inventory_id, action = st.session_state.inventory_action
        details = get_inventory_by_id(inventory_id)
        if details:
            st.markdown("---")
            if action == "view":
                st.subheader(f"View Inventory Item #{inventory_id}")
                st.json(details)