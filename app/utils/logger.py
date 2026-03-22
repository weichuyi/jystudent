"""
日志系统 - 分级日志和文件管理
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(app):
    """配置应用日志系统"""
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 获取Flask logger
    logger = app.logger
    logger.setLevel(logging.DEBUG)
    
    # 移除默认handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    # 创建格式化器
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    # 控制台处理器（DEBUG级别及以上）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter(log_format))
    logger.addHandler(console_handler)
    
    # 文件处理器 - INFO日志（rotating）
    info_log = log_dir / "app.log"
    info_handler = logging.handlers.RotatingFileHandler(
        info_log,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)
    
    # 文件处理器 - ERROR日志（单独文件）
    error_log = log_dir / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log,
        maxBytes=10485760,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # 操作审计日志处理器
    audit_log = log_dir / "audit.log"
    audit_handler = logging.handlers.RotatingFileHandler(
        audit_log,
        maxBytes=10485760,
        backupCount=10,
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    audit_handler.setFormatter(audit_formatter)
    
    # 审计logger（单独的logger，不继承app logger）
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False
    
    logger.info("日志系统初始化完成")
    return logger


def get_audit_logger():
    """获取审计日志logger"""
    return logging.getLogger('audit')


def log_audit(user_id, action, module, record_id=None, details=None):
    """记录审计日志"""
    audit_logger = get_audit_logger()
    timestamp = datetime.utcnow().isoformat()
    log_entry = f"USER={user_id} | ACTION={action} | MODULE={module}"
    if record_id:
        log_entry += f" | RECORD_ID={record_id}"
    if details:
        log_entry += f" | DETAILS={details}"
    audit_logger.info(log_entry)


def cleanup_old_logs(log_dir="logs", days=30):
    """清理超过指定天数的日志文件"""
    import time
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    
    current_time = time.time()
    cutoff_time = current_time - (days * 86400)
    
    for log_file in log_path.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
            except Exception as e:
                logging.warning(f"无法删除日志文件 {log_file}: {e}")


# 创建 utils/__init__.py
__all__ = ['setup_logging', 'get_audit_logger', 'log_audit', 'cleanup_old_logs']
