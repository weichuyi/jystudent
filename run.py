"""
学生信息管理系统 - 浏览器启动器

这个脚本会在启动 Flask 应用后自动打开浏览器
"""

import os
import sys
import time
import webbrowser
from threading import Thread


def open_browser(url="http://127.0.0.1:5000", delay=2):
    """等待一段时间后打开浏览器"""
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    
    thread = Thread(target=_open, daemon=True)
    thread.start()


if __name__ == "__main__":
    # 导入 Flask 应用
    from app import app, init_db
    
    print("=" * 60)
    print("学生信息管理系统")
    print("=" * 60)
    print()
    print("初始化数据库...")
    init_db()
    print("✓ 数据库已就绪")
    print()
    print("启动服务器...")
    print("-" * 60)
    print()
    
    # 打开浏览器
    print("浏览器将在 2 秒后自动打开")
    print("访问地址: http://127.0.0.1:5000")
    print("默认账户: admin / admin@2024")
    print()
    print("-" * 60)
    
    open_browser()
    
    # 启动 Flask 应用
    try:
        app.run(debug=False, port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n服务器已关闭")
        sys.exit(0)
