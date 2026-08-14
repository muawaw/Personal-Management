import streamlit as st
from pathlib import Path
import sys
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.stock_opname import (
    create_stock_opname,
    get_all_stock_opname,
    get_stock_opname_by_id,
    update_stock_opname,
    delete_stock_opname,
)
from backend.master_data import get_all_materials, get_all_locations
from backend.inventory import get_all_inventory


@st.dialog("Confirm Deletion")
def confirm_delete_stock_opname_dialog(opname_id):
    st.write(f"Are you sure you want to delete Stock Opname **ID: {opname_id}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete", type="primary", use_container_width=True):
            try:
                with st.spinner("Deleting stock opname..."):
                    delete_stock_opname(opname_id)
                st.session_state.stock_msg = ("success", "Stock opname deleted successfully.")
                if "stock_action" in st.session_state and st.session_state.stock_action[0] == opname_id:
                    del st.session_state.stock_action
                if "delete_stock_target" in st.session_state:
                    del st.session_state.delete_stock_target
                st.rerun()
            except Exception as exc:
                st.error(f"Could not delete stock opname: {exc}")
    with col2:
        if st.button("Cancel", use_container_width=True):
            if "delete_stock_target" in st.session_state:
                del st.session_state.delete_stock_target
            st.rerun()


def render():
    st.title("Stock Opname")

    # Display feedback message after rerun if present
    if "stock_msg" in st.session_state:
        msg_type, msg_text = st.session_state.pop("stock_msg")
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "error":
            st.error(msg_text)

    # Check if delete modal was triggered
    if "delete_stock_target" in st.session_state:
        target_id = st.session_state.delete_stock_target
        confirm_delete_stock_opname_dialog(target_id)

    material_options = get_all_materials()
    location_options = get_all_locations()
    inventory_options = get_all_inventory()

    material_map = {m["material_name"]: m["material_id"] for m in material_options}
    location_map = {l["location_name"]: l["location_id"] for l in location_options}
    inventory_map = {
    (i["material_id"], i["location_id"]): i["stock_qty"] 
    for i in inventory_options 
    if "material_id" in i and "location_id" in i
    }
    
    with st.expander("New Stock Opname", expanded=False):
        c_mat, c_loc = st.columns(2)
        with c_mat:
            material_name = st.selectbox(
                "Material", 
                ["Select material"] + [m["material_name"] for m in material_options],
                key="so_material_select"
            )
        with c_loc:
            location_name = st.selectbox(
                "Location", 
                ["Select location"] + [l["location_name"] for l in location_options],
                key="so_location_select"
            )

        fetched_system_qty = 0.0
        if material_name != "Select material" and location_name != "Select location":
            mat_id = material_map[material_name]
            loc_id = location_map[location_name]
            fetched_system_qty = float(inventory_map.get((mat_id, loc_id), 0.0))

        # st.divider()
        with st.form("stock_opname_input_form"):
            c1, c2 = st.columns(2)
            with c1:
                system_qty = st.number_input(
                    "System Qty", 
                    value=fetched_system_qty, 
                    disabled=True,
                    key=f"system_qty_{material_name}_{location_name}"
                )
            with c2:
                actual_qty = st.number_input("Actual Qty", min_value=0.0, value=0.0, step=1.0)
                            
            stock_opname_date = st.date_input("Stock Opname Date", value=date.today())
            notes = st.text_area("Notes", value="")

            submit_col, _ = st.columns([1, 3])
            with submit_col:
                submitted = st.form_submit_button("Submit Stock Opname")

            if submitted:
                if material_name == "Select material" or location_name == "Select location":
                    st.warning("Please complete all required fields before submitting.")
                else:
                    try:
                        difference_qty = actual_qty - system_qty
                        with st.spinner("Processing stock opname..."):
                            create_stock_opname(
                                material_id=material_map[material_name],
                                location_id=location_map[location_name],
                                system_qty=system_qty,
                                actual_qty=actual_qty,
                                difference_qty=difference_qty,
                                stock_opname_date=stock_opname_date.isoformat(),
                                notes=notes if notes else None,
                            )
                        st.session_state.stock_msg = ("success", "Stock opname saved successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not save stock opname: {exc}")

    st.markdown("---")
    st.subheader("Stock Opname Records")
    try:
        opname_records = get_all_stock_opname()
        if not opname_records:
            st.info("No stock opname records found.")
            return

        display_stock_opname_table(opname_records, material_options, location_options)
    except Exception as exc:
        st.error(f"Could not fetch stock opname records: {exc}")


def display_stock_opname_table(records, material_options, location_options):
    headers = ["ID", "Material", "Location", "System", "Actual", "Diff", "Date", "Actions"]
    cols = st.columns([0.6, 1.5, 1.2, 0.8, 0.8, 0.8, 1.2, 1.8])
    for col, label in zip(cols, headers):
        col.markdown(f"**{label}**")

    material_lookup = {m["material_id"]: m["material_name"] for m in material_options}
    location_lookup = {l["location_id"]: l["location_name"] for l in location_options}

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

    for row in records:
        cols = st.columns([0.6, 1.5, 1.2, 0.8, 0.8, 0.8, 1.2, 1.6])
        cols[0].write(row["opname_id"])
        cols[1].write(material_lookup.get(row["material_id"], row["material_id"]))
        cols[2].write(location_lookup.get(row["location_id"], row["location_id"]))
        
        cols[3].write(float(row["system_qty"]) if row.get("system_qty") is not None else 0.0)
        cols[4].write(float(row["actual_qty"]) if row.get("actual_qty") is not None else 0.0)
        cols[5].write(float(row["difference_qty"]) if row.get("difference_qty") is not None else 0.0)

        opname_date = row.get("stock_opname_date")
        try:
            if isinstance(opname_date, date):
                cols[6].write(opname_date.isoformat())
            else:
                cols[6].write(str(opname_date))
        except Exception:
            cols[6].write(str(opname_date))

        st.markdown('<div class="compact-action-row">', unsafe_allow_html=True)
        action_cols = cols[7].columns([0.85, 0.85, 0.85])
        if action_cols[0].button("View", key=f"view_opname_{row['opname_id']}", help="View"):
            st.session_state.stock_action = (row["opname_id"], "view")
        if action_cols[1].button("Edit", key=f"edit_opname_{row['opname_id']}", help="Edit"):
            st.session_state.stock_action = (row["opname_id"], "edit")
        if action_cols[2].button("Delete", key=f"delete_opname_{row['opname_id']}", help="Delete"):
            st.session_state.delete_stock_target = row["opname_id"]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if "stock_action" in st.session_state:
        opname_id, action = st.session_state.stock_action
        details = get_stock_opname_by_id(opname_id)
        if details:
            st.markdown("---")
            if action == "view":
                st.subheader(f"View Stock Opname #{opname_id}")
                st.json(details)
            elif action == "edit":
                st.subheader(f"Edit Stock Opname #{opname_id}")
                render_stock_opname_edit_form(details, material_options, location_options)


def render_stock_opname_edit_form(details, material_options, location_options):
    material_map = {m["material_name"]: m["material_id"] for m in material_options}
    location_map = {l["location_name"]: l["location_id"] for l in location_options}
    material_names = [m["material_name"] for m in material_options]
    location_names = [l["location_name"] for l in location_options]

    current_material = next(
        (m["material_name"] for m in material_options if m["material_id"] == details["material_id"]),
        "Select material",
    )
    current_location = next(
        (l["location_name"] for l in location_options if l["location_id"] == details["location_id"]),
        "Select location",
    )

    default_system = float(str(details["system_qty"])) if details.get("system_qty") is not None else 0.0
    default_actual = float(str(details["actual_qty"])) if details.get("actual_qty") is not None else 0.0
    default_notes = details.get("notes") or ""

    with st.form("stock_opname_edit_form"):
        material_name = st.selectbox(
            "Material",
            ["Select material"] + material_names,
            index=(material_names.index(current_material) + 1 if current_material in material_names else 0),
        )
        location_name = st.selectbox(
            "Location",
            ["Select location"] + location_names,
            index=(location_names.index(current_location) + 1 if current_location in location_names else 0),
        )
        c1, c2 = st.columns(2)
        with c1:
            system_qty = st.number_input("System Qty", min_value=0.0, value=default_system, step=1.0)
        with c2:
            actual_qty = st.number_input("Actual Qty", min_value=0.0, value=default_actual, step=1.0)
            
        stock_opname_date = st.date_input("Stock Opname Date", value=details["stock_opname_date"])
        notes = st.text_area("Notes", value=default_notes)
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            if material_name == "Select material" or location_name == "Select location":
                st.warning("Please complete all required fields before saving.")
            else:
                try:
                    difference_qty = actual_qty - system_qty
                    with st.spinner("Updating stock opname..."):
                        update_stock_opname(
                            opname_id=details["opname_id"],
                            material_id=material_map[material_name],
                            location_id=location_map[location_name],
                            system_qty=system_qty,
                            actual_qty=actual_qty,
                            difference_qty=difference_qty,
                            stock_opname_date=stock_opname_date.isoformat() if isinstance(stock_opname_date, date) else str(stock_opname_date),
                            notes=notes if notes else None,
                        )
                    st.session_state.stock_msg = ("success", "Stock opname updated successfully.")
                    del st.session_state.stock_action
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not update stock opname: {exc}")