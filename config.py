"""
应用配置文件 - 环境变量和全局配置管理
"""
import os
from datetime import timedelta

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "student-system-secret-key-2026"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///students.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session 配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/app.log"
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # 安全配置
    BCRYPT_LOG_ROUNDS = 12
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_ATTEMPTS = 5
    PASSWORD_LOCKOUT_TIME = 900  # 15分钟
    
    # 表单配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # 导入导出配置
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB 文件大小限制
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    

class DevelopmentConfig(Config):
    """开发配置"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """生产配置"""
    DEBUG = False
    TESTING = False
    

class TestingConfig(Config):
    """测试配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


def get_config():
    """获取配置对象"""
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()
