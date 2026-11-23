"""
Bakery Manager - Streamlit front end for the MySQL bakery database.

Run:  streamlit run app.py
"""
import os
from datetime import datetime
from decimal import Decimal

import mysql.connector
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# Config (edit here, or set environment variables)
# ----------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "bakery_app"),
    "password": os.getenv("DB_PASSWORD", "YOUR_PASSWORD"),
    "database": os.getenv("DB_NAME", "bakery"),
}
LOW_STOCK_THRESHOLD = 10
TIERS = {"Bronze": 400, "Silver": 401, "Gold": 402}

st.set_page_config(page_title="Bakery Manager", page_icon="🥐", layout="wide")


# ----------------------------------------------------------------------------
# Database helpers
# ----------------------------------------------------------------------------
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=None) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame (Decimals converted to floats)."""
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        df = pd.DataFrame(cur.fetchall())
    finally:
        conn.close()
    for col in df.columns:
        if len(df) and isinstance(df[col].iloc[0], Decimal):
            df[col] = df[col].astype(float)
    return df


def execute(sql, params=None):
    """Run a single INSERT/UPDATE/DELETE."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
    finally:
        conn.close()


def next_id(cur, table, column, start):
    cur.execute(f"SELECT COALESCE(MAX({column}), {start}) + 1 FROM {table}")
    return int(cur.fetchone()[0])


def place_order(employee_id, customer_id, payment_method, payment_status, cart):
    """
    cart: list of dicts {item_id, price, qty}
    Writes Invoice -> Transaction -> Transaction_Order and decrements Inventory
    in ONE database transaction (all succeed or all roll back).
    """
    conn = get_conn()
    try:
        cur = conn.cursor()

        # Check stock first (lock the rows so two people can't oversell)
        for line in cart:
            cur.execute(
                "SELECT Quantity FROM Inventory WHERE Item_ID = %s FOR UPDATE",
                (line["item_id"],),
            )
            row = cur.fetchone()
            if row is None or row[0] < line["qty"]:
                raise ValueError(f"Not enough stock for item {line['item_id']}")

        payment_id = next_id(cur, "Invoice", "Payment_ID", 9000)
        transaction_id = next_id(cur, "`Transaction`", "Transaction_ID", 330)
        order_id = next_id(cur, "`Transaction`", "Order_ID", 600)
        receipt_id = next_id(cur, "`Transaction`", "Reciept_ID", 70000)  # (sic) spelling matches your table
        total = round(sum(l["price"] * l["qty"] for l in cart), 2)
        t_time = datetime.now().strftime("%I:%M%p").lstrip("0").lower()  # e.g. 7:15am

        cur.execute(
            "INSERT INTO Invoice (Payment_ID, Payment_Method, Payment_Status) VALUES (%s,%s,%s)",
            (payment_id, payment_method, payment_status),
        )
        cur.execute(
            """INSERT INTO `Transaction`
               (Transaction_ID, Order_ID, Reciept_ID, Employee_ID, Customer_ID,
                Payment_ID, Payment_Method, Payment_Status, Transaction_Total, T_Time)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (transaction_id, order_id, receipt_id, employee_id, customer_id,
             payment_id, payment_method, payment_status, total, t_time),
        )
        for line in cart:
            cur.execute(
                """INSERT INTO Transaction_Order
                   (Order_ID, Transaction_ID, Item_ID, Price, Quantity)
                   VALUES (%s,%s,%s,%s,%s)""",
                (order_id, transaction_id, line["item_id"], line["price"], line["qty"]),
            )
            cur.execute(
                "UPDATE Inventory SET Quantity = Quantity - %s WHERE Item_ID = %s",
                (line["qty"], line["item_id"]),
            )
        conn.commit()
        return transaction_id, total
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ----------------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------------
def login_screen():
    st.title("🥐 Bakery Manager")
    st.subheader("Employee login")
    with st.form("login"):
        emp_id = st.text_input("Employee ID")
        pwd = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        try:
            df = query(
                "SELECT Employee_ID FROM Login WHERE Employee_ID = %s AND Pwd = %s",
                (emp_id.strip(), pwd),
            )
        except Exception as e:
            st.error(f"Database error: {e}")
            return
        if len(df):
            st.session_state["employee_id"] = int(df["Employee_ID"].iloc[0])
            st.rerun()
        else:
            st.error("Invalid employee ID or password.")


# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
def page_menu():
    st.header("Menu")
    st.dataframe(
        query("SELECT Item_ID, Item_name, Category_Name, Price, Exp_Date FROM Menu"),
        use_container_width=True, hide_index=True,
    )


def page_inventory():
    st.header("Inventory")
    df = query(
        """SELECT i.Item_ID, i.Item_name, inv.Quantity
           FROM Inventory inv JOIN Item i ON i.Item_ID = inv.Item_ID
           ORDER BY inv.Quantity"""
    )
    out = df[df.Quantity == 0]
    low = df[(df.Quantity > 0) & (df.Quantity < LOW_STOCK_THRESHOLD)]
    c1, c2 = st.columns(2)
    c1.metric("Out of stock", len(out))
    c2.metric(f"Low stock (<{LOW_STOCK_THRESHOLD})", len(low))
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Update stock")
    with st.form("stock"):
        choice = st.selectbox("Item", df.Item_name)
        qty = st.number_input("New quantity", min_value=0, step=1)
        if st.form_submit_button("Save"):
            item_id = int(df[df.Item_name == choice].Item_ID.iloc[0])
            execute("UPDATE Inventory SET Quantity = %s WHERE Item_ID = %s", (qty, item_id))
            st.success(f"{choice} set to {qty}.")
            st.rerun()


def page_new_order():
    st.header("New order")
    menu = query(
        """SELECT m.Item_ID, m.Item_name, m.Price, inv.Quantity AS Stock
           FROM Menu m JOIN Inventory inv ON inv.Item_ID = m.Item_ID
           ORDER BY m.Item_name"""
    )
    customers = query(
        "SELECT Customer_ID, Customer_firstname, Customer_lastname FROM Rewards"
    )
    customers["label"] = (
        customers.Customer_firstname + " " + customers.Customer_lastname
        + " (#" + customers.Customer_ID.astype(str) + ")"
    )

    with st.form("order"):
        c1, c2, c3 = st.columns(3)
        cust_label = c1.selectbox("Customer", customers.label)
        method = c2.selectbox("Payment method", ["Cash", "Card"])
        status = c3.selectbox("Payment status", ["Valid", "Pending", "Invalid"])

        st.markdown("**Items**")
        quantities = {}
        for _, row in menu.iterrows():
            a, b = st.columns([3, 1])
            if row.Stock <= 0:
                a.write(f"{row.Item_name} — ${row.Price:.2f}")
                b.write("Out of stock")
                quantities[row.Item_ID] = 0
            else:
                quantities[row.Item_ID] = b.number_input(
                    f"{row.Item_name} — ${row.Price:.2f}  (stock: {int(row.Stock)})",
                    min_value=0, max_value=int(row.Stock), step=1,
                    key=f"qty_{row.Item_ID}",
                )
        submitted = st.form_submit_button("Place order")

    if submitted:
        cart = [
            {"item_id": int(r.Item_ID), "price": float(r.Price), "qty": int(quantities[r.Item_ID])}
            for _, r in menu.iterrows() if quantities[r.Item_ID] > 0
        ]
        if not cart:
            st.warning("Add at least one item.")
            return
        customer_id = int(customers[customers.label == cust_label].Customer_ID.iloc[0])
        try:
            tid, total = place_order(
                st.session_state["employee_id"], customer_id, method, status, cart
            )
            st.success(f"Order placed! Transaction #{tid}, total ${total:.2f}")
        except Exception as e:
            st.error(f"Could not place order: {e}")


def page_orders():
    st.header("Transactions")
    df = query(
        """SELECT t.Transaction_ID, t.T_Time, t.Employee_ID,
                  CONCAT(r.Customer_firstname, ' ', r.Customer_lastname) AS Customer,
                  t.Payment_Method, t.Payment_Status, t.Transaction_Total
           FROM `Transaction` t
           LEFT JOIN Rewards r ON r.Customer_ID = t.Customer_ID
           ORDER BY t.Transaction_ID DESC"""
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    if len(df):
        st.subheader("Order details")
        tid = st.selectbox("Transaction", df.Transaction_ID)
        st.dataframe(
            query(
                """SELECT i.Item_name, o.Quantity, o.Price, (o.Quantity * o.Price) AS Line_total
                   FROM Transaction_Order o JOIN Item i ON i.Item_ID = o.Item_ID
                   WHERE o.Transaction_ID = %s""",
                (int(tid),),
            ),
            use_container_width=True, hide_index=True,
        )


def page_rewards():
    st.header("Rewards customers")
    st.dataframe(query("SELECT * FROM Rewards"), use_container_width=True, hide_index=True)

    st.subheader("Add customer")
    with st.form("new_customer"):
        c1, c2 = st.columns(2)
        first = c1.text_input("First name")
        last = c2.text_input("Last name")
        phone = c1.text_input("Phone")
        email = c2.text_input("Email (optional)")
        tier = st.selectbox("Tier", list(TIERS))
        if st.form_submit_button("Add"):
            if not (first and last):
                st.warning("First and last name are required.")
            else:
                conn = get_conn()
                try:
                    cur = conn.cursor()
                    cid = next_id(cur, "Rewards", "Customer_ID", 0)
                    cur.execute(
                        """INSERT INTO Rewards (Customer_ID, Tier_ID, Tier_type, Customer_pn,
                           Customer_firstname, Customer_lastname, Customer_email)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (cid, TIERS[tier], tier, phone, first, last, email or None),
                    )
                    conn.commit()
                    st.success(f"Added {first} {last} (#{cid}).")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Could not add customer: {e}")
                finally:
                    conn.close()


def page_dashboard():
    st.header("Sales dashboard")
    st.caption("Only transactions with status 'Valid' are counted.")

    totals = query(
        """SELECT COUNT(*) AS n, COALESCE(SUM(Transaction_Total), 0) AS revenue
           FROM `Transaction` WHERE Payment_Status = 'Valid'"""
    ).iloc[0]
    n, revenue = int(totals["n"]), float(totals["revenue"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", f"${revenue:,.2f}")
    c2.metric("Transactions", n)
    c3.metric("Avg. transaction", f"${revenue / n:,.2f}" if n else "$0.00")

    left, right = st.columns(2)
    with left:
        st.subheader("Revenue by item")
        df = query(
            """SELECT i.Item_name, SUM(o.Price * o.Quantity) AS Revenue
               FROM Transaction_Order o
               JOIN Item i ON i.Item_ID = o.Item_ID
               JOIN `Transaction` t ON t.Transaction_ID = o.Transaction_ID
               WHERE t.Payment_Status = 'Valid'
               GROUP BY i.Item_name ORDER BY Revenue DESC"""
        )
        if len(df):
            st.bar_chart(df.set_index("Item_name"))
    with right:
        st.subheader("Revenue by payment method")
        df = query(
            """SELECT Payment_Method, SUM(Transaction_Total) AS Revenue
               FROM `Transaction` WHERE Payment_Status = 'Valid'
               GROUP BY Payment_Method"""
        )
        if len(df):
            st.bar_chart(df.set_index("Payment_Method"))

    st.subheader("Units sold by category")
    df = query(
        """SELECT m.Category_Name, SUM(o.Quantity) AS Units
           FROM Transaction_Order o
           JOIN Menu m ON m.Item_ID = o.Item_ID
           JOIN `Transaction` t ON t.Transaction_ID = o.Transaction_ID
           WHERE t.Payment_Status = 'Valid'
           GROUP BY m.Category_Name ORDER BY Units DESC"""
    )
    if len(df):
        st.bar_chart(df.set_index("Category_Name"))


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
PAGES = {
    "Dashboard": page_dashboard,
    "New Order": page_new_order,
    "Transactions": page_orders,
    "Menu": page_menu,
    "Inventory": page_inventory,
    "Rewards": page_rewards,
}

if "employee_id" not in st.session_state:
    login_screen()
else:
    st.sidebar.title("🥐 Bakery Manager")
    st.sidebar.write(f"Logged in as employee **{st.session_state['employee_id']}**")
    choice = st.sidebar.radio("Go to", list(PAGES))
    if st.sidebar.button("Log out"):
        del st.session_state["employee_id"]
        st.rerun()
    try:
        PAGES[choice]()
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
