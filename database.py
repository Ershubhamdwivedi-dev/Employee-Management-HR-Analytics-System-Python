import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)

DB_NAME = DB_DIR / "hr_management.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            gender TEXT,
            dob TEXT,
            department TEXT,
            designation TEXT,
            joining_date TEXT,
            salary REAL,
            city TEXT,
            status TEXT DEFAULT 'Active',
            performance_rating REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT,
            attendance_date TEXT,
            status TEXT,
            check_in TEXT,
            check_out TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT,
            leave_type TEXT,
            start_date TEXT,
            end_date TEXT,
            reason TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT,
            month TEXT,
            basic_salary REAL,
            allowance REAL,
            deduction REAL,
            net_salary REAL,
            payment_status TEXT DEFAULT 'Pending'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT,
            review_date TEXT,
            rating REAL,
            remarks TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO admins(username, password)
        VALUES ('admin', 'admin123')
    """)

    conn.commit()
    conn.close()


def generate_demo_data(count=500):

    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    if existing >= count:
        conn.close()
        return

    first_names = [
        "Rahul", "Amit", "Rohit", "Vikas", "Ankit",
        "Shubham", "Arjun", "Karan", "Piyush", "Mohit",
        "Priya", "Neha", "Pooja", "Anjali", "Sneha",
        "Kavita", "Riya", "Simran", "Nisha", "Aarti"
    ]

    last_names = [
        "Sharma", "Verma", "Singh", "Gupta", "Yadav",
        "Mishra", "Pandey", "Dwivedi", "Kumar", "Jain"
    ]

    departments = {
        "IT": [
            "Python Developer",
            "Software Engineer",
            "Backend Developer",
            "Frontend Developer"
        ],
        "HR": [
            "HR Executive",
            "HR Manager",
            "Recruiter"
        ],
        "Finance": [
            "Accountant",
            "Finance Executive",
            "Financial Analyst"
        ],
        "Marketing": [
            "Marketing Executive",
            "SEO Executive",
            "Marketing Manager"
        ],
        "Sales": [
            "Sales Executive",
            "Sales Manager",
            "Business Development Executive"
        ],
        "Operations": [
            "Operations Executive",
            "Operations Manager"
        ]
    }

    cities = [
        "Lucknow",
        "Delhi",
        "Noida",
        "Mohali",
        "Chandigarh",
        "Gurgaon",
        "Kanpur",
        "Ayodhya",
        "Jaipur",
        "Pune"
    ]

    genders = ["Male", "Female"]

    start_id = existing + 1

    for i in range(start_id, count + 1):

        name = random.choice(first_names) + " " + random.choice(last_names)

        code = f"EMP{i:04d}"

        email = f"employee{i}@smarthr.com"

        phone = "9" + "".join(
            random.choice("0123456789") for _ in range(9)
        )

        gender = random.choice(genders)

        dob = date(
            random.randint(1985, 2002),
            random.randint(1, 12),
            random.randint(1, 28)
        )

        department = random.choice(list(departments.keys()))

        designation = random.choice(
            departments[department]
        )

        joining_date = date(
            random.randint(2018, 2026),
            random.randint(1, 12),
            random.randint(1, 28)
        )

        salary = random.randint(
            18000, 150000
        )

        city = random.choice(cities)

        rating = round(
            random.uniform(2.5, 5.0), 1
        )

        cursor.execute("""
            INSERT INTO employees
            (
                employee_code,
                name,
                email,
                phone,
                gender,
                dob,
                department,
                designation,
                joining_date,
                salary,
                city,
                status,
                performance_rating
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code,
            name,
            email,
            phone,
            gender,
            str(dob),
            department,
            designation,
            str(joining_date),
            salary,
            city,
            "Active",
            rating
        ))

    conn.commit()

    # Attendance data
    employees = cursor.execute(
        "SELECT employee_code FROM employees"
    ).fetchall()

    for emp in employees:

        for day_offset in range(30):

            attendance_date = (
                date.today() -
                timedelta(days=day_offset)
            )

            status = random.choices(
                ["Present", "Absent", "Leave"],
                weights=[85, 8, 7]
            )[0]

            check_in = "09:" + str(
                random.randint(0, 59)
            )

            check_out = "18:" + str(
                random.randint(0, 59)
            )

            cursor.execute("""
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
                emp["employee_code"],
                str(attendance_date),
                status,
                check_in if status == "Present" else None,
                check_out if status == "Present" else None
            ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    generate_demo_data(500)
    print("Database created successfully!")