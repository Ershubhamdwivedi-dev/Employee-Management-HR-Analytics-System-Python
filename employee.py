import streamlit as st
import pandas as pd
from database import get_connection
from utils import page_header, footer


def employee_page():

    # =====================================================
    # PAGE HEADER
    # =====================================================

    page_header(
        "Employee Management",
        "Manage employee profiles, departments, salaries and employment status."
    )

    # =====================================================
    # LOAD EMPLOYEES
    # =====================================================

    conn = get_connection()

    employee_rows = conn.execute("""
        SELECT
            id,
            employee_code,
            name,
            email,
            phone,
            department,
            designation,
            salary,
            joining_date,
            status,
            performance_rating
        FROM employees
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    # =====================================================
    # IMPORTANT FIX
    # Convert sqlite3.Row -> normal dictionaries
    # =====================================================

    employees = []

    for row in employee_rows:

        employees.append({
            "id": row["id"],
            "employee_code": row["employee_code"],
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
            "department": row["department"],
            "designation": row["designation"],
            "salary": row["salary"],
            "joining_date": row["joining_date"],
            "status": row["status"],
            "performance_rating": row["performance_rating"]
        })

    # =====================================================
    # STATISTICS
    # =====================================================

    total_employees = len(employees)

    active_employees = len([
        e for e in employees
        if e["status"] == "Active"
    ])

    inactive_employees = len([
        e for e in employees
        if e["status"] != "Active"
    ])

    departments = len(set(
        e["department"]
        for e in employees
        if e["department"]
    ))

    # =====================================================
    # METRIC CARDS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "👨‍💼 Total Employees",
        total_employees
    )

    col2.metric(
        "🟢 Active",
        active_employees
    )

    col3.metric(
        "🔴 Inactive",
        inactive_employees
    )

    col4.metric(
        "🏢 Departments",
        departments
    )

    st.write("")

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3 = st.tabs([
        "👥 Employee List",
        "➕ Add Employee",
        "⚙️ Manage Employee"
    ])

    # =====================================================
    # TAB 1 - EMPLOYEE LIST
    # =====================================================

    with tab1:

        st.subheader(
            "👥 All Employees"
        )

        # ---------------------------------------------
        # Search
        # ---------------------------------------------

        search = st.text_input(
            "🔎 Search Employee",
            placeholder="Search by name, employee code, email or department...",
            key="employee_search"
        )

        # ---------------------------------------------
        # Department Filter
        # ---------------------------------------------

        department_list = sorted(
            list(set(
                e["department"]
                for e in employees
                if e["department"]
            ))
        )

        col1, col2 = st.columns(2)

        with col1:

            department_filter = st.selectbox(
                "🏢 Department",
                ["All"] + department_list,
                key="employee_department_filter"
            )

        with col2:

            status_filter = st.selectbox(
                "📌 Status",
                [
                    "All",
                    "Active",
                    "Inactive"
                ],
                key="employee_status_filter"
            )

        # ---------------------------------------------
        # Convert to DataFrame
        # ---------------------------------------------

        df = pd.DataFrame(employees)

        if not df.empty:

            # Search

            if search:

                mask = (
                    df["name"]
                    .fillna("")
                    .str.contains(
                        search,
                        case=False,
                        na=False
                    )
                    |
                    df["employee_code"]
                    .fillna("")
                    .str.contains(
                        search,
                        case=False,
                        na=False
                    )
                    |
                    df["email"]
                    .fillna("")
                    .str.contains(
                        search,
                        case=False,
                        na=False
                    )
                    |
                    df["department"]
                    .fillna("")
                    .str.contains(
                        search,
                        case=False,
                        na=False
                    )
                )

                df = df[mask]

            # Department

            if department_filter != "All":

                df = df[
                    df["department"]
                    == department_filter
                ]

            # Status

            if status_filter != "All":

                df = df[
                    df["status"]
                    == status_filter
                ]

            # -----------------------------------------
            # Display columns
            # -----------------------------------------

            display_columns = [
                "employee_code",
                "name",
                "email",
                "phone",
                "department",
                "designation",
                "salary",
                "joining_date",
                "status",
                "performance_rating"
            ]

            available_columns = [
                col
                for col in display_columns
                if col in df.columns
            ]

            st.dataframe(
                df[available_columns],
                use_container_width=True,
                hide_index=True
            )

            # -----------------------------------------
            # Download
            # -----------------------------------------

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "📥 Download Employee CSV",
                csv,
                "employees.csv",
                "text/csv",
                use_container_width=True
            )

        else:

            st.info(
                "No employees found."
            )

    # =====================================================
    # TAB 2 - ADD EMPLOYEE
    # =====================================================

    with tab2:

        st.subheader(
            "➕ Add New Employee"
        )

        col1, col2 = st.columns(2)

        with col1:

            employee_code = st.text_input(
                "🆔 Employee Code",
                placeholder="EMP0001",
                key="add_employee_code"
            )

            name = st.text_input(
                "👤 Full Name",
                placeholder="Enter employee name",
                key="add_employee_name"
            )

            email = st.text_input(
                "📧 Email",
                placeholder="employee@example.com",
                key="add_employee_email"
            )

            phone = st.text_input(
                "📱 Phone",
                placeholder="9876543210",
                key="add_employee_phone"
            )

        with col2:

            department = st.selectbox(
                "🏢 Department",
                [
                    "IT",
                    "HR",
                    "Finance",
                    "Sales",
                    "Marketing",
                    "Operations",
                    "Support"
                ],
                key="add_department"
            )

            designation = st.text_input(
                "💼 Designation",
                placeholder="Python Developer",
                key="add_designation"
            )

            salary = st.number_input(
                "💰 Salary",
                min_value=0.0,
                value=25000.0,
                step=1000.0,
                key="add_salary"
            )

            joining_date = st.date_input(
                "📅 Joining Date",
                key="add_joining_date"
            )

        st.divider()

        if st.button(
            "➕ Add Employee",
            use_container_width=True,
            key="add_employee_button"
        ):

            if not employee_code.strip():

                st.warning(
                    "⚠️ Employee code is required."
                )

            elif not name.strip():

                st.warning(
                    "⚠️ Employee name is required."
                )

            elif not email.strip():

                st.warning(
                    "⚠️ Email is required."
                )

            elif not designation.strip():

                st.warning(
                    "⚠️ Designation is required."
                )

            else:

                conn = get_connection()

                try:

                    existing = conn.execute("""
                        SELECT id
                        FROM employees
                        WHERE employee_code = ?
                    """, (
                        employee_code.strip(),
                    )).fetchone()

                    if existing:

                        st.error(
                            "❌ Employee code already exists."
                        )

                    else:

                        conn.execute("""
                            INSERT INTO employees
                            (
                                employee_code,
                                name,
                                email,
                                phone,
                                department,
                                designation,
                                salary,
                                joining_date,
                                status,
                                performance_rating
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            employee_code.strip(),
                            name.strip(),
                            email.strip().lower(),
                            phone.strip(),
                            department,
                            designation.strip(),
                            salary,
                            str(joining_date),
                            "Active",
                            0
                        ))

                        conn.commit()

                        st.success(
                            "🎉 Employee added successfully!"
                        )

                        st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Database Error: {e}"
                    )

                finally:

                    conn.close()

    # =====================================================
    # TAB 3 - MANAGE EMPLOYEE
    # =====================================================

    with tab3:

        st.subheader(
            "⚙️ Manage Employee"
        )

        if not employees:

            st.info(
                "No employees available."
            )

        else:

            # =================================================
            # FIX:
            # Only strings are passed to selectbox
            # =================================================

            employee_options = [
                (
                    f"{employee['employee_code']} - "
                    f"{employee['name']}"
                )
                for employee in employees
            ]

            selected = st.selectbox(
                "Select Employee",
                employee_options,
                key="manage_employee"
            )

            # Find selected employee using normal list
            selected_index = employee_options.index(
                selected
            )

            employee = employees[
                selected_index
            ]

            st.divider()

            # =================================================
            # EMPLOYEE DETAILS
            # =================================================

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Employee Code",
                employee["employee_code"]
            )

            col2.metric(
                "Department",
                employee["department"]
            )

            col3.metric(
                "Current Status",
                employee["status"]
            )

            st.divider()

            # =================================================
            # UPDATE
            # =================================================

            st.subheader(
                "✏️ Update Employee"
            )

            col1, col2 = st.columns(2)

            with col1:

                new_name = st.text_input(
                    "Name",
                    value=employee["name"] or "",
                    key="update_name"
                )

                new_email = st.text_input(
                    "Email",
                    value=employee["email"] or "",
                    key="update_email"
                )

                new_phone = st.text_input(
                    "Phone",
                    value=employee["phone"] or "",
                    key="update_phone"
                )

            with col2:

                departments = [
                    "IT",
                    "HR",
                    "Finance",
                    "Sales",
                    "Marketing",
                    "Operations",
                    "Support"
                ]

                current_department = (
                    employee["department"]
                    if employee["department"]
                    in departments
                    else "IT"
                )

                new_department = st.selectbox(
                    "Department",
                    departments,
                    index=departments.index(
                        current_department
                    ),
                    key="update_department"
                )

                new_designation = st.text_input(
                    "Designation",
                    value=employee["designation"] or "",
                    key="update_designation"
                )

                new_salary = st.number_input(
                    "Salary",
                    min_value=0.0,
                    value=float(
                        employee["salary"] or 0
                    ),
                    step=1000.0,
                    key="update_salary"
                )

            new_status = st.selectbox(
                "Status",
                [
                    "Active",
                    "Inactive"
                ],
                index=(
                    0
                    if employee["status"] == "Active"
                    else 1
                ),
                key="update_status"
            )

            st.write("")

            if st.button(
                "💾 Update Employee",
                use_container_width=True,
                key="update_employee_button"
            ):

                conn = get_connection()

                try:

                    conn.execute("""
                        UPDATE employees

                        SET
                            name = ?,
                            email = ?,
                            phone = ?,
                            department = ?,
                            designation = ?,
                            salary = ?,
                            status = ?

                        WHERE employee_code = ?
                    """, (
                        new_name.strip(),
                        new_email.strip().lower(),
                        new_phone.strip(),
                        new_department,
                        new_designation.strip(),
                        new_salary,
                        new_status,
                        employee["employee_code"]
                    ))

                    conn.commit()

                    st.success(
                        "✅ Employee updated successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Update Error: {e}"
                    )

                finally:

                    conn.close()

            st.divider()

            # =================================================
            # DELETE
            # =================================================

            st.subheader(
                "🗑️ Delete Employee"
            )

            st.warning(
                "⚠️ Deleting an employee may affect "
                "related attendance, salary and performance records."
            )

            confirm_delete = st.checkbox(
                "I understand that this action cannot be easily undone.",
                key="confirm_delete"
            )

            if st.button(
                "🗑️ Delete Employee",
                disabled=not confirm_delete,
                use_container_width=True,
                key="delete_employee_button"
            ):

                conn = get_connection()

                try:

                    conn.execute("""
                        DELETE FROM employees
                        WHERE employee_code = ?
                    """, (
                        employee["employee_code"],
                    ))

                    conn.commit()

                    st.success(
                        "✅ Employee deleted successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Delete Error: {e}"
                    )

                finally:

                    conn.close()

    # =====================================================
    # FOOTER
    # =====================================================

    footer()
