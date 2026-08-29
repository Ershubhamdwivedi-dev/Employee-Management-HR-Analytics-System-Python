import streamlit as st
import pandas as pd
from database import get_connection


def reports_page():

    st.header("📊 Reports & Analytics")

    conn = get_connection()

    employee_df = pd.read_sql_query(
        "SELECT * FROM employees",
        conn
    )

    salary_df = pd.read_sql_query(
        "SELECT * FROM salaries",
        conn
    )

    attendance_df = pd.read_sql_query(
        "SELECT * FROM attendance",
        conn
    )

    conn.close()

    st.subheader(
        "Department Distribution"
    )

    department_count = (
        employee_df
        ["department"]
        .value_counts()
    )

    st.bar_chart(
        department_count
    )

    st.subheader(
        "Average Salary by Department"
    )

    salary_chart = (
        employee_df
        .groupby("department")["salary"]
        .mean()
    )

    st.bar_chart(
        salary_chart
    )

    st.subheader(
        "Attendance Status"
    )

    attendance_chart = (
        attendance_df
        ["status"]
        .value_counts()
    )

    st.bar_chart(
        attendance_chart
    )

    st.subheader(
        "Employee Performance"
    )

    performance_chart = (
        employee_df
        .groupby("department")
        ["performance_rating"]
        .mean()
    )

    st.bar_chart(
        performance_chart
    )

    st.divider()

    st.subheader(
        "Download Reports"
    )

    employee_csv = employee_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Employee CSV",
        employee_csv,
        "employees.csv",
        "text/csv"
    )

    salary_csv = salary_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Salary CSV",
        salary_csv,
        "salary.csv",
        "text/csv"
    )