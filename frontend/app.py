import streamlit as st
import requests
import os

# =========================
# CONFIG
# =========================
BASE_URL = os.getenv("FRONTEND_API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Inventory & Order Management System",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================
for key in ["token", "role", "username", "user_details"]:
    if key not in st.session_state:
        st.session_state[key] = None


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

            me = requests.get(f"{BASE_URL}/get-details", headers=auth_headers())
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
        for key in ["token", "role", "username", "user_details"]:
            st.session_state[key] = None
        st.rerun()


# =========================
# PUBLIC HOME
# =========================
st.title("Inventory & Order Management System")
st.write("Browse books publicly or search using natural language.")

# =========================
# AI SEARCH
# =========================
st.subheader("🔍 AI-Powered Book Search")

query = st.text_input(
    "Ask in natural language",
    placeholder="e.g. Give me personal finance books under 300 sorted by price desc"
)

page = st.number_input("Page", min_value=1, value=1)
page_size = st.selectbox("Page Size", [5, 10, 20, 50], index=1)

if st.button("Search with AI"):
    payload = {
        "query": query,
        "page": page,
        "page_size": page_size
    }

    res = requests.post(f"{BASE_URL}/public/ai-search", json=payload)

    if res.status_code == 200:
        data = res.json()

        st.caption(
            f"Page {data['current_page']} of {data['total_pages']} "
            f"({data['total_items']} total results)"
        )

        results = data.get("results", [])

        if results:
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No books matched your query.")
    else:
        st.error(res.text)


# =========================
# BASIC PUBLIC BROWSING
# =========================
st.divider()
st.subheader("📚 Browse All Books")

res = requests.get(f"{BASE_URL}/public/")
if res.status_code == 200:
    data = res.json()

    st.caption(
        f"Page {data['current_page']} of {data['total_pages']} "
        f"({data['total_items']} total books)"
    )

    books = data.get("results", [])

    if books:
        st.dataframe(
            books,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No books available.")
else:
    st.error("Failed to fetch books")


# =========================
# STOP IF NOT LOGGED IN
# =========================
if not st.session_state.token:
    st.info("Login to place orders or manage inventory.")
    st.stop()


# =========================
# AUTHENTICATED TABS
# =========================
tabs = ["My Profile", "Place Order", "My Orders"]

if st.session_state.role == "admin":
    tabs += ["Add Book", "All Orders"]

tab_objs = st.tabs(tabs)


# =========================
# MY PROFILE
# =========================
with tab_objs[0]:
    st.header("My Profile")
    st.json(st.session_state.user_details)


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
            st.dataframe(orders, use_container_width=True, hide_index=True)
        else:
            st.info("No orders found.")
    else:
        st.error("Failed to fetch orders.")
