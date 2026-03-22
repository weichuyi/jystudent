#!/usr/bin/env python
"""
PyInstaller 打包脚本
将 Flask 应用打包为独立的 .exe 执行文件

使用方法：
    python build_exe.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def main():
    # 获取项目根目录
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    spec_file = project_root / "SmartCampusPlatform.spec"

    print("=" * 60)
    print("智慧校园管理平台 - PyInstaller 打包工具")
    print("=" * 60)

    # 清理旧的构建文件
    print("\n[1/4] 清理旧的构建文件...")
    for directory in [dist_dir, build_dir]:
        if directory.exists():
            print(f"  删除: {directory}")
            shutil.rmtree(directory, ignore_errors=True)
    
    if spec_file.exists():
        print(f"  删除: {spec_file}")
        spec_file.unlink()

    # 检查 PyInstaller 是否已安装
    print("\n[2/4] 检查依赖...")
    try:
        import PyInstaller
        print(f"  ✓ PyInstaller 已安装 (v{PyInstaller.__version__})")
    except ImportError:
        print("  ✗ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # 构建命令
    print("\n[3/4] 开始打包...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # 单个 exe 文件
        "--windowed",                   # 无控制台窗口（可选）
        "--add-data", f"templates{os.pathsep}templates",
        "--add-data", f"static{os.pathsep}static",
        "--add-data", f"app.py{os.pathsep}.",
        "--collect-submodules", "flask",
        "--collect-submodules", "flask_sqlalchemy",
        "--hidden-import", "flask_sqlalchemy",
        "--name", "SmartCampusPlatform",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(project_root),
        str(project_root / "run.py")
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        if result.returncode == 0:
            print("  ✓ 打包成功！")
        else:
            print("  ✗ 打包失败")
            return 1
    except subprocess.CalledProcessError as e:
        print(f"  ✗ 打包过程出错: {e}")
        return 1

    # 显示结果
    print("\n[4/4] 打包完成！")
    exe_file = dist_dir / "SmartCampusPlatform.exe"
    
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"\n✓ 可执行文件已生成:")
        print(f"  位置: {exe_file}")
        print(f"  大小: {size_mb:.2f} MB")
        print("\n使用方法:")
        print(f"  1. 双击运行: {exe_file.name}")
        print(f"  2. 应用会自动打开浏览器访问 http://127.0.0.1:5001")
        print(f"  3. 默认管理员账号: admin / weichuy1")
        return 0
    else:
        print("\n✗ 打包失败，未生成 exe 文件")
        return 1

if __name__ == "__main__":
    sys.exit(main())
