import streamlit as st
from app.services.user_service import register_user, login_user
from app.data.users import get_user_by_username

st.set_page_config(page_title="Login / Register",
                   page_icon="🔒", layout="centered")

# ---------- Initialise session state ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        st.switch_page("pages/1_Cybersecurity.py")
    st.stop()

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input(
        "Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        # Check credentials against database
        if login_user(login_username, login_password):
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.success(f"Welcome back, {login_username}! ")
            st.switch_page("pages/1_Cybersecurity.py")
        else:
            st.error("Invalid username or password.")

# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input(
        "Choose a password", type="password", key="register_password")
    confirm_password = st.text_input(
        "Confirm password", type="password", key="register_confirm")

    if st.button("Create account"):
        # Basic validation
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif get_user_by_username(new_username):
            st.error("Username already exists. Choose another one.")
        else:
            # Create user in database
            if register_user(new_username, new_password):
                st.success(
                    "Account created! You can now log in from the Login tab.")
                st.info(
                    "Tip: go to the Login tab and sign in with your new account.")
            else:
                st.error(
                    "An error occurred while creating your account. Please try again.")
