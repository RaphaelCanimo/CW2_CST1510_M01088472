import streamlit as st
import time
from app.data.db import connect_database
from app.data.datasets import *

st.set_page_config(page_title="Data Science Dashboard", layout="wide")
st.title("Data Science Dashboard")

conn = connect_database()
cursor = conn.cursor()

# Show warning if user is not logged in
if not st.session_state.logged_in:
    st.warning("You must log in to access this page.")
    if st.button("Go to Login"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Home.py")
    st.stop()

# Show logout button in sidebar only when user is logged in
with st.sidebar:
    if st.session_state.logged_in:
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.info("You have been logged out")
            time.sleep(1)
            st.switch_page("Home.py")

# ---------- READ dataset metrics: Total Datasets / Records / File Size ----------
key1, key2, key3 = st.columns(3)

with key1:
    cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
    count = cursor.fetchone()
    st.text("Total datasets")
    st.header(count[0])

with key2:
    cursor.execute(
        "SELECT SUM(record_count) FROM datasets_metadata")
    total_record_count = cursor.fetchone()
    st.text("Total Record Count")
    st.header(f"{total_record_count[0]:,}")

with key3:
    cursor.execute("SELECT SUM(file_size_mb) FROM datasets_metadata")
    total_file_size = cursor.fetchone()
    st.text("Total File Size")
    st.header(f"{total_file_size[0] / 1024:.2f} GB")

st.divider()

# ---------- READ stats: Dataset Types / Sources ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Dataset Types")
    st.bar_chart(get_dataset_by_category_count(conn), x="category", y="count")

with col2:
    st.subheader("Dataset Sources")
    st.bar_chart(get_dataset_by_source(conn), x="source", y="count")

with st.expander("See the full raw data"):
    datasets = get_all_datasets(conn)
    st.dataframe(datasets, width='stretch')

st.divider()

# ---------- Tabs: Create / Update / Delete ----------
tab_create, tab_update, tab_update_2, tab_delete = st.tabs(
    ["Log New Dataset", "Update Record Count", "Update Last Updated", "Delete Dataset"])

# Get the min and max range for ID lookup
cursor.execute("SELECT MIN(id), MAX(id) FROM datasets_metadata")
min_id, max_id = cursor.fetchone()

# ---------- CREATE new dataset ----------
with tab_create:
    st.subheader("Log a New Dataset")
    with st.form("new_dataset"):
        # Form inputs
        dataset_name = st.text_input("Enter dataset name")
        category = st.selectbox("Category", [
                                "Cloud Logs", "Endpoint Data", "Malware Samples",
                                "Network Logs", "Threat Intelligence", "User Activity"])
        source = st.selectbox("Source", [
                              "External", "Internal", "Open-Source",
                              "Research Group", "Vendor A", "Vendor B"])
        last_updated = st.date_input("Enter last updated")
        record_count = st.number_input("Enter record count", 1)
        file_size_mb = st.number_input("Enter file size in MB")

        # Form submit button
        i_submitted = st.form_submit_button("Submit New Dataset")

    # When form is submitted
    if i_submitted and dataset_name:
        insert_dataset(conn, dataset_name, category, source, last_updated, record_count, file_size_mb)
        st.success("✓ Incident added successfully!")
        time.sleep(1)
        st.rerun()

# ---------- UPDATE dataset attributes ----------
with tab_update:
    st.subheader("Change Dataset Record Count")
    with st.form("update_record_count"):
        dataset_id = st.number_input("Enter dataset ID", min_id, max_id)
        new_record_count = st.number_input("Enter updated record count", 1)

        u_submitted = st.form_submit_button("Update Record Count")

    # When form is submitted
    if u_submitted and dataset_id:
        update_dataset_record_count(conn, dataset_id, new_record_count)
        st.success("✓ Dataset updated successfully!")
        time.sleep(1)
        st.rerun()

with tab_update_2:
    st.subheader("Change Dataset Last Updated Date")
    with st.form("update_last_updated"):
        dataset_id_2 = st.number_input("Enter dataset ID", min_id, max_id)
        new_date = st.date_input("Enter last updated")

        u2_submitted = st.form_submit_button("Update Last Updated Date")

    # When form is submitted
    if u2_submitted and dataset_id_2:
        update_dataset_last_updated(conn, dataset_id_2, new_date)
        st.success("✓ Dataset updated successfully!")
        time.sleep(1)
        st.rerun()

# ---------- DELETE dataset ----------
with tab_delete:
    st.subheader("Remove Dataset from Database")
    st.warning("Record deletion requires careful consideration.")
    with st.form("delete_dataset"):
        dataset_id_3 = st.number_input("Enter dataset ID", min_id, max_id)

        d_submitted = st.form_submit_button("Delete Dataset")

    # When form is submitted
    if d_submitted and dataset_id_3:
        rows_affected = delete_dataset(conn, dataset_id_3)
        st.success(f"✓ {rows_affected} row/s deleted successfully!")
        time.sleep(1)
        st.rerun()

conn.close()
