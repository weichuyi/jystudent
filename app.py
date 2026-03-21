import os
from datetime import datetime
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "student-system-secret-key-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ======================== 模型定义 ========================

class User(db.Model):
    """用户表：系统用户（管理员、教师、学生）"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")  # admin, teacher, student
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Class(db.Model):
    """班级表"""
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    class_no = db.Column(db.String(50), unique=True, nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    headteacher_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    grade = db.Column(db.String(20))  # 年级
    total_students = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship("Student", backref="class_obj", lazy=True)
    headteacher = db.relationship("User", backref="classes_managed")


class Student(db.Model):
    """学生表：扩展版本"""
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    student_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    major = db.Column(db.String(100))
    status = db.Column(db.String(20), default="enrolled")  # enrolled, leave, return, dropout
    id_number = db.Column(db.String(50), unique=True)
    enrollment_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="student_profile")
    enrollments = db.relationship("Enrollment", backref="student", lazy=True)
    status_changes = db.relationship("StudentStatusChange", backref="student", lazy=True)


class Teacher(db.Model):
    """教师表"""
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    teacher_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    qualification = db.Column(db.String(100))  # 学位
    hire_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="teacher_profile")
    courses = db.relationship("Course", backref="teacher", lazy=True)


class Course(db.Model):
    """课程表"""
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    course_no = db.Column(db.String(50), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Float)  # 学分
    hours = db.Column(db.Integer)  # 学时
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    max_capacity = db.Column(db.Integer, default=50)
    semester = db.Column(db.String(20))  # 学期 如 2024-1
    status = db.Column(db.String(20), default="open")  # open, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship("Enrollment", backref="course", lazy=True)


class Enrollment(db.Model):
    """选课表：学生选课记录"""
    __tablename__ = "enrollments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    score = db.Column(db.Float)
    grade = db.Column(db.String(5))  # 等级 A, B, C, D, F
    status = db.Column(db.String(20), default="enrolled")  # enrolled, withdrawn, completed
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint("student_id", "course_id", name="unique_student_course"),)


class Score(db.Model):
    """成绩表：详细成绩记录"""
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollments.id"), nullable=False)
    score_value = db.Column(db.Float)
    grade = db.Column(db.String(5))
    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"))  # 录入教师
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StudentStatusChange(db.Model):
    """学籍异动表：记录学生休学、复学、退学等"""
    __tablename__ = "student_status_changes"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    change_type = db.Column(db.String(20), nullable=False)  # leave, return, dropout
    reason = db.Column(db.String(255))
    approval_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OperationLog(db.Model):
    """操作日志表"""
    __tablename__ = "operation_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(50))  # 模块名 student, course, score
    record_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ======================== 权限装饰器 ========================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("请先登录", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("请先登录", "warning")
                return redirect(url_for("login"))
            user = User.query.get(session.get("user_id"))
            if user.role not in roles:
                flash("权限不足", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ======================== 数据库初始化 ========================

def init_db():
    with app.app_context():
        db.create_all()
        # 创建默认管理员账户
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                full_name="系统管理员",
                role="admin",
                email="admin@school.com"
            )
            admin.set_password("admin@2024")
            db.session.add(admin)
            db.session.commit()


# ======================== 认证路由 ========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            session["full_name"] = user.full_name

            # 记录登录日志
            log = OperationLog(
                user_id=user.id,
                action="login",
                module="system"
            )
            db.session.add(log)
            db.session.commit()

            flash(f"欢迎 {user.full_name}", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("用户名或密码错误", "danger")

    return render_template("auth/login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("已退出登录", "info")
    return redirect(url_for("login"))


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        user = User.query.get(session["user_id"])
        if not user.check_password(old_password):
            flash("原密码错误", "danger")
        elif new_password != confirm_password:
            flash("两次输入密码不一致", "danger")
        elif len(new_password) < 6:
            flash("密码至少 6 个字符", "danger")
        else:
            user.set_password(new_password)
            db.session.commit()
            flash("密码修改成功", "success")
            return redirect(url_for("dashboard"))

    return render_template("auth/change_password.html")


# ======================== 首页 / 仪表板 ========================

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    
    stats = {
        "total_students": Student.query.count(),
        "total_teachers": Teacher.query.count(),
        "total_courses": Course.query.count(),
        "total_classes": Class.query.count(),
    }

    return render_template("dashboard.html", user=user, stats=stats)


# ======================== 学生管理路由 ========================

@app.route("/students")
@login_required
def list_students():
    query = request.args.get("q", "").strip()
    class_id = request.args.get("class_id", type=int)
    status = request.args.get("status", "").strip()

    q = Student.query

    if query:
        like_query = f"%{query}%"
        q = q.filter(
            db.or_(
                Student.student_no.ilike(like_query),
                Student.name.ilike(like_query),
                Student.major.ilike(like_query)
            )
        )

    if class_id:
        q = q.filter(Student.class_id == class_id)

    if status:
        q = q.filter(Student.status == status)

    students = q.order_by(Student.id.desc()).all()
    classes = Class.query.all()

    return render_template(
        "students/list.html",
        students=students,
        classes=classes,
        query=query,
        class_id=class_id,
        status=status
    )


@app.route("/students/add", methods=["GET", "POST"])
@role_required("admin", "teacher")
def add_student():
    classes = Class.query.all()

    if request.method == "POST":
        student_no = request.form.get("student_no", "").strip()
        name = request.form.get("name", "").strip()
        gender = request.form.get("gender", "").strip()
        age_raw = request.form.get("age", "").strip()
        class_id = request.form.get("class_id", type=int)
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        major = request.form.get("major", "").strip()
        id_number = request.form.get("id_number", "").strip()

        errors = []
        if not student_no:
            errors.append("学号不能为空")
        if not name:
            errors.append("姓名不能为空")
        if age_raw and not age_raw.isdigit():
            errors.append("年龄必须是数字")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("students/form.html", classes=classes, action="add")

        try:
            student = Student(
                student_no=student_no,
                name=name,
                gender=gender,
                age=int(age_raw) if age_raw else None,
                class_id=class_id,
                phone=phone,
                email=email,
                major=major,
                id_number=id_number,
                status="enrolled"
            )
            db.session.add(student)
            db.session.commit()

            # 记录操作日志
            log = OperationLog(
                user_id=session["user_id"],
                action="create",
                module="student",
                record_id=student.id,
                details=f"新增学生 {name}({student_no})"
            )
            db.session.add(log)
            db.session.commit()

            flash("新增学生成功", "success")
            return redirect(url_for("list_students"))
        except Exception as e:
            db.session.rollback()
            flash(f"添加失败：{str(e)}", "danger")

    return render_template("students/form.html", classes=classes, action="add")


@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@role_required("admin", "teacher")
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    classes = Class.query.all()

    if request.method == "POST":
        student.student_no = request.form.get("student_no", "").strip()
        student.name = request.form.get("name", "").strip()
        student.gender = request.form.get("gender", "").strip()
        age_raw = request.form.get("age", "").strip()
        student.age = int(age_raw) if age_raw else None
        student.class_id = request.form.get("class_id", type=int)
        student.phone = request.form.get("phone", "").strip()
        student.email = request.form.get("email", "").strip()
        student.major = request.form.get("major", "").strip()
        student.id_number = request.form.get("id_number", "").strip()

        try:
            db.session.commit()

            log = OperationLog(
                user_id=session["user_id"],
                action="update",
                module="student",
                record_id=student.id,
                details=f"修改学生信息 {student.name}({student.student_no})"
            )
            db.session.add(log)
            db.session.commit()

            flash("修改成功", "success")
            return redirect(url_for("list_students"))
        except Exception as e:
            db.session.rollback()
            flash(f"修改失败：{str(e)}", "danger")

    return render_template("students/form.html", student=student, classes=classes, action="edit")


@app.route("/students/delete/<int:student_id>", methods=["POST"])
@role_required("admin")
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = student.name

    try:
        log = OperationLog(
            user_id=session["user_id"],
            action="delete",
            module="student",
            record_id=student.id,
            details=f"删除学生 {name}({student.student_no})"
        )
        db.session.add(log)
        db.session.delete(student)
        db.session.commit()

        flash("删除成功", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"删除失败：{str(e)}", "danger")

    return redirect(url_for("list_students"))


# ======================== 班级管理路由 ========================

@app.route("/classes")
@login_required
def list_classes():
    classes = Class.query.order_by(Class.id.desc()).all()
    teachers = Teacher.query.all()
    return render_template("classes/list.html", classes=classes, teachers=teachers)


@app.route("/classes/add", methods=["GET", "POST"])
@role_required("admin")
def add_class():
    teachers = Teacher.query.all()

    if request.method == "POST":
        class_no = request.form.get("class_no", "").strip()
        class_name = request.form.get("class_name", "").strip()
        headteacher_id = request.form.get("headteacher_id", type=int)
        grade = request.form.get("grade", "").strip()

        if not class_no or not class_name:
            flash("班级编号和班级名称不能为空", "danger")
            return render_template("classes/form.html", teachers=teachers, action="add")

        try:
            cls = Class(
                class_no=class_no,
                class_name=class_name,
                headteacher_id=headteacher_id,
                grade=grade
            )
            db.session.add(cls)
            db.session.commit()

            log = OperationLog(
                user_id=session["user_id"],
                action="create",
                module="class",
                record_id=cls.id,
                details=f"新增班级 {class_name}"
            )
            db.session.add(log)
            db.session.commit()

            flash("新增班级成功", "success")
            return redirect(url_for("list_classes"))
        except Exception as e:
            db.session.rollback()
            flash(f"添加失败：{str(e)}", "danger")

    return render_template("classes/form.html", teachers=teachers, action="add")


# ======================== 教师管理路由 ========================

@app.route("/teachers")
@login_required
def list_teachers():
    query = request.args.get("q", "").strip()
    q = Teacher.query

    if query:
        like_query = f"%{query}%"
        q = q.filter(
            db.or_(
                Teacher.teacher_no.ilike(like_query),
                Teacher.name.ilike(like_query),
                Teacher.department.ilike(like_query)
            )
        )

    teachers = q.order_by(Teacher.id.desc()).all()
    return render_template("teachers/list.html", teachers=teachers, query=query)


@app.route("/teachers/add", methods=["GET", "POST"])
@role_required("admin")
def add_teacher():
    if request.method == "POST":
        teacher_no = request.form.get("teacher_no", "").strip()
        name = request.form.get("name", "").strip()
        gender = request.form.get("gender", "").strip()
        department = request.form.get("department", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        qualification = request.form.get("qualification", "").strip()

        if not teacher_no or not name:
            flash("教工号和姓名不能为空", "danger")
            return render_template("teachers/form.html", action="add")

        try:
            teacher = Teacher(
                teacher_no=teacher_no,
                name=name,
                gender=gender,
                department=department,
                phone=phone,
                email=email,
                qualification=qualification
            )
            db.session.add(teacher)
            db.session.commit()

            log = OperationLog(
                user_id=session["user_id"],
                action="create",
                module="teacher",
                record_id=teacher.id,
                details=f"新增教师 {name}({teacher_no})"
            )
            db.session.add(log)
            db.session.commit()

            flash("新增教师成功", "success")
            return redirect(url_for("list_teachers"))
        except Exception as e:
            db.session.rollback()
            flash(f"添加失败：{str(e)}", "danger")

    return render_template("teachers/form.html", action="add")


@app.route("/teachers/edit/<int:teacher_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    if request.method == "POST":
        teacher.teacher_no = request.form.get("teacher_no", "").strip()
        teacher.name = request.form.get("name", "").strip()
        teacher.gender = request.form.get("gender", "").strip()
        teacher.department = request.form.get("department", "").strip()
        teacher.phone = request.form.get("phone", "").strip()
        teacher.email = request.form.get("email", "").strip()
        teacher.qualification = request.form.get("qualification", "").strip()

        try:
            db.session.commit()

            log = OperationLog(
                user_id=session["user_id"],
                action="update",
                module="teacher",
                record_id=teacher.id,
                details=f"修改教师信息 {teacher.name}({teacher.teacher_no})"
            )
            db.session.add(log)
            db.session.commit()

            flash("修改成功", "success")
            return redirect(url_for("list_teachers"))
        except Exception as e:
            db.session.rollback()
            flash(f"修改失败：{str(e)}", "danger")

    return render_template("teachers/form.html", teacher=teacher, action="edit")


@app.route("/teachers/delete/<int:teacher_id>", methods=["POST"])
@role_required("admin")
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    name = teacher.name

    try:
        log = OperationLog(
            user_id=session["user_id"],
            action="delete",
            module="teacher",
            record_id=teacher.id,
            details=f"删除教师 {name}({teacher.teacher_no})"
        )
        db.session.add(log)
        db.session.delete(teacher)
        db.session.commit()

        flash("删除成功", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"删除失败：{str(e)}", "danger")

    return redirect(url_for("list_teachers"))


# ======================== 课程管理路由 ========================

@app.route("/courses")
@login_required
def list_courses():
    semester = request.args.get("semester", "").strip()
    status = request.args.get("status", "").strip()

    q = Course.query

    if semester:
        q = q.filter(Course.semester == semester)

    if status:
        q = q.filter(Course.status == status)

    courses = q.order_by(Course.id.desc()).all()
    semesters = db.session.query(Course.semester).distinct().all()

    return render_template(
        "courses/list.html",
        courses=courses,
        semesters=[s[0] for s in semesters if s[0]],
        semester=semester,
        status=status
    )


@app.route("/courses/add", methods=["GET", "POST"])
@role_required("admin", "teacher")
def add_course():
    teachers = Teacher.query.all()

    if request.method == "POST":
        course_no = request.form.get("course_no", "").strip()
        course_name = request.form.get("course_name", "").strip()
        credits = request.form.get("credits", type=float)
        hours = request.form.get("hours", type=int)
        teacher_id = request.form.get("teacher_id", type=int)
        max_capacity = request.form.get("max_capacity", type=int, default=50)
        semester = request.form.get("semester", "").strip()

        if not course_no or not course_name:
            flash("课程编号和课程名称不能为空", "danger")
            return render_template("courses/form.html", teachers=teachers, action="add")

        try:
            course = Course(
                course_no=course_no,
                course_name=course_name,
                credits=credits,
                hours=hours,
                teacher_id=teacher_id,
                max_capacity=max_capacity,
                semester=semester,
                status="open"
            )
            db.session.add(course)
            db.session.commit()

            log = OperationLog(
                user_id=session["user_id"],
                action="create",
                module="course",
                record_id=course.id,
                details=f"新增课程 {course_name}"
            )
            db.session.add(log)
            db.session.commit()

            flash("新增课程成功", "success")
            return redirect(url_for("list_courses"))
        except Exception as e:
            db.session.rollback()
            flash(f"添加失败：{str(e)}", "danger")

    return render_template("courses/form.html", teachers=teachers, action="add")


# ======================== 选课管理 ========================

@app.route("/enrollments")
@login_required
def list_enrollments():
    if session.get("role") == "student":
        student = Student.query.filter_by(user_id=session["user_id"]).first()
        enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    else:
        enrollments = Enrollment.query.all()

    return render_template("enrollments/list.html", enrollments=enrollments)


@app.route("/enrollments/add/<int:course_id>", methods=["POST"])
@login_required
def add_enrollment(course_id):
    course = Course.query.get_or_404(course_id)
    student = Student.query.filter_by(user_id=session["user_id"]).first()

    if not student:
        flash("学生信息不存在", "danger")
        return redirect(url_for("list_courses"))

    existing = Enrollment.query.filter_by(
        student_id=student.id,
        course_id=course_id
    ).first()

    if existing:
        flash("已经选过该课程", "warning")
        return redirect(url_for("list_courses"))

    current_count = db.session.query(Enrollment).filter_by(course_id=course_id).count()
    if current_count >= course.max_capacity:
        flash("课程已满员", "danger")
        return redirect(url_for("list_courses"))

    try:
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course_id,
            status="enrolled"
        )
        db.session.add(enrollment)
        db.session.commit()

        log = OperationLog(
            user_id=session["user_id"],
            action="enroll",
            module="course",
            record_id=enrollment.id,
            details=f"选课 {course.course_name}"
        )
        db.session.add(log)
        db.session.commit()

        flash("选课成功", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"选课失败：{str(e)}", "danger")

    return redirect(url_for("list_courses"))


# ======================== 成绩管理 ========================

@app.route("/scores")
@login_required
def list_scores():
    if session.get("role") == "student":
        student = Student.query.filter_by(user_id=session["user_id"]).first()
        q = Enrollment.query.filter_by(student_id=student.id)
        enrollments = q.all()
    else:
        enrollments = Enrollment.query.all()

    return render_template("scores/list.html", enrollments=enrollments)


@app.route("/scores/record/<int:enrollment_id>", methods=["GET", "POST"])
@role_required("admin", "teacher")
def record_score(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if request.method == "POST":
        score_value = request.form.get("score", type=float)
        grade = request.form.get("grade", "").strip()

        if score_value is None or score_value < 0 or score_value > 100:
            flash("成绩必须在 0-100 之间", "danger")
            return render_template("scores/form.html", enrollment=enrollment, action="record")

        try:
            enrollment.score = score_value
            enrollment.grade = grade

            db.session.commit()

            log = OperationLog(
                user_id=session["user_id"],
                action="record_score",
                module="score",
                record_id=enrollment.id,
                details=f"录入成绩 {score_value} 分"
            )
            db.session.add(log)
            db.session.commit()

            flash("成绩录入成功", "success")
            return redirect(url_for("list_scores"))
        except Exception as e:
            db.session.rollback()
            flash(f"录入失败：{str(e)}", "danger")

    return render_template("scores/form.html", enrollment=enrollment, action="record")


# ======================== 系统管理 ========================

@app.route("/ops-log")
@role_required("admin")
def list_ops_log():
    logs = OperationLog.query.order_by(OperationLog.created_at.desc()).limit(500).all()
    return render_template("admin/logs.html", logs=logs)


@app.route("/users")
@role_required("admin")
def list_users():
    users = User.query.order_by(User.id.desc()).all()
    return render_template("admin/users.html", users=users)


@app.route("/users/add", methods=["GET", "POST"])
@role_required("admin")
def add_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "").strip()
        email = request.form.get("email", "").strip()

        if not username or not password or not full_name:
            flash("用户名、密码、姓名不能为空", "danger")
            return render_template("admin/user_form.html", action="add")

        if User.query.filter_by(username=username).first():
            flash("用户名已存在", "danger")
            return render_template("admin/user_form.html", action="add")

        try:
            user = User(
                username=username,
                full_name=full_name,
                role=role,
                email=email
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            log = OperationLog(
                user_id=session["user_id"],
                action="create",
                module="user",
                record_id=user.id,
                details=f"新增用户 {username}({full_name})"
            )
            db.session.add(log)
            db.session.commit()

            flash("新增用户成功", "success")
            return redirect(url_for("list_users"))
        except Exception as e:
            db.session.rollback()
            flash(f"添加失败：{str(e)}", "danger")

    return render_template("admin/user_form.html", action="add")


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
