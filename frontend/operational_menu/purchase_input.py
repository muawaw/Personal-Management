import streamlit as st
from pathlib import Path
import sys
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.purchasing import (
    create_purchase,
    get_all_purchases,
    get_purchase_by_id,
    update_purchase,
    delete_purchase,
)
from backend.master_data import get_all_materials, get_all_locations


def render():
    st.title("Purchase Input")

    material_options = get_all_materials()
    location_options = get_all_locations()

    material_map = {m["material_name"]: m["material_id"] for m in material_options}
    location_map = {l["location_name"]: l["location_id"] for l in location_options}

    with st.expander("New Purchase", expanded=False):
        with st.form("purchase_input_form"):
            purchase_number = st.text_input("Purchase Number")
            material_name = st.selectbox(
                "Material", ["Select material"] + [m["material_name"] for m in material_options]
            )
            location_name = st.selectbox(
                "Location", ["Select location"] + [l["location_name"] for l in location_options]
            )
            quantity = st.number_input("Quantity", min_value=0.0, value=1.0, step=0.1)
            unit_price = st.number_input(
                "Unit Price", min_value=0.0, value=0.0, step=1000.0, format="%.2f"
            )
            purchase_date = st.date_input("Purchase Date", value=date.today())

            submit_col, _ = st.columns([1, 3])
            with submit_col:
                submitted = st.form_submit_button("Submit Purchase")

            if submitted:
                if material_name == "Select material" or location_name == "Select location" or not purchase_number:
                    st.warning("Please complete all fields before submitting.")
                else:
                    try:
                        with st.spinner("Processing purchase..."):
                            result = create_purchase(
                                purchase_number=purchase_number,
                                material_id=material_map[material_name],
                                location_id=location_map[location_name],
                                quantity=quantity,
                                unit_price=unit_price,
                                purchase_date=purchase_date,
                            )
                        st.success("Purchase saved successfully.")
                        st.json(result)
                    except Exception as exc:
                        st.error(f"Could not save purchase: {exc}")

    st.markdown("---")
    st.subheader("Recent Purchases")
    try:
        purchases = get_all_purchases()
        if not purchases:
            st.info("No purchase records found.")
            return

        display_purchase_table(purchases, material_options, location_options)
    except Exception as exc:
        st.error(f"Could not fetch purchases: {exc}")


def display_purchase_table(purchases, material_options, location_options):
    headers = ["ID", "Number", "Material", "Location", "Qty", "Price", "Date", "Actions"]
    cols = st.columns([0.6, 1.5, 1.5, 1.2, 0.8, 1.0, 1.2, 1.8])
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

    for row in purchases:
        cols = st.columns([0.6, 1.5, 1.5, 1.2, 0.8, 1.0, 1.2, 1.6])
        cols[0].write(row["purchase_id"])
        cols[1].write(row["purchase_number"])
        cols[2].write(material_lookup.get(row["material_id"], row["material_id"]))
        cols[3].write(location_lookup.get(row["location_id"], row["location_id"]))
        # Render numeric/date values safely (DB may return Decimal/date types)
        try:
            cols[4].write(float(row["quantity"]))
        except Exception:
            cols[4].write(row["quantity"])
        try:
            cols[5].write(f"Rp {float(row['unit_price']):,.2f}")
        except Exception:
            cols[5].write(row.get("unit_price", ""))
        purchase_date = row.get("purchase_date")
        try:
            if isinstance(purchase_date, date):
                cols[6].write(purchase_date.isoformat())
            else:
                cols[6].write(str(purchase_date))
        except Exception:
            cols[6].write(str(purchase_date))

        st.markdown('<div class="compact-action-row">', unsafe_allow_html=True)
        action_cols = cols[7].columns([0.85, 0.85, 0.85])
        if action_cols[0].button("View", key=f"view_purchase_{row['purchase_id']}", help="View"):
            st.session_state.purchase_action = (row["purchase_id"], "view")
        if action_cols[1].button("Edit", key=f"edit_purchase_{row['purchase_id']}", help="Edit"):
            st.session_state.purchase_action = (row["purchase_id"], "edit")
        if action_cols[2].button("Delete", key=f"delete_purchase_{row['purchase_id']}", help="Delete"):
            try:
                with st.spinner("Deleting purchase..."):
                    delete_purchase(row["purchase_id"])
                st.success("Purchase deleted successfully.")
                # Streamlit will rerun the script on user interaction; no experimental_rerun call used.
            except Exception as exc:
                st.error(f"Could not delete purchase: {exc}")
        st.markdown('</div>', unsafe_allow_html=True)

    if "purchase_action" in st.session_state:
        purchase_id, action = st.session_state.purchase_action
        details = get_purchase_by_id(purchase_id)
        if details:
            st.markdown("---")
            if action == "view":
                st.subheader(f"View Purchase #{purchase_id}")
                st.json(details)
            elif action == "edit":
                st.subheader(f"Edit Purchase #{purchase_id}")
                render_purchase_edit_form(details, material_options, location_options)


def render_purchase_edit_form(details, material_options, location_options):
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

    with st.form("purchase_edit_form"):
        purchase_number = st.text_input("Purchase Number", value=details["purchase_number"])
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
        quantity = st.number_input(
            "Quantity", min_value=0.0, value=details["quantity"], step=0.1
        )
        unit_price = st.number_input(
            "Unit Price", min_value=0.0, value=details["unit_price"], step=1000.0, format="%.2f"
        )
        purchase_date = st.date_input("Purchase Date", value=details["purchase_date"])
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            if material_name == "Select material" or location_name == "Select location" or not purchase_number:
                st.warning("Please complete all fields before saving.")
            else:
                try:
                    with st.spinner("Updating purchase..."):
                        update_purchase(
                            purchase_id=details["purchase_id"],
                            purchase_number=purchase_number,
                            material_id=material_map[material_name],
                            location_id=location_map[location_name],
                            quantity=quantity,
                            unit_price=unit_price,
                            purchase_date=purchase_date,
                        )
                    st.success("Purchase updated successfully.")
                    del st.session_state.purchase_action
                except Exception as exc:
                    st.error(f"Could not update purchase: {exc}")
