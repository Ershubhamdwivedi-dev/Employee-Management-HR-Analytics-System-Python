import streamlit as st
import pandas as pd
from database import get_connection


def attendance_page():

    st.header("📅 Attendance Management")

    tab1, tab2 = st.tabs([
        "➕ Mark Attendance",
        "📊 Attendance Report"
    ])

    # =====================================================
    # TAB 1 - MARK ATTENDANCE
    # =====================================================

    with tab1:

        conn = get_connection()

        employee_rows = conn.execute("""
            SELECT employee_code, name
            FROM employees
            WHERE status = 'Active'
            ORDER BY name
        """).fetchall()

        conn.close()

        # Convert sqlite3.Row into normal Python tuples
        employees = [
            (
                row["employee_code"],
                row["name"]
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

        # Create readable employee names
        employee_options = [
            f"{code} - {name}"
            for code, name in employees
        ]

        selected_employee = st.selectbox(
            "👨‍💼 Select Employee",
            employee_options,
            key="attendance_employee"
        )

        # Get selected employee code
        selected_code = selected_employee.split(" - ")[0]

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            attendance_date = st.date_input(
                "📅 Attendance Date",
                key="attendance_date"
            )

        with col2:

            status = st.selectbox(
                "📌 Attendance Status",
                [
                    "Present",
                    "Absent",
                    "Leave"
                ],
                key="attendance_status"
            )

        col3, col4 = st.columns(2)

        with col3:

            check_in = st.time_input(
                "🕘 Check In",
                key="check_in"
            )

        with col4:

            check_out = st.time_input(
                "🕕 Check Out",
                key="check_out"
            )

        st.divider()

        if st.button(
            "💾 Save Attendance",
            use_container_width=True
        ):

            conn = get_connection()

            try:

                # Check whether attendance already exists
                existing = conn.execute("""
                    SELECT id
                    FROM attendance
                    WHERE employee_code = ?
                    AND attendance_date = ?
                """, (
                    selected_code,
                    str(attendance_date)
                )).fetchone()

                if existing:

                    st.warning(
                        "⚠️ Attendance already exists "
                        "for this employee on this date."
                    )

                else:

                    conn.execute("""
                        INSERT INTO attendance
                        (
                            employee_code,
                            attendance_date,
                            status,
                            check_in,
                            check_out
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        selected_code,
                        str(attendance_date),
                        status,
                        str(check_in)
                        if status == "Present"
                        else None,
                        str(check_out)
                        if status == "Present"
                        else None
                    ))

                    conn.commit()

                    st.success(
                        "✅ Attendance saved successfully!"
                    )

            except Exception as e:

                st.error(
                    f"❌ Database Error: {e}"
                )

            finally:

                conn.close()


    # =====================================================
    # TAB 2 - ATTENDANCE REPORT
    # =====================================================

    with tab2:

        conn = get_connection()

        df = pd.read_sql_query("""
            SELECT
                attendance.id,
                attendance.employee_code,
                employees.name,
                employees.department,
                attendance.attendance_date,
                attendance.status,
                attendance.check_in,
                attendance.check_out
            FROM attendance
            LEFT JOIN employees
            ON attendance.employee_code =
               employees.employee_code
            ORDER BY attendance.attendance_date DESC
        """, conn)

        conn.close()

        if df.empty:

            st.info(
                "No attendance records found."
            )

        else:

            # ---------------------------------------------
            # Filters
            # ---------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                search = st.text_input(
                    "🔎 Search Employee"
                )

            with col2:

                status_filter = st.selectbox(
                    "📌 Status",
                    [
                        "All",
                        "Present",
                        "Absent",
                        "Leave"
                    ]
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
                    )
                )

            # ---------------------------------------------
            # Apply Search
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
            # Apply Status Filter
            # ---------------------------------------------

            if status_filter != "All":

                df = df[
                    df["status"] ==
                    status_filter
                ]

            # ---------------------------------------------
            # Apply Department Filter
            # ---------------------------------------------

            if department_filter != "All":

                df = df[
                    df["department"] ==
                    department_filter
                ]

            # ---------------------------------------------
            # Statistics
            # ---------------------------------------------

            total = len(df)

            present = len(
                df[df["status"] == "Present"]
            )

            absent = len(
                df[df["status"] == "Absent"]
            )

            leave = len(
                df[df["status"] == "Leave"]
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "📊 Total",
                total
            )

            col2.metric(
                "✅ Present",
                present
            )

            col3.metric(
                "❌ Absent",
                absent
            )

            col4.metric(
                "🏖️ Leave",
                leave
            )

            st.divider()

            # ---------------------------------------------
            # Data Table
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
                "📥 Download Attendance CSV",
                csv,
                "attendance_report.csv",
                "text/csv",
                use_container_width=True
            )
