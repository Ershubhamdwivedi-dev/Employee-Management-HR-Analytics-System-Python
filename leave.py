
import streamlit as st
import pandas as pd
from database import get_connection


def leave_page():

    st.header("🏖️ Leave Management")

    tab1, tab2 = st.tabs([
        "➕ Apply Leave",
        "📊 Leave Requests"
    ])

    # =====================================================
    # TAB 1 - APPLY LEAVE
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

        # IMPORTANT:
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

        # ---------------------------------------------
        # Employee Dropdown
        # ---------------------------------------------

        employee_options = [
            f"{code} - {name}"
            for code, name in employees
        ]

        selected_employee = st.selectbox(
            "👨‍💼 Select Employee",
            employee_options,
            key="leave_employee"
        )

        # Employee code
        selected_code = selected_employee.split(
            " - "
        )[0]

        st.divider()

        # ---------------------------------------------
        # Leave Type
        # ---------------------------------------------

        leave_type = st.selectbox(
            "🏖️ Leave Type",
            [
                "Casual Leave",
                "Sick Leave",
                "Earned Leave",
                "Emergency Leave",
                "Maternity Leave",
                "Paternity Leave"
            ],
            key="leave_type"
        )

        # ---------------------------------------------
        # Dates
        # ---------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            start_date = st.date_input(
                "📅 Start Date",
                key="leave_start_date"
            )

        with col2:

            end_date = st.date_input(
                "📅 End Date",
                key="leave_end_date"
            )

        # ---------------------------------------------
        # Reason
        # ---------------------------------------------

        reason = st.text_area(
            "📝 Reason",
            placeholder="Enter leave reason...",
            key="leave_reason"
        )

        st.divider()

        # ---------------------------------------------
        # Submit
        # ---------------------------------------------

        if st.button(
            "📤 Submit Leave Request",
            use_container_width=True
        ):

            # Validate dates
            if end_date < start_date:

                st.error(
                    "❌ End date cannot be before start date."
                )

            elif not reason.strip():

                st.warning(
                    "⚠️ Please enter a leave reason."
                )

            else:

                conn = get_connection()

                try:

                    conn.execute("""
                        INSERT INTO leaves
                        (
                            employee_code,
                            leave_type,
                            start_date,
                            end_date,
                            reason,
                            status
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        selected_code,
                        leave_type,
                        str(start_date),
                        str(end_date),
                        reason.strip(),
                        "Pending"
                    ))

                    conn.commit()

                    st.success(
                        "✅ Leave request submitted successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Database Error: {e}"
                    )

                finally:

                    conn.close()


    # =====================================================
    # TAB 2 - LEAVE REQUESTS
    # =====================================================

    with tab2:

        conn = get_connection()

        df = pd.read_sql_query("""
            SELECT
                leaves.id,
                leaves.employee_code,
                employees.name,
                employees.department,
                leaves.leave_type,
                leaves.start_date,
                leaves.end_date,
                leaves.reason,
                leaves.status
            FROM leaves
            LEFT JOIN employees
            ON leaves.employee_code =
               employees.employee_code
            ORDER BY leaves.id DESC
        """, conn)

        conn.close()

        if df.empty:

            st.info(
                "📭 No leave requests found."
            )

        else:

            # ---------------------------------------------
            # Filters
            # ---------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                status_filter = st.selectbox(
                    "📌 Filter by Status",
                    [
                        "All",
                        "Pending",
                        "Approved",
                        "Rejected"
                    ],
                    key="leave_status_filter"
                )

            with col2:

                search = st.text_input(
                    "🔎 Search Employee",
                    key="leave_search"
                )

            # ---------------------------------------------
            # Apply Status Filter
            # ---------------------------------------------

            if status_filter != "All":

                df = df[
                    df["status"] ==
                    status_filter
                ]

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
            # Statistics
            # ---------------------------------------------

            total = len(df)

            pending = len(
                df[df["status"] == "Pending"]
            )

            approved = len(
                df[df["status"] == "Approved"]
            )

            rejected = len(
                df[df["status"] == "Rejected"]
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "📊 Total",
                total
            )

            col2.metric(
                "⏳ Pending",
                pending
            )

            col3.metric(
                "✅ Approved",
                approved
            )

            col4.metric(
                "❌ Rejected",
                rejected
            )

            st.divider()

            # ---------------------------------------------
            # Leave Table
            # ---------------------------------------------

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # ---------------------------------------------
            # Approve / Reject
            # ---------------------------------------------

            st.subheader(
                "⚙️ Manage Leave Request"
            )

            conn = get_connection()

            request_rows = conn.execute("""
                SELECT
                    leaves.id,
                    leaves.employee_code,
                    employees.name,
                    leaves.leave_type,
                    leaves.start_date,
                    leaves.end_date,
                    leaves.status
                FROM leaves
                LEFT JOIN employees
                ON leaves.employee_code =
                   employees.employee_code
                WHERE leaves.status = 'Pending'
                ORDER BY leaves.id DESC
            """).fetchall()

            conn.close()

            # Convert sqlite3.Row to tuples
            requests = [
                (
                    row["id"],
                    row["employee_code"],
                    row["name"],
                    row["leave_type"],
                    row["start_date"],
                    row["end_date"],
                    row["status"]
                )
                for row in request_rows
            ]

            if requests:

                request_options = [
                    (
                        f"#{request_id} | "
                        f"{code} | "
                        f"{name} | "
                        f"{leave_type} | "
                        f"{start_date} → {end_date}"
                    )
                    for (
                        request_id,
                        code,
                        name,
                        leave_type,
                        start_date,
                        end_date,
                        status
                    ) in requests
                ]

                selected_request = st.selectbox(
                    "Select Pending Request",
                    request_options,
                    key="pending_leave_request"
                )

                selected_index = request_options.index(
                    selected_request
                )

                selected_request_data = requests[
                    selected_index
                ]

                request_id = selected_request_data[0]

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Approve",
                        use_container_width=True
                    ):

                        conn = get_connection()

                        conn.execute("""
                            UPDATE leaves
                            SET status = 'Approved'
                            WHERE id = ?
                        """, (
                            request_id,
                        ))

                        conn.commit()
                        conn.close()

                        st.success(
                            "Leave approved successfully!"
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        "❌ Reject",
                        use_container_width=True
                    ):

                        conn = get_connection()

                        conn.execute("""
                            UPDATE leaves
                            SET status = 'Rejected'
                            WHERE id = ?
                        """, (
                            request_id,
                        ))

                        conn.commit()
                        conn.close()

                        st.warning(
                            "Leave rejected."
                        )

                        st.rerun()

            else:

                st.info(
                    "🎉 No pending leave requests."
                )

            # ---------------------------------------------
            # CSV Download
            # ---------------------------------------------

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "📥 Download Leave Report",
                csv,
                "leave_report.csv",
                "text/csv",
                use_container_width=True
            )
