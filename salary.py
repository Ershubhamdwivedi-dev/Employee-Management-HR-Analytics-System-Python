import streamlit as st
import pandas as pd
from database import get_connection


def salary_page():

    st.header("💰 Salary Management")

    tab1, tab2 = st.tabs([
        "💵 Generate Salary",
        "📊 Salary Records"
    ])

    # =====================================================
    # TAB 1 - GENERATE SALARY
    # =====================================================

    with tab1:

        conn = get_connection()

        employee_rows = conn.execute("""
            SELECT
                employee_code,
                name,
                salary
            FROM employees
            WHERE status = 'Active'
            ORDER BY name
        """).fetchall()

        conn.close()

        # IMPORTANT:
        # Convert sqlite3.Row into normal Python tuples
        employees = [
            (
                row["employee_code"],
                row["name"],
                row["salary"]
            )
            for row in employee_rows
        ]

        if not employees:

            st.warning(
                "⚠️ No active employees found."
            )

            st.info(
                "Please add an employee first."
            )

            return

        # ---------------------------------------------
        # Employee Dropdown
        # ---------------------------------------------

        employee_options = [
            f"{code} - {name}"
            for code, name, salary in employees
        ]

        selected_employee = st.selectbox(
            "👨‍💼 Select Employee",
            employee_options,
            key="salary_employee"
        )

        # Find selected employee
        selected_index = employee_options.index(
            selected_employee
        )

        selected_code = employees[
            selected_index
        ][0]

        selected_name = employees[
            selected_index
        ][1]

        selected_salary = employees[
            selected_index
        ][2]

        st.success(
            f"Selected Employee: **{selected_name}**"
        )

        st.divider()

        # ---------------------------------------------
        # Salary Month
        # ---------------------------------------------

        month = st.text_input(
            "📅 Salary Month",
            value="August 2026",
            key="salary_month"
        )

        # ---------------------------------------------
        # Salary Components
        # ---------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            basic_salary = st.number_input(
                "💵 Basic Salary",
                min_value=0.0,
                value=float(selected_salary or 0),
                step=1000.0,
                key="basic_salary"
            )

        with col2:

            allowance = st.number_input(
                "➕ Allowance",
                min_value=0.0,
                value=5000.0,
                step=500.0,
                key="salary_allowance"
            )

        col3, col4 = st.columns(2)

        with col3:

            deduction = st.number_input(
                "➖ Deduction",
                min_value=0.0,
                value=1000.0,
                step=500.0,
                key="salary_deduction"
            )

        with col4:

            payment_status = st.selectbox(
                "💳 Payment Status",
                [
                    "Pending",
                    "Paid"
                ],
                key="payment_status"
            )

        # ---------------------------------------------
        # Calculate Net Salary
        # ---------------------------------------------

        net_salary = (
            basic_salary
            + allowance
            - deduction
        )

        st.divider()

        st.subheader(
            "💰 Salary Summary"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Basic Salary",
            f"₹{basic_salary:,.2f}"
        )

        col2.metric(
            "Allowance",
            f"₹{allowance:,.2f}"
        )

        col3.metric(
            "Deduction",
            f"₹{deduction:,.2f}"
        )

        col4.metric(
            "Net Salary",
            f"₹{net_salary:,.2f}"
        )

        st.divider()

        # ---------------------------------------------
        # Generate Salary
        # ---------------------------------------------

        if st.button(
            "💾 Generate Salary",
            use_container_width=True
        ):

            if not month.strip():

                st.warning(
                    "⚠️ Please enter salary month."
                )

            else:

                conn = get_connection()

                try:

                    # Check duplicate salary
                    existing = conn.execute("""
                        SELECT id
                        FROM salaries
                        WHERE employee_code = ?
                        AND month = ?
                    """, (
                        selected_code,
                        month.strip()
                    )).fetchone()

                    if existing:

                        st.warning(
                            "⚠️ Salary for this employee "
                            "and month already exists."
                        )

                    else:

                        conn.execute("""
                            INSERT INTO salaries
                            (
                                employee_code,
                                month,
                                basic_salary,
                                allowance,
                                deduction,
                                net_salary,
                                payment_status
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            selected_code,
                            month.strip(),
                            basic_salary,
                            allowance,
                            deduction,
                            net_salary,
                            payment_status
                        ))

                        conn.commit()

                        st.success(
                            "✅ Salary generated successfully!"
                        )

                except Exception as e:

                    st.error(
                        f"❌ Database Error: {e}"
                    )

                finally:

                    conn.close()


    # =====================================================
    # TAB 2 - SALARY RECORDS
    # =====================================================

    with tab2:

        conn = get_connection()

        df = pd.read_sql_query("""
            SELECT
                salaries.id,
                salaries.employee_code,
                employees.name,
                employees.department,
                salaries.month,
                salaries.basic_salary,
                salaries.allowance,
                salaries.deduction,
                salaries.net_salary,
                salaries.payment_status
            FROM salaries
            LEFT JOIN employees
            ON salaries.employee_code =
               employees.employee_code
            ORDER BY salaries.id DESC
        """, conn)

        conn.close()

        if df.empty:

            st.info(
                "📭 No salary records found."
            )

        else:

            # ---------------------------------------------
            # Filters
            # ---------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                search = st.text_input(
                    "🔎 Search Employee",
                    key="salary_search"
                )

            with col2:

                status_filter = st.selectbox(
                    "💳 Payment Status",
                    [
                        "All",
                        "Paid",
                        "Pending"
                    ],
                    key="salary_status_filter"
                )

            with col3:

                department_filter = st.selectbox(
                    "🏢 Department",
                    ["All"] +
                    sorted(
                        df["department"]
                        .dropna()
                        .unique()
                        .tolist()
                    ),
                    key="salary_department_filter"
                )

            # ---------------------------------------------
            # Search Filter
            # ---------------------------------------------

            if search:

                df = df[
                    df["name"]
                    .fillna("")
                    .str.contains(
                        search,
                        case=False,
                        na=False
                    )
                ]

            # ---------------------------------------------
            # Status Filter
            # ---------------------------------------------

            if status_filter != "All":

                df = df[
                    df["payment_status"]
                    == status_filter
                ]

            # ---------------------------------------------
            # Department Filter
            # ---------------------------------------------

            if department_filter != "All":

                df = df[
                    df["department"]
                    == department_filter
                ]

            # ---------------------------------------------
            # Salary Statistics
            # ---------------------------------------------

            total_salary = df["net_salary"].sum()

            paid_salary = df[
                df["payment_status"] == "Paid"
            ]["net_salary"].sum()

            pending_salary = df[
                df["payment_status"] == "Pending"
            ]["net_salary"].sum()

            total_records = len(df)

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "📊 Records",
                total_records
            )

            col2.metric(
                "💰 Total Salary",
                f"₹{total_salary:,.0f}"
            )

            col3.metric(
                "✅ Paid",
                f"₹{paid_salary:,.0f}"
            )

            col4.metric(
                "⏳ Pending",
                f"₹{pending_salary:,.0f}"
            )

            st.divider()

            # ---------------------------------------------
            # Salary Table
            # ---------------------------------------------

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # ---------------------------------------------
            # CSV Download
            # ---------------------------------------------

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "📥 Download Salary Report",
                csv,
                "salary_report.csv",
                "text/csv",
                use_container_width=True
            )
