"""
用户服务 - 处理用户相关业务逻辑
"""
from datetime import datetime, timedelta
from app.models import User, db
from app.utils import (
    ValidationError, AuthenticationError, DuplicateResourceError,
    ResourceNotFoundError, PasswordValidator, RateLimiter, InputValidator,
    log_audit
)
import pyotp


class UserService:
    """用户服务"""
    
    @staticmethod
    def create_user(username, password, full_name, role="student", email=None, phone=None):
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 密码
            full_name: 全名
            role: 角色
            email: 邮箱
            phone: 手机号
        
        Returns:
            User对象
        """
        # 验证用户名唯一性
        if User.query.filter_by(username=username).first():
            raise DuplicateResourceError("用户名", username)
        
        # 验证邮箱唯一性
        if email and User.query.filter_by(email=email).first():
            raise DuplicateResourceError("邮箱", email)
        
        # 验证密码强度
        is_valid, message = PasswordValidator.validate_password_strength(password)
        if not is_valid:
            raise ValidationError(message)
        
        # 验证输入
        if email:
            InputValidator.sanitize_input(email, "email")
        if phone:
            InputValidator.sanitize_input(phone, "phone")
        
        try:
            user = User(
                username=username,
                full_name=full_name,
                role=role,
                email=email,
                phone=phone,
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            log_audit(None, "create_user", "user", user.id, f"创建用户 {username}")
            return user
        except Exception as e:
            db.session.rollback()
            raise Exception(f"创建用户失败: {str(e)}")
    
    @staticmethod
    def authenticate(username, password):
        """
        用户认证
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            User对象 或抛出异常
        """
        # 检查账户是否被锁定
        user = User.query.filter_by(username=username).first()
        if not user:
            raise AuthenticationError("用户名或密码错误")
        
        if user.is_locked and user.locked_until:
            if datetime.utcnow() < user.locked_until:
                remaining_minutes = (user.locked_until - datetime.utcnow()).total_seconds() / 60
                raise AuthenticationError(
                    f"账户已被锁定，请在 {int(remaining_minutes)} 分钟后重试"
                )
            else:
                # 解锁
                user.is_locked = False
                user.locked_until = None
                user.failed_login_attempts = 0
                db.session.commit()
        
        # 验证密码
        if not user.check_password(password):
            # 记录失败尝试
            is_locked, remaining = RateLimiter.record_failed_attempt(
                username,
                max_attempts=5,
                lockout_minutes=15
            )
            
            user.failed_login_attempts += 1
            if is_locked:
                user.is_locked = True
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            
            db.session.commit()
            
            if is_locked:
                raise AuthenticationError(f"登录失败次数过多，账户已锁定15分钟")
            else:
                raise AuthenticationError("用户名或密码错误")
        
        # 验证账户是否激活
        if not user.is_active:
            raise AuthenticationError("账户已被禁用")
        
        # 重置失败次数和锁定状态
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        RateLimiter.reset_failed_attempts(username)
        
        return user
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError("用户")
        
        # 验证旧密码
        if not user.check_password(old_password):
            raise ValidationError("原密码错误")
        
        # 验证新密码强度
        is_valid, message = PasswordValidator.validate_password_strength(new_password)
        if not is_valid:
            raise ValidationError(message)
        
        # 新密码不能和旧密码相同
        if user.check_password(new_password):
            raise ValidationError("新密码不能与原密码相同")
        
        try:
            user.set_password(new_password)
            db.session.commit()
            log_audit(user_id, "change_password", "user", user_id)
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"修改密码失败: {str(e)}")
    
    @staticmethod
    def enable_2fa(user_id):
        """
        启用双因素认证
        
        Returns:
            (secret, qr_uri)
        """
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError("用户")
        
        # 生成密钥
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # 生成QR码URI （用于二维码显示）
        qr_uri = totp.provisioning_uri(
            name=user.username,
            issuer_name='Smart Campus'
        )
        
        return secret, qr_uri
    
    @staticmethod
    def verify_2fa_token(user_id, token):
        """
        验证2FA令牌
        
        Returns:
            True/False
        """
        user = User.query.get(user_id)
        if not user or not user.two_fa_secret:
            return False
        
        totp = pyotp.TOTP(user.two_fa_secret)
        return totp.verify(token)
