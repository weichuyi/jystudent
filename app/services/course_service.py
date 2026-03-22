"""
课程和选课服务
"""
from datetime import datetime
from sqlalchemy import and_
from app.models import Course, Enrollment, Teacher, db
from app.utils import (
    ValidationError, ResourceNotFoundError, BusinessLogicError,
    ValidationRules, log_audit
)


class CourseService:
    """课程服务"""
    
    @staticmethod
    def create_course(course_no, course_name, credits=None, hours=None,
                     teacher_id=None, max_capacity=50, semester=None,
                     status="open", created_by_id=None):
        """
        创建课程
        """
        # 检查课程号唯一性
        if Course.query.filter_by(course_no=course_no).first():
            raise ValidationError(f"课程号 {course_no} 已存在")
        
        # 验证学分和学时
        if credits:
            ValidationRules.validate_credits(credits)
        if hours and (hours < 0 or hours > 200):
            raise ValidationError("学时数必须在0-200之间")
        
        try:
            course = Course(
                course_no=course_no,
                course_name=course_name,
                credits=credits,
                hours=hours,
                teacher_id=teacher_id,
                max_capacity=max_capacity,
                semester=semester,
                status=status
            )
            db.session.add(course)
            db.session.commit()
            
            log_audit(created_by_id, "create_course", "course", course.id,
                     f"创建课程 {course_name}({course_no})")
            return course
        except Exception as e:
            db.session.rollback()
            raise Exception(f"创建课程失败: {str(e)}")
    
    @staticmethod
    def update_course(course_id, **kwargs):
        """更新课程信息"""
        course = Course.query.get(course_id)
        if not course:
            raise ResourceNotFoundError("课程")
        
        allowed_fields = {
            'course_name', 'credits', 'hours', 'teacher_id',
            'max_capacity', 'semester', 'status', 'enrollment_start',
            'enrollment_end'
        }
        
        try:
            for field, value in kwargs.items():
                if field not in allowed_fields or value is None:
                    continue
                
                if field == "credits":
                    ValidationRules.validate_credits(value)
                elif field == "max_capacity" and value < 1:
                    raise ValidationError("课程容量必须至少为1")
                
                setattr(course, field, value)
            
            db.session.commit()
            return course
        except Exception as e:
            db.session.rollback()
            raise Exception(f"更新课程失败: {str(e)}")
    
    @staticmethod
    def delete_course(course_id, deleted_by_id=None):
        """删除课程"""
        course = Course.query.get(course_id)
        if not course:
            raise ResourceNotFoundError("课程")
        
        # 检查是否有学生已选该课程
        enrollment_count = Enrollment.query.filter_by(
            course_id=course_id,
            status="enrolled"
        ).count()
        if enrollment_count > 0:
            raise BusinessLogicError(
                f"课程 {course.course_name} 已有 {enrollment_count} 名学生选课，无法删除"
            )
        
        try:
            db.session.delete(course)
            db.session.commit()
            
            log_audit(deleted_by_id, "delete_course", "course", course_id,
                     f"删除课程 {course.course_name}({course.course_no})")
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"删除课程失败: {str(e)}")
    
    @staticmethod
    def get_courses_by_semester(semester, open_only=False):
        """获取某学期的课程"""
        query = Course.query.filter_by(semester=semester)
        if open_only:
            query = query.filter_by(status="open")
        return query.all()


class EnrollmentService:
    """选课服务"""
    
    @staticmethod
    def enroll_student(student_id, course_id, enrolled_by_id=None):
        """
        学生选课
        
        Args:
            student_id: 学生ID
            course_id: 课程ID
            enrolled_by_id: 操作者ID
        
        Returns:
            Enrollment对象
        """
        from app.models import Student
        
        student = Student.query.get(student_id)
        if not student:
            raise ResourceNotFoundError("学生")
        
        course = Course.query.get(course_id)
        if not course:
            raise ResourceNotFoundError("课程")
        
        # 检查课程是否可选课
        if not course.is_available_for_enrollment():
            raise BusinessLogicError(
                "课程已关闭或选课已截止, 无法选课"
            )
        
        # 检查是否已选该课程
        existing = Enrollment.query.filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
                Enrollment.status == "enrolled"
            )
        ).first()
        
        if existing:
            raise BusinessLogicError(f"您已选过课程 {course.course_name}")
        
        # 检查课程容量
        current_count = course.get_current_enrollment_count()
        if current_count >= course.max_capacity:
            raise BusinessLogicError(
                f"课程 {course.course_name} 已满人({current_count}/{course.max_capacity})"
            )
        
        try:
            enrollment = Enrollment(
                student_id=student_id,
                course_id=course_id,
                status="enrolled",
                enrollment_date=datetime.utcnow()
            )
            db.session.add(enrollment)
            db.session.commit()
            
            log_audit(enrolled_by_id, "enroll", "enrollment", enrollment.id,
                     f"学生选课: {student.name} -> {course.course_name}")
            
            return enrollment
        except Exception as e:
            db.session.rollback()
            raise Exception(f"选课失败: {str(e)}")
    
    @staticmethod
    def withdraw_student(enrollment_id, withdrawn_by_id=None):
        """
        学生退课
        
        Args:
            enrollment_id: 选课记录ID
            withdrawn_by_id: 操作者ID
        """
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            raise ResourceNotFoundError("选课记录")
        
        if enrollment.status != "enrolled":
            raise BusinessLogicError("只能退出已选的课程")
        
        try:
            enrollment.status = "withdrawn"
            enrollment.withdrawal_date = datetime.utcnow()
            db.session.commit()
            
            log_audit(withdrawn_by_id, "withdraw", "enrollment", enrollment_id,
                     f"学生退课: {enrollment.student.name} <- {enrollment.course.course_name}")
            
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"退课失败: {str(e)}")
    
    @staticmethod
    def get_student_enrollments_by_course(course_id, status="enrolled"):
        """获取某课程的学生选课记录"""
        return Enrollment.query.filter_by(
            course_id=course_id,
            status=status
        ).all()
    
    @staticmethod
    def get_available_courses(student_id, semester=None):
        """
        获取学生可选的课程列表
        
        Args:
            student_id: 学生ID
            semester: 学期
        
        Returns:
            Course列表
        """
        # 获取学生已选的课程ID
        enrolled_course_ids = db.session.query(Enrollment.course_id).filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.status == "enrolled"
            )
        ).all()
        enrolled_ids = [c[0] for c in enrolled_course_ids]
        
        # 查询可选课程
        query = Course.query.filter(
            Course.status == "open"
        )
        
        if semester:
            query = query.filter_by(semester=semester)
        
        # 排除已选课程
        if enrolled_ids:
            query = query.filter(~Course.id.in_(enrolled_ids))
        
        return query.all()
