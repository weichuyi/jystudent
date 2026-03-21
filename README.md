# 学生信息管理系统

一个基于 Flask + SQLite 的简易学生信息管理系统，支持学生信息的增删改查与搜索。

## 功能

- 新增学生
- 编辑学生信息
- 删除学生信息
- 学号/姓名/专业搜索
- 本地 SQLite 持久化存储

## 技术栈

- Python 3.10+
- Flask
- SQLite
- Bootstrap 5

## 快速开始

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 启动项目

```bash
python app.py
```

3. 浏览器访问

```text
http://127.0.0.1:5000
```

首次运行会自动在项目根目录创建 `students.db` 数据库文件。
