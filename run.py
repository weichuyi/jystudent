"""
智慧校园管理平台 - 浏览器启动器

这个脚本会在启动 Flask 应用后自动打开浏览器
"""

import io
import os
import sys
import time
import webbrowser
import importlib.util
import socket
from pathlib import Path
from threading import Thread

# PyInstaller --windowed 模式下 sys.stdout/stderr 为 None，
# 任何 print 都会崩溃。此处统一重定向到 devnull 避免启动失败。
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")


def open_browser(url="http://127.0.0.1:5001", delay=2):
    """等待一段时间后打开浏览器"""
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    
    thread = Thread(target=_open, daemon=True)
    thread.start()


def load_runtime_app():
    """优先从根目录 app.py 加载，避免与 app/ 包同名冲突。"""
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    app_file = base_dir / "app.py"

    if not app_file.exists():
        raise FileNotFoundError(f"未找到应用入口文件: {app_file}")

    spec = importlib.util.spec_from_file_location("legacy_app_main", str(app_file))
    if spec is None or spec.loader is None:
        raise ImportError("无法加载 app.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app, module.init_db


def find_available_port(preferred_port=5001, max_tries=20):
    """返回可用端口，优先5001，冲突时顺延。"""
    for port in range(preferred_port, preferred_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("未找到可用端口，请关闭占用端口的进程后重试")


if __name__ == "__main__":
    # 导入 Flask 应用（规避 app.py 与 app/ 同名包冲突）
    app, init_db = load_runtime_app()
    port = find_available_port(preferred_port=5001)
    url = f"http://127.0.0.1:{port}"
    
    print("=" * 60)
    print("智慧校园管理平台")
    print("=" * 60)
    print()
    print("初始化数据库...")
    init_db()
    print("[OK] 数据库已就绪")
    print()
    print("启动服务器...")
    print("-" * 60)
    print()
    
    # 打开浏览器
    print("浏览器将在 2 秒后自动打开")
    print(f"访问地址: {url}")
    if port != 5001:
        print("提示: 5001 端口被占用，已自动切换到可用端口")
    print("默认账户: admin / weichuy1")
    print()
    print("-" * 60)
    
    open_browser(url=url)
    
    # 启动 Flask 应用
    try:
        app.run(debug=False, port=port, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n服务器已关闭")
        sys.exit(0)
