"""
Smart Campus Platform - 新的应用入口
运行此文件以启动重构后的应用
"""
import os
import sys
import webbrowser
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.models import db, User
from app.routes import register_blueprints
from config import DevelopmentConfig


def init_db():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
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
            print("✓ 创建默认管理员: admin / weichuy1")
        else:
            print("✓ 管理员账户已存在")


def main():
    """主程序入口"""
    # 创建应用
    app = create_app(DevelopmentConfig())
    
    # 注册蓝图
    register_blueprints(app)
    
    # 初始化数据库（如果需要）
    with app.app_context():
        db.create_all()
        
        # 确保有默认管理员
        if not User.query.filter_by(username="admin").first():
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
    
    # 启动应用
    print("="*60)
    print("智慧校园管理平台 (Smart Campus Platform)")
    print("="*60)
    print("启动信息:")
    print(f"  URL: http://127.0.0.1:5000")
    print(f"  默认账号: admin")
    print(f"  默认密码: weichuy1")
    print("="*60)
    print("按 Ctrl+C 停止服务器")
    print("="*60)
    
    # 尝试自动打开浏览器
    def open_browser():
        import time
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:5000')
    
    import threading
    thread = threading.Thread(target=open_browser, daemon=True)
    thread.start()
    
    # 运行应用
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True,
        use_debugger=True
    )


if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "init-db":
            init_db()
            sys.exit(0)
    
    main()
