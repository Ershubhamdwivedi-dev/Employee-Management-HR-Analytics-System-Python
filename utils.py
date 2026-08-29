import streamlit as st


def apply_custom_css():

    st.markdown("""
    <style>

    /* ================================
       MAIN APP
    ================================= */

    .stApp {
        background: #f5f7fb;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* ================================
       SIDEBAR
    ================================= */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #111827 0%,
            #1f2937 100%
        );
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    section[data-testid="stSidebar"] .stRadio label {
        padding: 10px;
        border-radius: 8px;
    }


    /* ================================
       HEADINGS
    ================================= */

    h1 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }

    h2 {
        font-weight: 700 !important;
    }

    h3 {
        font-weight: 600 !important;
    }


    /* ================================
       METRIC CARDS
    ================================= */

    div[data-testid="stMetric"] {

        background: white;

        border-radius: 15px;

        padding: 20px;

        border: 1px solid #e5e7eb;

        box-shadow:
            0 4px 15px rgba(0, 0, 0, 0.05);

    }

    div[data-testid="stMetricLabel"] {
        color: #6b7280;
    }

    div[data-testid="stMetricValue"] {
        font-weight: 700;
    }


    /* ================================
       BUTTONS
    ================================= */

    .stButton > button {

        border-radius: 9px;

        font-weight: 600;

        border: none;

        padding: 0.65rem 1rem;

        transition: 0.2s;

    }

    .stButton > button:hover {

        transform: translateY(-1px);

        box-shadow:
            0 5px 15px rgba(0,0,0,0.12);

    }


    /* ================================
       DATAFRAME
    ================================= */

    div[data-testid="stDataFrame"] {

        border-radius: 12px;

        overflow: hidden;

        border: 1px solid #e5e7eb;

    }


    /* ================================
       INPUTS
    ================================= */

    div[data-baseweb="input"] {

        border-radius: 8px;

    }

    div[data-baseweb="select"] {

        border-radius: 8px;

    }


    /* ================================
       CUSTOM CARDS
    ================================= */

    .dashboard-card {

        background: white;

        padding: 22px;

        border-radius: 15px;

        border: 1px solid #e5e7eb;

        box-shadow:
            0 4px 15px rgba(0,0,0,0.05);

        margin-bottom: 15px;

    }

    .dashboard-card h3 {

        margin-top: 0;

    }


    /* ================================
       HERO
    ================================= */

    .hero {

        background: linear-gradient(
            135deg,
            #111827,
            #374151
        );

        padding: 30px;

        border-radius: 18px;

        color: white;

        margin-bottom: 25px;

    }

    .hero h1 {

        color: white;

        margin-bottom: 5px;

    }

    .hero p {

        color: #d1d5db;

        margin-bottom: 0;

    }


    /* ================================
       STATUS
    ================================= */

    .status-active {

        background: #dcfce7;

        color: #166534;

        padding: 5px 10px;

        border-radius: 20px;

    }


    /* ================================
       FOOTER
    ================================= */

    .footer {

        text-align: center;

        color: #9ca3af;

        padding: 30px;

        margin-top: 40px;

        border-top: 1px solid #e5e7eb;

    }

    </style>
    """, unsafe_allow_html=True)


def page_header(title, subtitle=""):

    st.markdown(
        f"""
        <div style="margin-bottom:25px;">
            <h1>{title}</h1>
            <p style="
                color:#6b7280;
                font-size:1rem;
            ">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def footer():

    st.markdown(
        """
        <div class="footer">
            SmartHR — Employee Management & HR Analytics System
            <br>
            Built with Python & Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )
