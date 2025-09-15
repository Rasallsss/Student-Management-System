from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "dev-secret-key"

# ---- configure your DB connection ----
DB_CONFIG = {
    "host": "localhost",      # or "localhost"
    "user": "root",
    "password": "",           # if you have a password, put it here
    "database": "student_db",
    "port": 3306
}

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print("DB connection error:", e)
        return None

# --------------- ROUTES ---------------

@app.route("/")
def index():
    conn = get_connection()
    students = []
    if conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM students ORDER BY id DESC")
        students = cur.fetchall()
        cur.close()
        conn.close()
    return render_template("index.html", students=students)

@app.route("/view/<int:student_id>")
def view_student(student_id):
    conn = get_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for("index"))

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()
    cur.close()
    conn.close()

    if not student:
        flash("Student not found.", "warning")
        return redirect(url_for("index"))

    return render_template("view.html", student=student)



@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age") or None
        course = request.form.get("course", "").strip()
        grade = request.form.get("grade", "").strip()

        if not name:
            flash("Name is required.", "danger")
            return redirect(url_for("add_student"))

        conn = get_connection()
        if conn:
            cur = conn.cursor()
            sql = "INSERT INTO students (name, age, course, grade) VALUES (%s, %s, %s, %s)"
            cur.execute(sql, (name, age, course, grade))
            conn.commit()
            cur.close()
            conn.close()
            flash("Student added successfully.", "success")
        else:
            flash("Database connection failed.", "danger")

        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for("index"))

    cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age") or None
        course = request.form.get("course", "").strip()
        grade = request.form.get("grade", "").strip()

        if not name:
            flash("Name is required.", "danger")
            return redirect(url_for("edit_student", student_id=student_id))

        sql = "UPDATE students SET name=%s, age=%s, course=%s, grade=%s WHERE id=%s"
        cur2 = conn.cursor()
        cur2.execute(sql, (name, age, course, grade, student_id))
        conn.commit()
        cur2.close()
        flash("Student updated.", "success")
        cur.close()
        conn.close()
        return redirect(url_for("index"))

    # GET -> fetch student
    cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cur.fetchone()
    cur.close()
    conn.close()
    if not student:
        flash("Student not found.", "warning")
        return redirect(url_for("index"))
    return render_template("edit.html", student=student)


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Student deleted.", "success")
    else:
        flash("Database connection failed.", "danger")
    return redirect(url_for("index"))


# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
