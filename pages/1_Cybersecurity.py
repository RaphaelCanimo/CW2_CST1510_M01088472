from openai import OpenAI
import streamlit as st
import time
from app.data.db import connect_database
from app.data.incidents import *

# Show warning if user is not logged in
if not st.session_state.logged_in:
    st.warning("You must log in to access this page.")
    if st.button("Go to Login"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Home.py")
    st.stop()

st.set_page_config(page_title="Cyber Incidents Dashboard", layout="wide")
st.title("Cyber Incidents Dashboard")

conn = connect_database()
cursor = conn.cursor()

dashboard, chatbot = st.tabs(["Dashboard", "AI Chatbot"])

with dashboard:
    # ---------- READ incident metrics: Total / Open / Critical Incidents ----------
    key1, key2, key3 = st.columns(3)

    with key1:
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
        count = cursor.fetchone()
        st.text("Total incidents")
        st.header(count[0])

    with key2:
        cursor.execute(
            "SELECT COUNT(*) FROM cyber_incidents WHERE status = 'Open'")
        open_count = cursor.fetchone()
        st.text("Open incidents")
        st.header(open_count[0])

    with key3:
        cursor.execute(
            "SELECT COUNT(*) FROM cyber_incidents WHERE severity = 'Critical'")
        critical_count = cursor.fetchone()
        st.text("Critical severity count")
        st.header(critical_count[0])

    st.divider()

    # ---------- READ stats: Incident Types / High Incidents Status / Incidents > 15 Cases ----------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Incident Types")
        st.bar_chart(get_incidents_by_type_count(
            conn), x="incident_type", y="count")

    with col2:
        st.subheader("High Severity By Status")
        st.bar_chart(get_high_severity_by_status(conn), x="status", y="count")

    st.subheader("Incident Types With More Than 15 Cases")
    st.bar_chart(get_incident_types_with_many_cases(
        conn), x="incident_type", y="count")

    with st.expander("See the full raw data"):
        incidents = get_all_incidents(conn)
        st.dataframe(incidents, width='stretch')

    st.divider()

    # ---------- Tabs: Create / Update / Delete ----------
    tab_create, tab_update, tab_delete = st.tabs(
        ["Log New Incident", "Update Status", "Delete Incident"])

    # Get the min and max range for ID lookup
    cursor.execute("SELECT MIN(id), MAX(id) FROM cyber_incidents")
    min_id, max_id = cursor.fetchone()

    # ---------- CREATE new incident with a form ----------
    with tab_create:
        st.subheader("Log a New Cyber Incident")
        with st.form("new_incident"):
            # Form inputs
            date = st.date_input("Enter date of incident")
            incident_type = st.selectbox("Incident Type", [
                "DDoS", "Data Breach", "Insider Threat", "Malware", "Phishing", "Ransomware"])
            severity = st.selectbox(
                "Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox(
                "Status", ["Open", "In Progress", "Resolved"])
            description = st.text_area("Description")

            # Form submit button
            i_submitted = st.form_submit_button("Submit New Incident")

        # When form is submitted
        if i_submitted and date:
            insert_incident(conn, date, incident_type, severity, status,
                            description, st.session_state.username)
            st.success("✓ Incident added successfully!")
            time.sleep(1)
            st.rerun()

    # ---------- UPDATE incident status ----------
    with tab_update:
        st.subheader("Change Incident Status")
        with st.form("update_status"):
            incident_id = st.number_input("Enter incident ID", min_id, max_id)
            new_status = st.selectbox(
                "Status", ["Open", "In Progress", "Resolved"])

            u_submitted = st.form_submit_button("Update Status")

        # When form is submitted
        if u_submitted and incident_id:
            update_incident_status(conn, incident_id, new_status)
            st.success("✓ Incident updated successfully!")
            time.sleep(1)
            st.rerun()

    # ---------- DELETE incident ----------
    with tab_delete:
        st.subheader("Remove Incident from Database")
        st.warning("Record deletion requires careful consideration.")
        with st.form("delete_incident"):
            incident_id_2 = st.number_input(
                "Enter incident ID", min_id, max_id)

            d_submitted = st.form_submit_button("Delete Incident")

        # When form is submitted
        if d_submitted and incident_id_2:
            rows_affected = delete_incident(conn, incident_id_2)
            st.success(f"✓ {rows_affected} row/s deleted successfully!")
            time.sleep(1)
            st.rerun()

    conn.close()

with chatbot:
    # Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Permanent system prompt
    SYSTEM_PROMPT = (
        "You are a helpful cybersecurity expert. Provide accurate, helpful "
        "information about cybersecurity incidents, best practices, and threat analysis."
    )

    # Title
    st.subheader("💬 ChatGPT - OpenAI API")
    st.caption("Powered by GPT-4.1 mini")

    # Initialize session state with the system message
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Sidebar with controls
    with st.sidebar:
        with st.expander("⚙️ Chat Settings", expanded=False):

            # Display message count (excluding system message)
            message_count = len(
                [m for m in st.session_state.messages if m["role"] != "system"]
            )
            st.metric("Messages", message_count)

            # Clear chat button
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ]
                st.rerun()

            # Model selection
            model = st.selectbox(
                "Model",
                ["gpt-4.1-mini", "gpt-4.1"],
                index=0
            )

            # Temperature slider
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=1.0,
                step=0.1,
                help="Higher values make output more random"
            )
        
        st.divider()
        
        # Show logout button in sidebar only when user is logged in
        if st.session_state.logged_in:
            if st.button("Log out"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.info("You have been logged out")
                time.sleep(1)
                st.switch_page("Home.py")


    # Display all previous non-system messages
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input
    prompt = st.chat_input("Say something...")

    if prompt:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Call OpenAI API with streaming
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                stream=True
            )

        # Display streaming response
        with st.chat_message("assistant"):
            container = st.empty()
            full_reply = ""

            for chunk in completion:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_reply += delta.content
                    container.markdown(full_reply + "▌")

            container.markdown(full_reply)

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_reply
        })
