"""
验证和安全工具函数
"""
import re
import string
from functools import wraps
from datetime import datetime, timedelta
from flask import session, redirect, url_for, flash


class PasswordValidator:
    """密码验证器 - 支持密码强度检查"""
    
    @staticmethod
    def validate_password_strength(password, min_length=8):
        """
        验证密码强度
        
        要求：
        - 长度至少8个字符
        - 包含大写字母
        - 包含小写字母
        - 包含数字
        - 包含特殊字符
        """
        if not password or len(password) < min_length:
            return False, f"密码长度至少需要 {min_length} 个字符"
        
        if not re.search(r'[A-Z]', password):
            return False, "密码必须包含至少一个大写字母"
        
        if not re.search(r'[a-z]', password):
            return False, "密码必须包含至少一个小写字母"
        
        if not re.search(r'[0-9]', password):
            return False, "密码必须包含至少一个数字"
        
        if not re.search(r'[!@#$%^&*()_\-+=\[\]{};:\'",.<>?/\\|`~]', password):
            return False, "密码必须包含至少一个特殊字符"
        
        return True, "密码符合强度要求"
    
    @staticmethod
    def get_password_strength_hint():
        """获取密码强度提示"""
        return {
            "min_length": 8,
            "requirements": [
                "至少 8 个字符",
                "包含大写字母 (A-Z)",
                "包含小写字母 (a-z)",
                "包含数字 (0-9)",
                "包含特殊字符 (!@#$%^&*等)"
            ]
        }


class InputValidator:
    """输入验证器 - 防止SQL注入和XSS"""
    
    DANGEROUS_PATTERNS = [
        r"('|(\')|(--)|(;)|(\/\*))",  # SQL注入常见模式
        r"(javascript:|onerror=|onclick=)",  # XSS模式1
        r"(<script|</script|<iframe|<embed|<object)",  # XSS模式2
    ]
    
    @staticmethod
    def sanitize_input(value, field_type="text"):
        """
        清理输入值
        
        Args:
            value: 输入值
            field_type: 字段类型 (text, email, phone, number等)
        """
        if value is None:
            return None
        
        value = str(value).strip()
        
        # 检查危险模式
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"输入包含非法字符: {value[:20]}...")
        
        # 根据字段类型进行具体验证
        if field_type == "email":
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                raise ValueError("邮箱格式无效")
        
        elif field_type == "phone":
            if not re.match(r'^1[3-9]\d{9}$', value):
                raise ValueError("手机号码格式无效")
        
        elif field_type == "id_number":
            if not re.match(r'^\d{18}$|^\d{17}X$', value):
                raise ValueError("身份证号码格式无效")
        
        elif field_type == "username":
            if not re.match(r'^[a-zA-Z0-9_]{3,20}$', value):
                raise ValueError("用户名只能包含字母、数字和下划线，长度3-20")
        
        elif field_type == "number":
            try:
                float(value)
            except ValueError:
                raise ValueError("请输入有效的数字")
        
        return value
    
    @staticmethod
    def is_safe_input(value):
        """检查输入是否安全（快速检查）"""
        if not value:
            return True
        value_str = str(value).lower()
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value_str, re.IGNORECASE):
                return False
        return True


class RateLimiter:
    """简单的速率限制器 - 防止暴力攻击"""
    
    # 存储登录失败次数: {username: (count, timestamp)}
    _failed_attempts = {}
    
    @classmethod
    def record_failed_attempt(cls, username, max_attempts=5, lockout_minutes=15):
        """
        记录失败尝试
        
        Args:
            username: 用户名
            max_attempts: 最大尝试次数
            lockout_minutes: 锁定时间（分钟）
        
        Returns:
            (is_locked, remaining_time)
        """
        now = datetime.utcnow()
        
        if username in cls._failed_attempts:
            count, last_time = cls._failed_attempts[username]
            lockout_end = last_time + timedelta(minutes=lockout_minutes)
            
            if now < lockout_end:
                # 仍在锁定期内
                remaining = (lockout_end - now).total_seconds() / 60
                return True, int(remaining)
            else:
                # 锁定期已过，重置
                cls._failed_attempts[username] = (1, now)
                return False, 0
        else:
            cls._failed_attempts[username] = (1, now)
            return False, 0
        
        # 查询是否超过最大尝试次数
        if count >= max_attempts:
            cls._failed_attempts[username] = (count + 1, now)
            remaining = lockout_minutes
            return True, remaining
        else:
            cls._failed_attempts[username] = (count + 1, now)
            return False, 0
    
    @classmethod
    def reset_failed_attempts(cls, username):
        """重置失败尝试计数"""
        if username in cls._failed_attempts:
            del cls._failed_attempts[username]
    
    @classmethod
    def get_failed_attempts(cls, username):
        """获取失败尝试次数"""
        if username in cls._failed_attempts:
            count, _ = cls._failed_attempts[username]
            return count
        return 0


class ValidationRules:
    """数据验证规则集合"""
    
    @staticmethod
    def validate_student_no(student_no):
        """验证学号"""
        if not student_no or not re.match(r'^[0-9]{10}$', str(student_no)):
            raise ValueError("学号必须是10位数字")
    
    @staticmethod
    def validate_teacher_no(teacher_no):
        """验证教工号"""
        if not teacher_no or not re.match(r'^[A-Z]\d{8}$', str(teacher_no)):
            raise ValueError("教工号格式为：1个大写字母 + 8位数字")
    
    @staticmethod
    def validate_class_no(class_no):
        """验证班级号"""
        if not class_no or len(class_no) > 20:
            raise ValueError("班级号长度不能超过20个字符")
    
    @staticmethod
    def validate_age(age):
        """验证年龄"""
        try:
            age_int = int(age)
            if age_int < 15 or age_int > 100:
                raise ValueError("年龄必须在 15-100 之间")
        except ValueError:
            raise ValueError("年龄必须是有效的整数")
    
    @staticmethod
    def validate_score(score):
        """验证成绩"""
        try:
            score_float = float(score)
            if score_float < 0 or score_float > 100:
                raise ValueError("成绩必须在 0-100 之间")
        except ValueError:
            raise ValueError("成绩必须是有效的数字")
    
    @staticmethod
    def validate_credits(credits):
        """验证学分"""
        try:
            credits_float = float(credits)
            if credits_float < 0 or credits_float > 100:
                raise ValueError("学分必须在 0-100 之间")
        except ValueError:
            raise ValueError("学分必须是有效的数字")


# 身份验证装饰器
def login_required(f):
    """验证用户是否已登录"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("请先登录", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """验证用户角色"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("请先登录", "warning")
                return redirect(url_for("auth.login"))
            
            user_role = session.get("role")
            if user_role not in roles:
                flash("权限不足", "danger")
                return redirect(url_for("dashboard.index"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
