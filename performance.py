import streamlit as st
import pandas as pd
from database import get_connection


def performance_page():

    st.header("⭐ Employee Performance Management")

    tab1, tab2 = st.tabs([
        "⭐ Add Performance Review",
        "📊 Performance Reports"
    ])

    # =====================================================
    # TAB 1 - ADD PERFORMANCE
    # =====================================================

    with tab1:

        conn = get_connection()

        employee_rows = conn.execute("""
            SELECT
                employee_code,
                name,
                department
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
                row["department"]
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
            f"{code} - {name} ({department})"
            for code, name, department in employees
        ]

        selected_employee = st.selectbox(
            "👨‍💼 Select Employee",
            employee_options,
            key="performance_employee"
        )

        # Get selected employee index
        selected_index = employee_options.index(
            selected_employee
        )

        selected_code = employees[
            selected_index
        ][0]

        selected_name = employees[
            selected_index
        ][1]

        selected_department = employees[
            selected_index
        ][2]

        st.success(
            f"Employee: **{selected_name}**"
        )

        st.info(
            f"Department: **{selected_department}** | "
            f"Employee ID: **{selected_code}**"
        )

        st.divider()

        # ---------------------------------------------
        # Review Date
        # ---------------------------------------------

        review_date = st.date_input(
            "📅 Review Date",
            key="performance_date"
        )

        # ---------------------------------------------
        # Performance Rating
        # ---------------------------------------------

        st.subheader(
            "⭐ Performance Rating"
        )

        rating = st.slider(
            "Rate Employee Performance",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.1,
            key="performance_rating"
        )

        # Rating description
        if rating >= 4.5:

            st.success(
                "🏆 Excellent Performance"
            )

        elif rating >= 3.5:

            st.info(
                "👍 Good Performance"
            )

        elif rating >= 2.5:

            st.warning(
                "⚠️ Average Performance"
            )

        else:

            st.error(
                "❗ Needs Improvement"
            )

        # ---------------------------------------------
        # Performance Categories
        # ---------------------------------------------

        st.subheader(
            "📋 Performance Categories"
        )

        col1, col2 = st.columns(2)

        with col1:

            productivity = st.slider(
                "Productivity",
                1,
                5,
                4,
                key="productivity"
            )

            teamwork = st.slider(
                "Teamwork",
                1,
                5,
                4,
                key="teamwork"
            )

            communication = st.slider(
                "Communication",
                1,
                5,
                4,
                key="communication"
            )

        with col2:

            punctuality = st.slider(
                "Punctuality",
                1,
                5,
                4,
                key="punctuality"
            )

            leadership = st.slider(
                "Leadership",
                1,
                5,
                3,
                key="leadership"
            )

            technical_skills = st.slider(
                "Technical Skills",
                1,
                5,
                4,
                key="technical_skills"
            )

        # ---------------------------------------------
        # Automatic Average
        # ---------------------------------------------

        average_rating = round(
            (
                productivity
                + teamwork
                + communication
                + punctuality
                + leadership
                + technical_skills
            ) / 6,
            2
        )

        st.divider()

        st.metric(
            "📊 Category Average",
            f"{average_rating} / 5"
        )

        # ---------------------------------------------
        # Remarks
        # ---------------------------------------------

        remarks = st.text_area(
            "📝 Manager Remarks",
            placeholder=(
                "Enter employee performance feedback..."
            ),
            key="performance_remarks"
        )

        # ---------------------------------------------
        # Save
        # ---------------------------------------------

        if st.button(
            "💾 Save Performance Review",
            use_container_width=True
        ):

            if not remarks.strip():

                st.warning(
                    "⚠️ Please enter manager remarks."
                )

            else:

                conn = get_connection()

                try:

                    # Save performance record
                    conn.execute("""
                        INSERT INTO performance
                        (
                            employee_code,
                            review_date,
                            rating,
                            remarks
                        )
                        VALUES (?, ?, ?, ?)
                    """, (
                        selected_code,
                        str(review_date),
                        rating,
                        remarks.strip()
                    ))

                    # Update employee's current rating
                    conn.execute("""
                        UPDATE employees
                        SET performance_rating = ?
                        WHERE employee_code = ?
                    """, (
                        rating,
                        selected_code
                    ))

                    conn.commit()

                    st.success(
                        "✅ Performance review saved successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Database Error: {e}"
                    )

                finally:

                    conn.close()


    # =====================================================
    # TAB 2 - PERFORMANCE REPORT
    # =====================================================

    with tab2:

        conn = get_connection()

        df = pd.read_sql_query("""
            SELECT
                performance.id,
                performance.employee_code,
                employees.name,
                employees.department,
                employees.designation,
                performance.review_date,
                performance.rating,
                performance.remarks
            FROM performance
            LEFT JOIN employees
            ON performance.employee_code =
               employees.employee_code
            ORDER BY performance.id DESC
        """, conn)

        conn.close()

        if df.empty:

            st.info(
                "📭 No performance records found."
            )

        else:

            # ---------------------------------------------
            # Filters
            # ---------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                search = st.text_input(
                    "🔎 Search Employee",
                    key="performance_search"
                )

            with col2:

                department_filter = st.selectbox(
                    "🏢 Department",
                    ["All"] +
                    sorted(
                        df["department"]
                        .dropna()
                        .unique()
                        .tolist()
                    ),
                    key="performance_department"
                )

            # ---------------------------------------------
            # Search
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
            # Department
            # ---------------------------------------------

            if department_filter != "All":

                df = df[
                    df["department"]
                    == department_filter
                ]

            # ---------------------------------------------
            # Statistics
            # ---------------------------------------------

            total_reviews = len(df)

            average_rating = (
                df["rating"].mean()
                if not df.empty
                else 0
            )

            excellent = len(
                df[df["rating"] >= 4.5]
            )

            needs_improvement = len(
                df[df["rating"] < 2.5]
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "📊 Reviews",
                total_reviews
            )

            col2.metric(
                "⭐ Average Rating",
                f"{average_rating:.2f}"
            )

            col3.metric(
                "🏆 Excellent",
                excellent
            )

            col4.metric(
                "⚠️ Needs Improvement",
                needs_improvement
            )

            st.divider()

            # ---------------------------------------------
            # Performance Chart
            # ---------------------------------------------

            st.subheader(
                "📈 Rating Distribution"
            )

            rating_chart = (
                df["rating"]
                .value_counts()
                .sort_index()
            )

            st.bar_chart(
                rating_chart
            )

            st.divider()

            # ---------------------------------------------
            # Department Performance
            # ---------------------------------------------

            st.subheader(
                "🏢 Department-wise Performance"
            )

            department_rating = (
                df.groupby("department")
                ["rating"]
                .mean()
                .sort_values(
                    ascending=False
                )
            )

            st.bar_chart(
                department_rating
            )

            st.divider()

            # ---------------------------------------------
            # Performance Table
            # ---------------------------------------------

            st.subheader(
                "📋 Performance Records"
            )

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
                "📥 Download Performance Report",
                csv,
                "performance_report.csv",
                "text/csv",
                use_container_width=True
            )
