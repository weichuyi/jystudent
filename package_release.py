#!/usr/bin/env python
"""
一键生成测试发布包：
1) 可选执行 build_exe.py 生成 exe
2) 复制 exe 到 release 目录
3) 可选打包 instance/students.db 测试数据
4) 生成 zip 供分发

用法：
  python package_release.py
  python package_release.py --skip-build
  python package_release.py --without-db
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).parent
EXE_NAME = "SmartCampusPlatform_Fixed.exe"
DIST_EXE = PROJECT_ROOT / "dist" / EXE_NAME
RELEASE_DIR = PROJECT_ROOT / "release"


def run_build() -> None:
    print("[1/4] 开始构建 exe...")
    cmd = [sys.executable, str(PROJECT_ROOT / "build_exe.py")]
    subprocess.run(cmd, check=True)
    if not DIST_EXE.exists():
        raise FileNotFoundError(f"未找到 exe: {DIST_EXE}")
    print(f"  [OK] 构建完成: {DIST_EXE.name}")


def copy_payload(target_dir: Path, include_db: bool) -> None:
    print("[2/4] 组装发布目录...")
    if target_dir.exists():
        shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(DIST_EXE, target_dir / DIST_EXE.name)

    if include_db:
        src_instance = PROJECT_ROOT / "instance"
        src_db = src_instance / "students.db"
        if src_db.exists():
            dest_instance = target_dir / "instance"
            dest_instance.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_db, dest_instance / "students.db")
            print("  [OK] 已包含测试数据库 instance/students.db")
        else:
            print("  ! 未找到 instance/students.db，跳过数据库打包")

    readme = target_dir / "START_HERE.txt"
    readme.write_text(
        "智慧校园管理平台 - 测试包使用说明\n"
        "================================\n\n"
        f"1. 双击 {EXE_NAME}\n"
        "2. 浏览器优先打开 http://127.0.0.1:5001（如被占用会自动切换到 5002/5003...）\n"
        "3. 默认管理员账号: admin\n"
        "4. 默认管理员密码: weichuy1\n\n"
        "说明:\n"
        "- 如果包含 instance/students.db，则使用打包者当前测试数据\n"
        "- 如果未包含数据库，首次启动会自动初始化空库\n",
        encoding="utf-8",
    )
    print("  [OK] 已生成 START_HERE.txt")


def make_zip(target_dir: Path) -> Path:
    print("[3/4] 生成 zip...")
    zip_path = RELEASE_DIR / f"{target_dir.name}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for path in target_dir.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=path.relative_to(target_dir))

    print(f"  [OK] 已生成: {zip_path.name}")
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="一键生成测试发布包")
    parser.add_argument("--skip-build", action="store_true", help="跳过 build_exe.py，直接使用现有 dist/SmartCampusPlatform.exe")
    parser.add_argument("--without-db", action="store_true", help="不包含 instance/students.db")
    args = parser.parse_args()

    print("=" * 60)
    print("智慧校园管理平台 - 一键测试发布")
    print("=" * 60)

    if not args.skip_build:
        run_build()
    elif not DIST_EXE.exists():
        print("[FAIL] 你选择了 --skip-build，但 exe 不存在，请先打包")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload_dir = RELEASE_DIR / f"SmartCampusPlatform_TestPackage_{timestamp}"

    print("[4/4] 打包发布文件...")
    copy_payload(payload_dir, include_db=not args.without_db)
    zip_path = make_zip(payload_dir)

    print("\n发布完成")
    print(f"目录: {payload_dir}")
    print(f"压缩包: {zip_path}")
    print("\n把 zip 文件发给测试人员即可。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
