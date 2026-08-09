import streamlit as st
from pathlib import Path
import sys
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.sales import (
    create_sale,
    get_all_sales,
    get_sale_by_id,
    update_sale,
    delete_sale,
)
from backend.master_data import get_all_materials, get_all_locations

def render():
    st.title("Sales Input")

    material_options = get_all_materials()
    location_options = get_all_locations()

    material_map = {m["material_name"]: m["material_id"] for m in material_options}
    location_map = {l["location_name"]: l["location_id"] for l in location_options}

    with st.expander("New Sale", expanded=False):
        with st.form("sales_input_form"):
            sales_number = st.text_input("Sales Number")
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
            sales_date = st.date_input("Sales Date", value=date.today())

            submit_col, _ = st.columns([1, 3])
            with submit_col:
                submitted = st.form_submit_button("Submit Sale")

            if submitted:
                if material_name == "Select material" or location_name == "Select location" or not sales_number:
                    st.warning("Please complete all fields before submitting.")
                else:
                    try:
                        with st.spinner("Processing sale..."):
                            result = create_sale(
                                sales_number=sales_number,
                                material_id=material_map[material_name],
                                location_id=location_map[location_name],
                                quantity=quantity,
                                unit_price=unit_price,
                                sales_date=sales_date,
                            )
                        st.success("Sale saved successfully.")
                        st.json(result)
                    except Exception as exc:
                        st.error(f"Could not save sale: {exc}")

    st.markdown("---")
    st.subheader("Recent Sales")
    try:
        sales = get_all_sales()
        if not sales:
            st.info("No sales records found.")
            return

        display_sales_table(sales, material_options, location_options)
    except Exception as exc:
        st.error(f"Could not fetch sales: {exc}")


def display_sales_table(sales, material_options, location_options):
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

    for row in sales:
        cols = st.columns([0.6, 1.5, 1.5, 1.2, 0.8, 1.0, 1.2, 1.6])
        cols[0].write(row["sale_id"])
        cols[1].write(row["sales_number"])
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
        sales_date = row.get("sales_date")
        try:
            if isinstance(sales_date, date):
                cols[6].write(sales_date.isoformat())
            else:
                cols[6].write(str(sales_date))
        except Exception:
            cols[6].write(str(sales_date))

        st.markdown('<div class="compact-action-row">', unsafe_allow_html=True)
        action_cols = cols[7].columns([0.85, 0.85, 0.85])
        if action_cols[0].button("View", key=f"view_sale_{row['sale_id']}", help="View"):
            st.session_state.sales_action = (row["sale_id"], "view")
        if action_cols[1].button("Edit", key=f"edit_sale_{row['sale_id']}", help="Edit"):
            st.session_state.sales_action = (row["sale_id"], "edit")
        if action_cols[2].button("Delete", key=f"delete_sale_{row['sale_id']}", help="Delete"):
            try:
                with st.spinner("Deleting sale..."):
                    delete_sale(row["sale_id"])
                st.success("Sale deleted successfully.")
                # Streamlit will rerun the script on user interaction; no experimental_rerun call used.
            except Exception as exc:
                st.error(f"Could not delete sale: {exc}")
        st.markdown('</div>', unsafe_allow_html=True)

    if "sales_action" in st.session_state:
        sale_id, action = st.session_state.sales_action
        details = get_sale_by_id(sale_id)
        if details:
            st.markdown("---")
            if action == "view":
                st.subheader(f"View Sale #{sale_id}")
                st.json(details)
            elif action == "edit":
                st.subheader(f"Edit Sale #{sale_id}")
                render_sale_edit_form(details, material_options, location_options)


def render_sale_edit_form(details, material_options, location_options):
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

    with st.form("sales_edit_form"):
        sales_number = st.text_input("Sales Number", value=details["sales_number"])
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
        # Ensure numeric defaults are native Python floats (DB may return Decimal)
        try:
            default_qty = float(details["quantity"])
        except Exception:
            default_qty = details["quantity"]
        try:
            default_price = float(details["unit_price"])
        except Exception:
            default_price = details["unit_price"]
        quantity = st.number_input(
            "Quantity", min_value=0.0, value=default_qty, step=0.1
        )
        unit_price = st.number_input(
            "Unit Price", min_value=0.0, value=default_price, step=1000.0, format="%.2f"
        )
        sales_date = st.date_input("Sales Date", value=details["sales_date"])
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            if material_name == "Select material" or location_name == "Select location" or not sales_number:
                st.warning("Please complete all fields before saving.")
            else:
                try:
                    with st.spinner("Updating sale..."):
                        update_sale(
                            sale_id=details["sale_id"],
                            sales_number=sales_number,
                            material_id=material_map[material_name],
                            location_id=location_map[location_name],
                            quantity=quantity,
                            unit_price=unit_price,
                            sales_date=sales_date,
                        )
                    st.success("Sale updated successfully.")
                    del st.session_state.sales_action
                except Exception as exc:
                    st.error(f"Could not update sale: {exc}")
