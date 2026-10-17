
from flask import Flask, render_template, request, redirect, url_for, flash # pyright: ignore[reportMissingImports]
import mysql.connector  # pyright: ignore[reportMissingImports]
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("DB_PASSWORD", "password"),
        database="employee_db"
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        department = request.form.get("department", "").strip()
        phone = request.form.get("phone", "").strip()

        if not all([name, email, department, phone]):
            flash("All fields are required.", "danger")
            return redirect(url_for("index"))

        if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,99}", name):
            flash("Please enter a valid name.", "danger")
            return redirect(url_for("index"))

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email.", "danger")
            return redirect(url_for("index"))

        if not re.fullmatch(r"[0-9+() -]{7,15}", phone):
            flash("Please enter a valid phone number.", "danger")
            return redirect(url_for("index"))

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO employees
                   (name, email, department, phone)
                   VALUES (%s, %s, %s, %s)""",
                (name, email, department, phone)
            )
            conn.commit()
            flash("Employee registered successfully!", "success")
        except mysql.connector.IntegrityError:
            flash("This email is already registered.", "danger")
        except mysql.connector.Error:
            app.logger.exception("Database operation failed")
            flash("Database error. Check your MySQL settings.", "danger")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

        return redirect(url_for("index"))

    employees = []
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees ORDER BY id DESC")
        employees = cursor.fetchall()
    except mysql.connector.Error:
        app.logger.exception("Could not load employees")
        flash("Cannot connect to database. Check your settings.", "danger")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    return render_template("index.html", employees=employees)


@app.route("/delete/<int:employee_id>", methods=["POST"])
def delete_employee(employee_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM employees WHERE id = %s", (employee_id,)
        )
        conn.commit()
        flash("Employee deleted successfully.", "success")
    except mysql.connector.Error:
        app.logger.exception("Could not delete employee")
        flash("Unable to delete employee.", "danger")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
