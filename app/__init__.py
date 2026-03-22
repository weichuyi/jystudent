"""
应用工厂函数 - 创建和配置Flask应用
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import get_config
from app.models import db
from app.utils import setup_logging, register_error_handlers


def create_app(config=None):
    """
    应用工厂函数
    
    Args:
        config: 配置对象
    
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # 初始化数据库
    db.init_app(app)
    
    # 设置日志
    setup_logging(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 应用上下文中初始化数据库
    with app.app_context():
        db.create_all()
    
    # 注册蓝图(将在后面实现)
    # from app.routes import register_blueprints
    # register_blueprints(app)
    
    # 自定义CLI命令
    register_cli_commands(app)
    
    app.logger.info("应用初始化完成")
    
    return app


def register_cli_commands(app):
    """注册CLI命令"""
    import click
    from app.models import User, db
    from app.utils import log_audit
    from app.services import BackupService
    
    @app.cli.command()
    def init_db():
        """初始化数据库和创建默认管理员"""
        click.echo("初始化数据库...")
        db.create_all()
        
        # 创建默认管理员
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                full_name="系统管理员",
                role="admin",
                email="admin@school.com",
                is_active=True
            )
            admin.set_password("weichuy1")
            db.session.add(admin)
            db.session.commit()
            click.echo("✓ 创建默认管理员: admin / weichuy1")
        else:
            click.echo("✓ 管理员账户已存在")
    
    @app.cli.command()
    def backup():
        """创建数据库备份"""
        try:
            backup_path = BackupService.create_backup()
            click.echo(f"✓ 备份成功: {backup_path}")
        except Exception as e:
            click.echo(f"✗ 备份失败: {str(e)}", err=True)
    
    @app.cli.command()
    @click.argument('backup_file')
    def restore(backup_file):
        """恢复数据库备份"""
        try:
            BackupService.restore_backup(backup_file)
            click.echo(f"✓ 恢复成功: {backup_file}")
        except Exception as e:
            click.echo(f"✗ 恢复失败: {str(e)}", err=True)
    
    @app.cli.command()
    def cleanup_logs():
        """清理旧日志文件"""
        from app.utils import cleanup_old_logs
        try:
            cleanup_old_logs(days=30)
            click.echo("✓ 日志清理完成")
        except Exception as e:
            click.echo(f"✗ 清理失败: {str(e)}", err=True)
