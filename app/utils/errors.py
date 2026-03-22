"""
应用异常定义和错误处理类
"""
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """应用基础异常类"""
    def __init__(self, message, code=500, category="error"):
        super().__init__(message)
        self.message = message
        self.code = code
        self.category = category
        logger.error(f"[{category}] {message}")


class ValidationError(AppException):
    """数据验证错误"""
    def __init__(self, message, field=None):
        super().__init__(message, 400, "validation_error")
        self.field = field


class AuthenticationError(AppException):
    """认证错误"""
    def __init__(self, message="认证失败"):
        super().__init__(message, 401, "authentication_error")


class AuthorizationError(AppException):
    """授权错误 - 权限不足"""
    def __init__(self, message="权限不足"):
        super().__init__(message, 403, "authorization_error")


class ResourceNotFoundError(AppException):
    """资源不存在"""
    def __init__(self, resource_type="资源", resource_id=None):
        msg = f"{resource_type}"
        if resource_id:
            msg += f"(ID: {resource_id})"
        msg += "不存在"
        super().__init__(msg, 404, "not_found_error")


class DuplicateResourceError(AppException):
    """资源重复 - 数据库唯一约束违反"""
    def __init__(self, field_name, value):
        message = f"{field_name} '{value}' 已存在"
        super().__init__(message, 409, "duplicate_error")


class DatabaseError(AppException):
    """数据库操作错误"""
    def __init__(self, message="数据库操作失败", original_error=None):
        super().__init__(message, 500, "database_error")
        if original_error:
            logger.exception(f"Database error: {original_error}")


class BusinessLogicError(AppException):
    """业务逻辑错误"""
    def __init__(self, message):
        super().__init__(message, 422, "business_logic_error")


class InvalidPasswordError(AppException):
    """密码验证错误"""
    def __init__(self, reason="密码不符合要求"):
        super().__init__(reason, 400, "invalid_password")


class AccountLockedError(AuthenticationError):
    """账户被锁定"""
    def __init__(self, message="账户因多次登录失败已被锁定，请稍后重试"):
        super().__init__(message)
        self.code = 429
        self.category = "account_locked"


class FileOperationError(AppException):
    """文件操作错误"""
    def __init__(self, message):
        super().__init__(message, 400, "file_operation_error")


def register_error_handlers(app):
    """注册所有错误处理器"""
    
    @app.errorhandler(ValidationError)
    @app.errorhandler(AuthenticationError)
    @app.errorhandler(AuthorizationError)
    @app.errorhandler(ResourceNotFoundError)
    @app.errorhandler(DuplicateResourceError)
    @app.errorhandler(BusinessLogicError)
    @app.errorhandler(InvalidPasswordError)
    @app.errorhandler(AccountLockedError)
    @app.errorhandler(FileOperationError)
    @app.errorhandler(DatabaseError)
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """处理应用自定义异常"""
        response = {
            "success": False,
            "message": error.message,
            "category": error.category
        }
        return jsonify(response), error.code
    
    @app.errorhandler(404)
    def handle_404(error):
        """处理404错误"""
        return jsonify({
            "success": False,
            "message": "请求的页面不存在",
            "category": "not_found"
        }), 404
    
    @app.errorhandler(500)
    def handle_500(error):
        """处理500错误"""
        logger.exception("Internal server error")
        return jsonify({
            "success": False,
            "message": "服务器内部错误，请稍后重试",
            "category": "server_error"
        }), 500
