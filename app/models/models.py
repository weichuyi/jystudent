"""
所有数据模型定义
"""
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from .base import BaseModel, db


class User(BaseModel):
    """用户表：系统用户（管理员、教师、学生）"""
    __tablename__ = "users"
    
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")  # admin, teacher, student
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # 2FA相关
    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_secret = db.Column(db.String(32))  # Base32编码的密钥
    
    # 登录安全相关
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    locked_until = db.Column(db.DateTime)
    password_last_changed = db.Column(db.DateTime)
    
    # 关系
    student_profile = db.relationship("Student", backref="user", uselist=False, foreign_keys="Student.user_id")
    teacher_profile = db.relationship("Teacher", backref="user", uselist=False, foreign_keys="Teacher.user_id")
    classes_managed = db.relationship("Class", backref="headteacher", foreign_keys="Class.headteacher_id")
    operation_logs = db.relationship("OperationLog", backref="user")
    scores_recorded = db.relationship("Score", backref="recorder", foreign_keys="Score.recorded_by")
    status_changes_created = db.relationship("StudentStatusChange", backref="creator", foreign_keys="StudentStatusChange.created_by")
    
    def set_password(self, password):
        """设置密码（哈希处理）"""
        self.password = generate_password_hash(password)
        self.password_last_changed = datetime.utcnow()
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)
    
    def enable_2fa(self, secret):
        """启用双因素认证"""
        self.two_fa_enabled = True
        self.two_fa_secret = secret
    
    def disable_2fa(self):
        """禁用双因素认证"""
        self.two_fa_enabled = False
        self.two_fa_secret = None


class Class(BaseModel):
    """班级表"""
    __tablename__ = "classes"
    
    class_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    class_name = db.Column(db.String(100), nullable=False)
    headteacher_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    grade = db.Column(db.String(20))  # 年级
    major = db.Column(db.String(100))  # 专业
    total_students = db.Column(db.Integer, default=0)
    
    # 关系
    students = db.relationship("Student", backref="class_obj", lazy=True, foreign_keys="Student.class_id")


class Student(BaseModel):
    """学生表：扩展版本"""
    __tablename__ = "students"
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    student_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), index=True)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    major = db.Column(db.String(100))
    status = db.Column(db.String(20), default="enrolled", index=True)  # enrolled, leave, return, dropout
    id_number = db.Column(db.String(50), unique=True)
    enrollment_date = db.Column(db.Date)
    
    # 关系
    enrollments = db.relationship("Enrollment", backref="student", lazy=True, foreign_keys="Enrollment.student_id")
    status_changes = db.relationship("StudentStatusChange", backref="student", lazy=True, foreign_keys="StudentStatusChange.student_id")
    
    def get_current_semester_gpa(self, semester=None):
        """计算当前学期绩点"""
        from sqlalchemy import and_
        from .models import Course
        
        query = db.session.query(Enrollment).filter(Enrollment.student_id == self.id)
        if semester:
            course_ids = db.session.query(Course.id).filter(Course.semester == semester).all()
            query = query.filter(Enrollment.course_id.in_([c[0] for c in course_ids]))
        
        enrollments = query.all()
        if not enrollments:
            return 0.0
        
        total_credits = 0
        weighted_gpa = 0
        for enrollment in enrollments:
            if enrollment.score and enrollment.course.credits:
                total_credits += enrollment.course.credits
                grade_point = self._score_to_gpa(enrollment.score)
                weighted_gpa += grade_point * enrollment.course.credits
        
        return weighted_gpa / total_credits if total_credits > 0 else 0.0
    
    @staticmethod
    def _score_to_gpa(score):
        """成绩转换为绩点"""
        if score >= 90:
            return 4.0
        elif score >= 85:
            return 3.7
        elif score >= 80:
            return 3.3
        elif score >= 75:
            return 3.0
        elif score >= 70:
            return 2.6
        elif score >= 60:
            return 2.0
        else:
            return 0.0


class Teacher(BaseModel):
    """教师表"""
    __tablename__ = "teachers"
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    teacher_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    department = db.Column(db.String(100), index=True)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    qualification = db.Column(db.String(100))  # 学位
    hire_date = db.Column(db.Date)
    
    # 关系
    courses = db.relationship("Course", backref="teacher", lazy=True, foreign_keys="Course.teacher_id")


class Course(BaseModel):
    """课程表"""
    __tablename__ = "courses"
    
    course_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    course_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Float)  # 学分
    hours = db.Column(db.Integer)  # 学时
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), index=True)
    max_capacity = db.Column(db.Integer, default=50)
    semester = db.Column(db.String(20), index=True)  # 学期 如 2024-1
    status = db.Column(db.String(20), default="open", index=True)  # open, closed
    enrollment_start = db.Column(db.DateTime)
    enrollment_end = db.Column(db.DateTime)
    
    # 关系
    enrollments = db.relationship("Enrollment", backref="course", lazy=True, foreign_keys="Enrollment.course_id")
    
    def get_current_enrollment_count(self):
        """获取当前选课人数"""
        return db.session.query(Enrollment).filter(
            Enrollment.course_id == self.id,
            Enrollment.status == "enrolled"
        ).count()
    
    def is_available_for_enrollment(self):
        """检查课程是否可选课"""
        if self.status != "open":
            return False
        
        now = datetime.utcnow()
        if self.enrollment_start and now < self.enrollment_start:
            return False
        if self.enrollment_end and now > self.enrollment_end:
            return False
        
        current_count = self.get_current_enrollment_count()
        return current_count < self.max_capacity


class Enrollment(BaseModel):
    """选课表：学生选课记录"""
    __tablename__ = "enrollments"
    
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    score = db.Column(db.Float)
    grade = db.Column(db.String(5))  # 等级 A, B, C, D, F
    status = db.Column(db.String(20), default="enrolled", index=True)  # enrolled, withdrawn, completed
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    withdrawal_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    
    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", name="unique_student_course"),
    )


class Score(BaseModel):
    """成绩表：详细成绩记录"""
    __tablename__ = "scores"
    
    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollments.id"), nullable=False, index=True)
    score_value = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5))
    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    enrollment = db.relationship("Enrollment", backref="score_record")


class StudentStatusChange(BaseModel):
    """学籍异动表：记录学生休学、复学、退学等"""
    __tablename__ = "student_status_changes"
    
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    change_type = db.Column(db.String(20), nullable=False)  # leave, return, dropout
    reason = db.Column(db.String(255))
    approval_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)


class OperationLog(BaseModel):
    """操作日志表"""
    __tablename__ = "operation_logs"
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    module = db.Column(db.String(50), index=True)  # 模块名 student, course, score
    record_id = db.Column(db.Integer, index=True)
    details = db.Column(db.Text)
    
    def __repr__(self):
        return f"<OperationLog {self.action} on {self.module} at {self.created_at}>"
