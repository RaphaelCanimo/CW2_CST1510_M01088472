from openai import OpenAI
import streamlit as st
import time
from app.data.db import connect_database
from app.data.tickets import *

# Show warning if user is not logged in
if not st.session_state.logged_in:
    st.warning("You must log in to access this page.")
    if st.button("Go to Login"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Home.py")
    st.stop()

st.set_page_config(page_title="IT Dashboard", layout="wide")
st.title("IT Dashboard")

conn = connect_database()
cursor = conn.cursor()

dashboard, chatbot = st.tabs(["Dashboard", "AI Chatbot"])

with dashboard:
    # ---------- READ tickets metrics: Total / Critical / Open Tickets ----------
    key1, key2, key3 = st.columns(3)

    with key1:
        cursor.execute("SELECT COUNT(*) FROM it_tickets")
        count = cursor.fetchone()
        st.text("Total tickets")
        st.header(count[0])

    with key2:
        cursor.execute(
            "SELECT COUNT(*) FROM it_tickets WHERE priority = 'Critical'")
        critical_count = cursor.fetchone()
        st.text("Total Critical Tickets")
        st.header(critical_count[0])

    with key3:
        cursor.execute(
            "SELECT COUNT(*) FROM it_tickets WHERE status = 'Open'")
        open_count = cursor.fetchone()
        st.text("Open Tickets")
        st.header(open_count[0])

    st.divider()

    # ---------- READ stats: Ticket Types of Priority / Status / Categories ----------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tickets Priority")
        st.bar_chart(get_tickets_by_priority(conn), x="priority", y="count")

    with col2:
        st.subheader("Tickets By Status")
        st.bar_chart(get_tickets_by_status(conn), x="status", y="count")

    st.subheader("Tickets Categories")
    st.bar_chart(get_tickets_by_category(conn), x="category", y="count")

    with st.expander("See the full raw data"):
        tickets = get_all_tickets(conn)
        st.dataframe(tickets, width='stretch')

    st.divider()

    # ---------- Tabs: Create / Update / Delete ----------
    tab_create, tab_update, tab_update_2, tab_update_3, tab_delete = st.tabs(
        ["Log New Ticket", "Update Ticket Status", "Update Ticket Assignment", "Resolve Ticket", "Delete Ticket"])


    # Get the min and max range for ID lookup
    cursor.execute("SELECT MIN(id), MAX(id) FROM it_tickets")
    min_id, max_id = cursor.fetchone()

    # ---------- CREATE new ticket ----------
    with tab_create:
        st.subheader("Log a New Ticket")
        with st.form("new_ticket"):
            # Form inputs
            priority = st.selectbox("Select Priority Level", [
                                    'Critical', 'High', 'Medium', 'Low'])
            status = st.selectbox(
                "Select Status", ['Open', 'In Progress', 'Resolved', 'Closed'])
            category = st.selectbox("Select Category", [
                                    'Hardware', 'Software', 'Network', 'Access Request', 'Security'])
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            created_date = st.date_input("Created At")
            # Form submit button
            i_submitted = st.form_submit_button("Submit New Ticket")

        # When form is submitted
        if i_submitted and priority:
            insert_ticket(conn, f"TKT-{max_id + 1001}", priority,
                        status, category, subject, description, created_date)
            st.success("✓ Ticket added successfully!")
            time.sleep(1)
            st.rerun()

    # ---------- UPDATE ticket attributes ----------
    with tab_update:
        st.subheader("Change Ticket Status")
        with st.form("update_ticket_status"):
            ticket_id = st.number_input("Enter ticket ID", min_id, max_id)
            new_status = st.selectbox("Update Status", [
                                    'Closed', 'In Progress', 'Open', 'Resolved'])

            u_submitted = st.form_submit_button("Update Ticket Status")

        # When form is submitted
        if u_submitted and ticket_id:
            update_ticket_status(conn, ticket_id, new_status)
            st.success("✓ Ticket updated successfully!")
            time.sleep(1)
            st.rerun()

    with tab_update_2:
        st.subheader("Change Ticket Assignment")
        with st.form("update_ticket_assignment"):
            ticket_id_2 = st.number_input("Enter ticket ID", min_id, max_id)
            assigned_to = st.text_input("Assigned to")

            u2_submitted = st.form_submit_button("Update Ticket Assignment")

        # When form is submitted
        if u2_submitted and ticket_id_2:
            update_ticket_assignment(conn, ticket_id_2, assigned_to)
            st.success("✓ Ticket updated successfully!")
            time.sleep(1)
            st.rerun()

    with tab_update_3:
        st.subheader("Resolve Ticket")
        with st.form("resolve_ticket"):
            ticket_id_3 = st.number_input("Enter ticket ID", min_id, max_id)
            resolved_date = st.date_input("Resolved Date")

            u3_submitted = st.form_submit_button("Resolve Ticket")

        # When form is submitted
        if u3_submitted and ticket_id_3:
            update_ticket_assignment(conn, ticket_id_3, resolved_date)
            st.success("✓ Ticket updated successfully!")
            time.sleep(1)
            st.rerun()

    # ---------- DELETE ticket ----------
    with tab_delete:
        st.subheader("Remove Ticket from Database")
        st.warning("Record deletion requires careful consideration.")
        with st.form("delete_ticket"):
            ticket_id_4 = st.number_input("Enter ticket ID", min_id, max_id)

            d_submitted = st.form_submit_button("Delete Ticket")

        # When form is submitted
        if d_submitted and ticket_id_4:
            rows_affected = delete_ticket(conn, ticket_id)
            st.success(f"✓ {rows_affected} row/s deleted successfully!")
            time.sleep(1)
            st.rerun()

    conn.close()

with chatbot:
    # Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Permanent system prompt
    SYSTEM_PROMPT = (
        "You are an experienced IT systems administrator and infrastructure expert"
        " with comprehensive knowledge across enterprise technology."
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
