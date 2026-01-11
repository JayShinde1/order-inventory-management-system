import streamlit as st
import requests
import os

# =========================
# CONFIG
# =========================
BASE_URL = os.getenv(
    "FRONTEND_API_BASE_URL",
    "http://localhost:8000"
)

st.set_page_config(
    page_title="Inventory & Order Management System",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "user_details" not in st.session_state:
    st.session_state.user_details = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# =========================
# SIDEBAR – LOGIN / LOGOUT
# =========================
st.sidebar.title("Account")

if not st.session_state.token:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        res = requests.post(
            f"{BASE_URL}/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if res.status_code == 200:
            token_data = res.json()
            st.session_state.token = token_data["access_token"]
            st.session_state.username = username

            # fetch user details
            me = requests.get(
                f"{BASE_URL}/get-details",
                headers=auth_headers()
            )

            if me.status_code == 200:
                st.session_state.user_details = me.json()
                st.session_state.role = me.json().get("role")

            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Invalid username or password")

else:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    st.sidebar.write(f"Role: **{st.session_state.role}**")

    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.role = None
        st.session_state.username = None
        st.session_state.user_details = None
        st.rerun()


# =========================
# PUBLIC HOME – BROWSE BOOKS
# =========================
st.title("Inventory & Order Management System")
st.write("Browse books publicly. Login to place orders or manage inventory.")

st.header("Browse Books")

browse_option = st.selectbox(
    "Browse Options",
    [
        "All Books",
        "By Book ID",
        "By Domain",
        "By Domain & Budget"
    ]
)

books = None

if browse_option == "All Books":
    res = requests.get(f"{BASE_URL}/public/")
    if res.status_code == 200:
        books = res.json()

elif browse_option == "By Book ID":
    book_id = st.number_input("Book ID", min_value=1)
    if st.button("Search"):
        res = requests.get(f"{BASE_URL}/public/{book_id}")
        if res.status_code == 200:
            books = [res.json()]
        else:
            st.error("Book not found")

elif browse_option == "By Domain":
    domain = st.text_input("Domain")
    if st.button("Search"):
        res = requests.get(
            f"{BASE_URL}/public/search/",
            params={"domain": domain}
        )
        if res.status_code == 200:
            books = res.json()
        else:
            st.error("No books found")

elif browse_option == "By Domain & Budget":
    domain = st.text_input("Domain")
    max_price = st.number_input("Max Price", min_value=0)
    if st.button("Search"):
        res = requests.get(
            f"{BASE_URL}/public/domain/{domain}",
            params={"max_price": max_price}
        )
        if res.status_code == 200:
            books = res.json()
        else:
            st.error("No books found")

if books:
    st.table(books)


# =========================
# REGISTER NEW USER (ONLY IF LOGGED OUT)
# =========================
if not st.session_state.token:
    st.divider()
    st.subheader("Create Account")

    new_username = st.text_input("Username", key="signup_username")
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Create Account"):
        if not new_username or not new_email or not new_password:
            st.error("All fields are required")
        else:
            payload = {
                "username": new_username,
                "email": new_email,
                "password": new_password,
                "role": "user"
            }

            res = requests.post(
                f"{BASE_URL}/create-user",
                json=payload
            )

            if res.status_code == 201:
                st.success("Account created successfully. You can now log in.")
            else:
                st.error(res.text)


# =========================
# STOP IF NOT LOGGED IN
# =========================
if not st.session_state.token:
    st.stop()


# =========================
# AUTHENTICATED TABS
# =========================
tabs = ["My Profile", "Place Order", "My Orders"]

if st.session_state.role == "admin":
    tabs.extend([
        "Add Book",
        "All Orders",
        "Update Order Status",
        "Update Book Stock",
        "Delete Book"
    ])

tab_objs = st.tabs(tabs)


# =========================
# USER PROFILE (GET DETAILS)
# =========================
with tab_objs[0]:
    st.header("My Profile")

    if "show_profile" not in st.session_state:
        st.session_state.show_profile = False

    if st.button("View / Hide Profile"):
        st.session_state.show_profile = not st.session_state.show_profile

    if st.session_state.show_profile:
        if st.session_state.user_details:
            st.json(st.session_state.user_details)
        else:
            st.info("User details not available")


# =========================
# PLACE ORDER
# =========================
with tab_objs[1]:
    st.header("Place Order")

    book_id = st.number_input("Book ID", min_value=1)
    quantity = st.number_input("Quantity", min_value=1)

    if st.button("Place Order"):
        payload = {"book_id": book_id, "quantity": quantity}
        res = requests.post(
            f"{BASE_URL}/orders/",
            json=payload,
            headers=auth_headers()
        )

        if res.status_code == 201:
            st.success("Order placed successfully")
        else:
            st.error(res.text)


# =========================
# MY ORDERS
# =========================
with tab_objs[2]:
    st.header("My Orders")

    res = requests.get(
        f"{BASE_URL}/orders/get-my-orders",
        headers=auth_headers()
    )

    if res.status_code == 200:
        orders = res.json()
        if orders:
            st.table(orders)
        else:
            st.info("No orders found.")
    else:
        st.error("Failed to fetch orders.")
