import os
import sqlite3
from contextlib import closing

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "student-system-secret-key"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_db_connection()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_no TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                major TEXT,
                phone TEXT,
                email TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


@app.route("/")
def home():
    return redirect(url_for("list_students"))


@app.route("/students")
def list_students():
    query = request.args.get("q", "").strip()

    with closing(get_db_connection()) as conn:
        if query:
            like_query = f"%{query}%"
            students = conn.execute(
                """
                SELECT *
                FROM students
                WHERE student_no LIKE ? OR name LIKE ? OR major LIKE ?
                ORDER BY id DESC
                """,
                (like_query, like_query, like_query),
            ).fetchall()
        else:
            students = conn.execute(
                "SELECT * FROM students ORDER BY id DESC"
            ).fetchall()

    return render_template("students.html", students=students, query=query)


def parse_student_form(form: dict) -> tuple[dict, str | None]:
    student_no = form.get("student_no", "").strip()
    name = form.get("name", "").strip()
    gender = form.get("gender", "").strip()
    age_raw = form.get("age", "").strip()
    major = form.get("major", "").strip()
    phone = form.get("phone", "").strip()
    email = form.get("email", "").strip()

    if not student_no:
        return {}, "学号不能为空"
    if not name:
        return {}, "姓名不能为空"

    age = None
    if age_raw:
        if not age_raw.isdigit():
            return {}, "年龄必须是数字"
        age = int(age_raw)
        if age < 1 or age > 120:
            return {}, "年龄范围应在 1 到 120"

    payload = {
        "student_no": student_no,
        "name": name,
        "gender": gender,
        "age": age,
        "major": major,
        "phone": phone,
        "email": email,
    }
    return payload, None


@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        payload, error = parse_student_form(request.form)
        if error:
            flash(error, "danger")
            return render_template("student_form.html", title="新增学生", student=request.form)

        with closing(get_db_connection()) as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO students (student_no, name, gender, age, major, phone, email)
                    VALUES (:student_no, :name, :gender, :age, :major, :phone, :email)
                    """,
                    payload,
                )
                conn.commit()
                flash("新增学生成功", "success")
                return redirect(url_for("list_students"))
            except sqlite3.IntegrityError:
                flash("学号已存在，请使用唯一学号", "danger")

        return render_template("student_form.html", title="新增学生", student=request.form)

    return render_template("student_form.html", title="新增学生", student={})


@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id: int):
    with closing(get_db_connection()) as conn:
        current = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()

        if not current:
            flash("未找到该学生", "warning")
            return redirect(url_for("list_students"))

        if request.method == "POST":
            payload, error = parse_student_form(request.form)
            if error:
                flash(error, "danger")
                return render_template(
                    "student_form.html",
                    title="编辑学生",
                    student=request.form,
                    student_id=student_id,
                )

            payload["id"] = student_id

            try:
                conn.execute(
                    """
                    UPDATE students
                    SET student_no = :student_no,
                        name = :name,
                        gender = :gender,
                        age = :age,
                        major = :major,
                        phone = :phone,
                        email = :email
                    WHERE id = :id
                    """,
                    payload,
                )
                conn.commit()
                flash("修改学生信息成功", "success")
                return redirect(url_for("list_students"))
            except sqlite3.IntegrityError:
                flash("学号已存在，请使用唯一学号", "danger")
                return render_template(
                    "student_form.html",
                    title="编辑学生",
                    student=request.form,
                    student_id=student_id,
                )

    return render_template(
        "student_form.html", title="编辑学生", student=current, student_id=student_id
    )


@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id: int):
    with closing(get_db_connection()) as conn:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

    flash("删除学生成功", "success")
    return redirect(url_for("list_students"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
