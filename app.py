import streamlit as st

from database import (
    create_tables,
    generate_demo_data
)

from auth import login
from employee import employee_page
from attendance import attendance_page
from leave import leave_page
from salary import salary_page
from performance import performance_page
from reports import reports_page


st.set_page_config(
    page_title="SmartHR",
    page_icon="👨‍💼",
    layout="wide"
)


# -------------------------------
# DATABASE INITIALIZATION
# -------------------------------

create_tables()

generate_demo_data(500)


# -------------------------------
# SESSION
# -------------------------------

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


# -------------------------------
# LOGIN
# -------------------------------

if not st.session_state.logged_in:

    login()

    st.stop()


# -------------------------------
# SIDEBAR
# -------------------------------

st.sidebar.title(
    "🏢 SmartHR"
)

st.sidebar.success(
    f"Logged in as: "
    f"{st.session_state.username}"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👨‍💼 Employees",
        "📅 Attendance",
        "🏖️ Leave",
        "💰 Salary",
        "⭐ Performance",
        "📊 Reports"
    ]
)


if st.sidebar.button(
    "🚪 Logout"
):

    st.session_state.logged_in = False

    st.rerun()


# -------------------------------
# DASHBOARD
# -------------------------------

if page == "🏠 Dashboard":

    st.title(
        "🏢 SmartHR Dashboard"
    )

    st.write(
        "Employee Management & HR Analytics System"
    )

    from database import get_connection

    conn = get_connection()

    total_employees = conn.execute("""
        SELECT COUNT(*)
        FROM employees
    """).fetchone()[0]

    active_employees = conn.execute("""
        SELECT COUNT(*)
        FROM employees
        WHERE status='Active'
    """).fetchone()[0]

    departments = conn.execute("""
        SELECT COUNT(
            DISTINCT department
        )
        FROM employees
    """).fetchone()[0]

    avg_salary = conn.execute("""
        SELECT AVG(salary)
        FROM employees
    """).fetchone()[0]

    present_today = conn.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = date('now')
        AND status='Present'
    """).fetchone()[0]

    pending_leaves = conn.execute("""
        SELECT COUNT(*)
        FROM leaves
        WHERE status='Pending'
    """).fetchone()[0]

    conn.close()


    # ---------------------------
    # METRICS
    # ---------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "👨‍💼 Total Employees",
        total_employees
    )

    col2.metric(
        "✅ Active Employees",
        active_employees
    )

    col3.metric(
        "🏢 Departments",
        departments
    )

    col4.metric(
        "💰 Average Salary",
        f"₹{avg_salary:,.0f}"
        if avg_salary else "₹0"
    )


    col5, col6 = st.columns(2)

    col5.metric(
        "📅 Present Today",
        present_today
    )

    col6.metric(
        "🏖️ Pending Leaves",
        pending_leaves
    )


    st.divider()

    st.subheader(
        "📈 HR Overview"
    )

    from database import get_connection
    import pandas as pd

    conn = get_connection()

    department_data = pd.read_sql_query("""
        SELECT
            department,
            COUNT(*) AS employees
        FROM employees
        GROUP BY department
    """, conn)

    conn.close()

    st.bar_chart(
        department_data.set_index(
            "department"
        )
    )


# -------------------------------
# EMPLOYEES
# -------------------------------

elif page == "👨‍💼 Employees":

    employee_page()


# -------------------------------
# ATTENDANCE
# -------------------------------

elif page == "📅 Attendance":

    attendance_page()


# -------------------------------
# LEAVE
# -------------------------------

elif page == "🏖️ Leave":

    leave_page()


# -------------------------------
# SALARY
# -------------------------------

elif page == "💰 Salary":

    salary_page()


# -------------------------------
# PERFORMANCE
# -------------------------------

elif page == "⭐ Performance":

    performance_page()


# -------------------------------
# REPORTS
# -------------------------------

elif page == "📊 Reports":

    reports_page()