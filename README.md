# 智慧校园管理平台

一个基于 Flask + SQLAlchemy + Jinja2 的校园管理系统，覆盖学生、教师、班级、课程、选课、成绩、用户、备份、日志等核心场景。

当前仓库同时保留了两套启动入口，但日常开发与最新业务功能以根目录的 `app.py` 为准。

## 快速概览

- 目标用户：学校管理员、教师、学生
- 技术栈：Flask、SQLAlchemy、SQLite、Bootstrap、Jinja2、openpyxl
- 数据库文件：`instance/students.db`
- 当前主运行端口：5001（由 `app.py` 启动）

## 快速开始

1. 创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 安装依赖：

```powershell
pip install -r requirements.txt
```

3. 运行（开发/测试）：

```powershell
python app.py
```

访问应用：

```text
http://127.0.0.1:5001
```

默认管理员：`admin / weichuy1`

## 打包为 Windows 可执行文件（exe）

仓库自带打包脚本 `build_exe.py`，最简单的打包方式是运行：

```powershell
python build_exe.py
```

脚本内部使用 PyInstaller 生成单文件 exe，等效的 PyInstaller 命令（Windows 下 pathsep=`;`）为：

```powershell
python -m PyInstaller --onefile --windowed \
	--add-data templates;templates \
	--add-data static;static \
	--add-data app.py;. \
	--collect-all openpyxl \
	--collect-submodules flask \
	--collect-submodules flask_sqlalchemy \
	--hidden-import flask_sqlalchemy \
	--hidden-import openpyxl \
	--name SmartCampusPlatform_Fixed \
	--distpath dist --workpath build --specpath . run.py
```

完成后可在 `dist/` 中找到 `SmartCampusPlatform_Fixed.exe`。

## 项目结构（简要）

```text
jystudent/
├── app.py
├── main.py
├── run.py
├── build_exe.py
├── requirements.txt
├── instance/
├── static/
├── templates/
├── app/
│   ├── forms/
│   ├── models/
│   ├── routes/
│   └── services/
├── backups/
├── logs/
└── release/
```

## 常用说明与注意事项

- 启动时若数据库不存在，`app.py` 会自动初始化并确保默认管理员存在。
- 打包前请先确保依赖已安装且项目能在开发环境正常启动。
- “跑路”功能位于：管理中心 -> 系统信息，执行后会删除业务数据，仅保留管理员账户，务必先备份。

## 文档与手册

- 用户手册：见 用户手册.md
- 模块说明：见 讲解.md（新建，用于小组作业说明）

## 后续维护建议

- 若继续扩展，建议把 `app.py` 中的新功能回迁到 `app/` 下模块化结构。
- 生产环境请更换 `SECRET_KEY` 并修改默认管理员密码。
