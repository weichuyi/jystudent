"""
学生服务 - 处理学生相关业务逻辑
"""
from datetime import datetime
from sqlalchemy import or_, and_
from app.models import Student, User, Class, Enrollment, OperationLog, db
from app.utils import (
    ValidationError, ResourceNotFoundError, DuplicateResourceError,
    ValidationRules, InputValidator, log_audit
)


class StudentService:
    """学生服务"""
    
    @staticmethod
    def create_student(student_no, name, class_id=None, gender=None, age=None,
                      phone=None, email=None, major=None, id_number=None,
                      user_id=None, created_by_id=None):
        """
        创建学生记录
        
        Args:
            student_no: 学号
            name: 姓名
            class_id: 班级ID
            gender: 性别
            age: 年龄
            phone: 手机
            email: 邮箱
            major: 专业
            id_number: 身份证号
            user_id: 关联的用户ID
            created_by_id: 创建者ID
        
        Returns:
            Student对象
        """
        # 验证学号
        ValidationRules.validate_student_no(student_no)
        
        # 检查学号唯一性
        if Student.query.filter_by(student_no=student_no).first():
            raise DuplicateResourceError("学号", student_no)
        
        # 验证输入
        if phone:
            InputValidator.sanitize_input(phone, "phone")
        if email:
            InputValidator.sanitize_input(email, "email")
        if id_number:
            InputValidator.sanitize_input(id_number, "id_number")
        
        if age:
            ValidationRules.validate_age(age)
        
        try:
            student = Student(
                student_no=student_no,
                name=name,
                class_id=class_id,
                gender=gender,
                age=age,
                phone=phone,
                email=email,
                major=major,
                id_number=id_number,
                user_id=user_id,
                status="enrolled",
                enrollment_date=datetime.utcnow().date()
            )
            db.session.add(student)
            db.session.commit()
            
            log_audit(created_by_id, "create_student", "student", student.id,
                     f"创建学生 {name}({student_no})")
            return student
        except Exception as e:
            db.session.rollback()
            raise Exception(f"创建学生失败: {str(e)}")
    
    @staticmethod
    def update_student(student_id, **kwargs):
        """
        更新学生信息
        
        Args:
            student_id: 学生ID
            **kwargs: 要更新的字段
        """
        student = Student.query.get(student_id)
        if not student:
            raise ResourceNotFoundError("学生")
        
        # 验证和清理输入
        allowed_fields = {
            'name', 'gender', 'age', 'class_id', 'phone', 'email',
            'major', 'status'
        }
        
        try:
            for field, value in kwargs.items():
                if field not in allowed_fields:
                    continue
                
                if value is None:
                    continue
                
                # 字段级验证
                if field == "age" and value:
                    ValidationRules.validate_age(value)
                elif field == "phone" and value:
                    InputValidator.sanitize_input(value, "phone")
                elif field == "email" and value:
                    InputValidator.sanitize_input(value, "email")
                
                setattr(student, field, value)
            
            db.session.commit()
            return student
        except Exception as e:
            db.session.rollback()
            raise Exception(f"更新学生失败: {str(e)}")
    
    @staticmethod
    def delete_student(student_id, deleted_by_id=None):
        """
        删除学生（级联删除选课和成绩）
        
        Args:
            student_id: 学生ID
            deleted_by_id: 操作者ID
        """
        student = Student.query.get(student_id)
        if not student:
            raise ResourceNotFoundError("学生")
        
        try:
            # 删除相关的选课记录
            Enrollment.query.filter_by(student_id=student_id).delete()
            
            # 删除学生记录
            db.session.delete(student)
            db.session.commit()
            
            log_audit(deleted_by_id, "delete_student", "student", student_id,
                     f"删除学生 {student.name}({student.student_no})")
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"删除学生失败: {str(e)}")
    
    @staticmethod
    def search_students(keyword=None, class_id=None, status=None, limit=50, offset=0):
        """
        搜索学生
        
        Args:
            keyword: 搜索关键词（学号、姓名）
            class_id: 班级ID过滤
            status: 学籍状态过滤
            limit: 限制数量
            offset: 分页offset
        
        Returns:
            (students_list, total_count)
        """
        query = Student.query
        
        # 关键词搜索
        if keyword:
            keyword = keyword.strip()
            query = query.filter(
                or_(
                    Student.student_no.contains(keyword),
                    Student.name.contains(keyword)
                )
            )
        
        # 班级过滤
        if class_id:
            query = query.filter_by(class_id=class_id)
        
        # 状态过滤
        if status:
            query = query.filter_by(status=status)
        
        # 获取总数
        total = query.count()
        
        # 分页
        students = query.order_by(Student.created_at.desc()).limit(limit).offset(offset).all()
        
        return students, total
    
    @staticmethod
    def get_student_enrollments(student_id, semester=None):
        """
        获取学生选课记录
        
        Args:
            student_id: 学生ID
            semester: 学期过滤
        
        Returns:
            Enrollment列表
        """
        query = Enrollment.query.filter_by(student_id=student_id)
        
        if semester:
            from app.models import Course
            course_ids = db.session.query(Course.id).filter(
                Course.semester == semester
            ).all()
            query = query.filter(
                Enrollment.course_id.in_([c[0] for c in course_ids])
            )
        
        return query.all()
    
    @staticmethod
    def get_student_gpa(student_id, semester=None):
        """
        计算学生绩点
        
        Args:
            student_id: 学生ID
            semester: 学期（None表示所有）
        
        Returns:
            GPA值
        """
        student = Student.query.get(student_id)
        if not student:
            raise ResourceNotFoundError("学生")
        
        return student.get_current_semester_gpa(semester)
    
    @staticmethod
    def change_student_status(student_id, new_status, reason=None, changed_by_id=None):
        """
        更改学生学籍状态
        
        Args:
            student_id: 学生ID
            new_status: 新状态
            reason: 原因
            changed_by_id: 操作者ID
        """
        student = Student.query.get(student_id)
        if not student:
            raise ResourceNotFoundError("学生")
        
        valid_statuses = ["enrolled", "leave", "return", "dropout"]
        if new_status not in valid_statuses:
            raise ValidationError(f"无效的学籍状态: {new_status}")
        
        try:
            old_status = student.status
            student.status = new_status
            
            # 记录学籍异动
            from app.models import StudentStatusChange
            status_change = StudentStatusChange(
                student_id=student_id,
                change_type=new_status,
                reason=reason,
                approval_date=datetime.utcnow().date(),
                created_by=changed_by_id
            )
            db.session.add(status_change)
            db.session.commit()
            
            log_audit(changed_by_id, "change_status", "student", student_id,
                     f"学生 {student.name} 学籍状态: {old_status} -> {new_status}")
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"更改学籍状态失败: {str(e)}")
