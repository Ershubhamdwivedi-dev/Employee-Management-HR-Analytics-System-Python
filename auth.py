import streamlit as st
from database import get_connection


def login_page():

    st.title("🔐 SmartHR Authentication")

    tab1, tab2 = st.tabs([
        "🔑 Login",
        "📝 Registration"
    ])

    # ==========================================
    # LOGIN
    # ==========================================

    with tab1:

        st.subheader("Login to SmartHR")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True
        ):

            if not username or not password:

                st.warning(
                    "Please enter username and password."
                )

            else:

                conn = get_connection()

                user = conn.execute("""
                    SELECT *
                    FROM admins
                    WHERE username = ?
                    AND password = ?
                """, (
                    username,
                    password
                )).fetchone()

                conn.close()

                if user:

                    st.session_state.logged_in = True
                    st.session_state.username = username

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Invalid username or password."
                    )


    # ==========================================
    # REGISTRATION
    # ==========================================

    with tab2:

        st.subheader("Create New Account")

        new_username = st.text_input(
            "Create Username",
            key="register_username"
        )

        new_password = st.text_input(
            "Create Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "📝 Register",
            use_container_width=True
        ):

            if not new_username or not new_password:

                st.warning(
                    "Please fill all required fields."
                )

            elif len(new_username) < 4:

                st.warning(
                    "Username must contain at least 4 characters."
                )

            elif len(new_password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            elif new_password != confirm_password:

                st.error(
                    "❌ Passwords do not match."
                )

            else:

                conn = get_connection()

                existing_user = conn.execute("""
                    SELECT *
                    FROM admins
                    WHERE username = ?
                """, (
                    new_username,
                )).fetchone()

                if existing_user:

                    st.error(
                        "❌ Username already exists."
                    )

                else:

                    conn.execute("""
                        INSERT INTO admins
                        (
                            username,
                            password
                        )
                        VALUES (?, ?)
                    """, (
                        new_username,
                        new_password
                    ))

                    conn.commit()

                    st.success(
                        "✅ Registration successful! "
                        "You can now login."
                    )

                conn.close()


def login():
    login_page()