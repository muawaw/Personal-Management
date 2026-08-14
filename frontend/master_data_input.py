import streamlit as st
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.master_data import (
    create_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    delete_category,
    create_location,
    get_all_locations,
    get_location_by_id,
    update_location,
    delete_location,
    create_material,
    get_all_materials,
    get_material_by_id,
    update_material,
    delete_material,
)
from constant.error_handling import handle_ui_exception


# ==========================================
# CONFIRMATION DIALOGS
# ==========================================

@st.dialog("Confirm Deletion")
def confirm_delete_dialog(entity_type, entity_id, entity_name):
    st.write(f"Are you sure you want to delete {entity_type} **{entity_name}** (ID: {entity_id})?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete", type="primary", use_container_width=True):
            try:
                with st.spinner(f"Deleting {entity_type.lower()}..."):
                    if entity_type == "Category":
                        delete_category(entity_id)
                    elif entity_type == "Location":
                        delete_location(entity_id)
                    elif entity_type == "Material":
                        delete_material(entity_id)

                st.session_state.master_msg = ("success", f"{entity_type} deleted successfully.")
                if "master_action" in st.session_state and st.session_state.master_action[0] == entity_id:
                    del st.session_state.master_action
                if "delete_master_target" in st.session_state:
                    del st.session_state.delete_master_target
                st.rerun()
            except Exception as exc:
                st.error(handle_ui_exception(exc))
    with col2:
        if st.button("Cancel", use_container_width=True):
            if "delete_master_target" in st.session_state:
                del st.session_state.delete_master_target
            st.rerun()


# ==========================================
# MAIN RENDER FUNCTION
# ==========================================

def render():
    st.title("Master Data Management")

    if "master_msg" in st.session_state:
        msg_type, msg_text = st.session_state.pop("master_msg")
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "error":
            st.error(msg_text)

    if "delete_master_target" in st.session_state:
        target_type, target_id, target_name = st.session_state.delete_master_target
        confirm_delete_dialog(target_type, target_id, target_name)

    tab_material, tab_category, tab_location = st.tabs(["Materials", "Categories", "Locations"])

    with tab_material:
        render_material_tab()

    with tab_category:
        render_category_tab()

    with tab_location:
        render_location_tab()


# ==========================================
# 1. MATERIAL TAB
# ==========================================

def render_material_tab():
    categories = get_all_categories()
    category_map = {c["category_name"]: c["category_id"] for c in categories}
    category_lookup = {c["category_id"]: c["category_name"] for c in categories}

    with st.expander("New Material", expanded=False):
        with st.form("material_input_form"):
            material_code = st.text_input("Material Code")
            material_name = st.text_input("Material Name")
            category_name = st.selectbox(
                "Category", ["Select category"] + [c["category_name"] for c in categories]
            )
            unit_of_measure = st.text_input("Unit of Measure", value="PCS")

            submit_col, _ = st.columns([1, 3])
            with submit_col:
                submitted = st.form_submit_button("Submit Material")

            if submitted:
                if not material_code or not material_name:
                    st.warning("Please complete Material Code and Material Name before submitting.")
                else:
                    try:
                        cat_id = category_map.get(category_name) if category_name != "Select category" else None
                        with st.spinner("Saving material..."):
                            create_material(
                                material_code=material_code,
                                material_name=material_name,
                                category_id=cat_id,
                                unit_of_measure=unit_of_measure,
                            )
                        st.session_state.master_msg = ("success", "Material saved successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(handle_ui_exception(exc))

    st.markdown("---")
    st.subheader("Material Records")
    try:
        materials = get_all_materials()
        if not materials:
            st.info("No material records found.")
            return

        display_material_table(materials, category_lookup, categories)
    except Exception as exc:
        st.error(handle_ui_exception(exc))


def display_material_table(materials, category_lookup, categories):
    headers = ["ID", "Code", "Name", "Category", "UoM", "Actions"]
    cols = st.columns([0.6, 1.2, 2.0, 1.5, 0.8, 1.8])
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

    for row in materials:
        cols = st.columns([0.6, 1.2, 2.0, 1.5, 0.8, 1.6])
        cols[0].write(row["material_id"])
        cols[1].write(row["material_code"])
        cols[2].write(row["material_name"])
        cols[3].write(category_lookup.get(row["category_id"], "-"))
        cols[4].write(row.get("unit_of_measure", "PCS"))

        st.markdown('<div class="compact-action-row">', unsafe_allow_html=True)
        action_cols = cols[5].columns([0.85, 0.85, 0.85])
        if action_cols[0].button("View", key=f"view_mat_{row['material_id']}", help="View"):
            st.session_state.master_action = ("Material", row["material_id"], "view")
        if action_cols[1].button("Edit", key=f"edit_mat_{row['material_id']}", help="Edit"):
            st.session_state.master_action = ("Material", row["material_id"], "edit")
        if action_cols[2].button("Delete", key=f"delete_mat_{row['material_id']}", help="Delete"):
            st.session_state.delete_master_target = ("Material", row["material_id"], row["material_name"])
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if "master_action" in st.session_state:
        entity_type, entity_id, action = st.session_state.master_action
        if entity_type == "Material":
            details = get_material_by_id(entity_id)
            if details:
                st.markdown("---")
                if action == "view":
                    st.subheader(f"View Material #{entity_id}")
                    st.json(details)
                elif action == "edit":
                    st.subheader(f"Edit Material #{entity_id}")
                    render_material_edit_form(details, categories)


def render_material_edit_form(details, categories):
    category_map = {c["category_name"]: c["category_id"] for c in categories}
    category_names = [c["category_name"] for c in categories]

    current_cat_name = next(
        (c["category_name"] for c in categories if c["category_id"] == details.get("category_id")),
        "Select category",
    )

    with st.form("material_edit_form"):
        material_code = st.text_input("Material Code", value=details["material_code"])
        material_name = st.text_input("Material Name", value=details["material_name"])
        category_name = st.selectbox(
            "Category",
            ["Select category"] + category_names,
            index=(category_names.index(current_cat_name) + 1 if current_cat_name in category_names else 0),
        )
        unit_of_measure = st.text_input("Unit of Measure", value=details.get("unit_of_measure", "PCS"))

        submitted = st.form_submit_button("Save Changes")

        if submitted:
            if not material_code or not material_name:
                st.warning("Please complete Material Code and Material Name before saving.")
            else:
                try:
                    cat_id = category_map.get(category_name) if category_name != "Select category" else None
                    with st.spinner("Updating material..."):
                        update_material(
                            material_id=details["material_id"],
                            material_code=material_code,
                            material_name=material_name,
                            category_id=cat_id,
                            unit_of_measure=unit_of_measure,
                        )
                    st.session_state.master_msg = ("success", "Material updated successfully.")
                    del st.session_state.master_action
                    st.rerun()
                except Exception as exc:
                    st.error(handle_ui_exception(exc))


# ==========================================
# 2. CATEGORY TAB
# ==========================================

def render_category_tab():
    with st.expander("New Category", expanded=False):
        with st.form("category_input_form"):
            category_code = st.text_input("Category Code")
            category_name = st.text_input("Category Name")

            submit_col, _ = st.columns([1, 3])
            with submit_col:
                submitted = st.form_submit_button("Submit Category")

            if submitted:
                if not category_code or not category_name:
                    st.warning("Please fill in both Category Code and Category Name.")
                else:
                    try:
                        with st.spinner("Saving category..."):
                            create_category(category_code=category_code, category_name=category_name)
                        st.session_state.master_msg = ("success", "Category saved successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(handle_ui_exception(exc))

    st.markdown("---")
    st.subheader("Category Records")
    try:
        categories = get_all_categories()
        if not categories:
            st.info("No category records found.")
            return

        display_category_table(categories)
    except Exception as exc:
        st.error(handle_ui_exception(exc))


def display_category_table(categories):
    headers = ["ID", "Code", "Name", "Actions"]
    cols = st.columns([0.8, 1.8, 3.0, 1.8])
    for col, label in zip(cols, headers):
        col.markdown(f"**{label}**")

    for row in categories:
        cols = st.columns([0.8, 1.8, 3.0, 1.6])
        cols[0].write(row["category_id"])
        cols[1].write(row["category_code"])
        cols[2].write(row["category_name"])

        st.markdown('<div class="compact-action-row">', unsafe_allow_html=True)
        action_cols = cols[3].columns([0.85, 0.85, 0.85])
        if action_cols[0].button("View", key=f"view_cat_{row['category_id']}", help="View"):
            st.session_state.master_action = ("Category", row["category_id"], "view")
        if action_cols[1].button("Edit", key=f"edit_cat_{row['category_id']}", help="Edit"):
            st.session_state.master_action = ("Category", row["category_id"], "edit")
        if action_cols[2].button("Delete", key=f"delete_cat_{row['category_id']}", help="Delete"):
            st.session_state.delete_master_target = ("Category", row["category_id"], row["category_name"])
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if "master_action" in st.session_state:
        entity_type, entity_id, action = st.session_state.master_action
        if entity_type == "Category":
            details = get_category_by_id(entity_id)
            if details:
                st.markdown("---")
                if action == "view":
                    st.subheader(f"View Category #{entity_id}")
                    st.json(details)
                elif action == "edit":
                    st.subheader(f"Edit Category #{entity_id}")
                    render_category_edit_form(details)


def render_category_edit_form(details):
    with st.form("category_edit_form"):
        category_code = st.text_input("Category Code", value=details["category_code"])
        category_name = st.text_input("Category Name", value=details["category_name"])
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            if not category_code or not category_name:
                st.warning("Please fill in both Category Code and Category Name.")
            else:
                try:
                    with st.spinner("Updating category..."):
                        update_category(
                            category_id=details["category_id"],
                            category_code=category_code,
                            category_name=category_name,
                        )
                    st.session_state.master_msg = ("success", "Category updated successfully.")
                    del st.session_state.master_action
                    st.rerun()
                except Exception as exc:
                    st.error(handle_ui_exception(exc))


# ==========================================
# 3. LOCATION TAB
# ==========================================

def render_location_tab():
    with st.expander("New Location", expanded=False):
        with st.form("location_input_form"):
            location_code = st.text_input("Location Code")
            location_name = st.text_input("Location Name")
            description = st.text_area("Description")

            submit_col, _ = st.columns([1, 3])
            with submit_col:
                submitted = st.form_submit_button("Submit Location")

            if submitted:
                if not location_code or not location_name:
                    st.warning("Please fill in both Location Code and Location Name.")
                else:
                    try:
                        with st.spinner("Saving location..."):
                            create_location(
                                location_code=location_code,
                                location_name=location_name,
                                description=description if description else None,
                            )
                        st.session_state.master_msg = ("success", "Location saved successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(handle_ui_exception(exc))

    st.markdown("---")
    st.subheader("Location Records")
    try:
        locations = get_all_locations()
        if not locations:
            st.info("No location records found.")
            return

        display_location_table(locations)
    except Exception as exc:
        st.error(handle_ui_exception(exc))


def display_location_table(locations):
    headers = ["ID", "Code", "Name", "Description", "Actions"]
    cols = st.columns([0.6, 1.2, 2.0, 2.0, 1.8])
    for col, label in zip(cols, headers):
        col.markdown(f"**{label}**")

    for row in locations:
        cols = st.columns([0.6, 1.2, 2.0, 2.0, 1.6])
        cols[0].write(row["location_id"])
        cols[1].write(row["location_code"])
        cols[2].write(row["location_name"])
        cols[3].write(row.get("description") or "-")

        st.markdown('<div class="compact-action-row">', unsafe_allow_html=True)
        action_cols = cols[4].columns([0.85, 0.85, 0.85])
        if action_cols[0].button("View", key=f"view_loc_{row['location_id']}", help="View"):
            st.session_state.master_action = ("Location", row["location_id"], "view")
        if action_cols[1].button("Edit", key=f"edit_loc_{row['location_id']}", help="Edit"):
            st.session_state.master_action = ("Location", row["location_id"], "edit")
        if action_cols[2].button("Delete", key=f"delete_loc_{row['location_id']}", help="Delete"):
            st.session_state.delete_master_target = ("Location", row["location_id"], row["location_name"])
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if "master_action" in st.session_state:
        entity_type, entity_id, action = st.session_state.master_action
        if entity_type == "Location":
            details = get_location_by_id(entity_id)
            if details:
                st.markdown("---")
                if action == "view":
                    st.subheader(f"View Location #{entity_id}")
                    st.json(details)
                elif action == "edit":
                    st.subheader(f"Edit Location #{entity_id}")
                    render_location_edit_form(details)


def render_location_edit_form(details):
    with st.form("location_edit_form"):
        location_code = st.text_input("Location Code", value=details["location_code"])
        location_name = st.text_input("Location Name", value=details["location_name"])
        description = st.text_area("Description", value=details.get("description") or "")
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            if not location_code or not location_name:
                st.warning("Please fill in both Location Code and Location Name.")
            else:
                try:
                    with st.spinner("Updating location..."):
                        update_location(
                            location_id=details["location_id"],
                            location_code=location_code,
                            location_name=location_name,
                            description=description if description else None,
                        )
                    st.session_state.master_msg = ("success", "Location updated successfully.")
                    del st.session_state.master_action
                    st.rerun()
                except Exception as exc:
                    st.error(handle_ui_exception(exc))