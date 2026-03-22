# 智慧校园管理平台

一个功能全面的智慧校园管理平台，基于 Flask + SQLAlchemy 开发，支持多角色权限管理、成绩管理、选课管理等完整的教育管理功能。

## 核心功能清单

### 1. 用户登录与权限 ✅
- **多角色登录**：管理员、教师、学生三种角色
- **密码管理**：登录验证、密码修改
- **权限控制**：不同角色可访问不同功能模块

### 2. 学生信息管理 ✅
- **增删改查**：学号、姓名、性别、班级、电话、邮箱等
- **高级筛选**：按班级、学籍状态、学号/姓名搜索
- **学籍异动**：记录休学、复学、退学等状态变化
- **数据批量**：支持单个学生编辑和删除

### 3. 教师信息管理 ✅
- 教师信息维护（工号、姓名、部门、学位等）
- 教师课程分配

### 4. 班级管理 ✅
- 班级创建、编辑、删除
- 班主任分配
- 班级成员人数统计

### 5. 课程管理 ✅
- 课程信息维护（课程号、名称、学分、学时）
- 教师分配
- 学期管理
- 课程容量设置

### 6. 选课管理 ✅
- 学生在线选课
- 选课记录查询
- 课程人数上限控制
- 退课功能（预留）

### 7. 成绩管理 ✅
- 教师录入 / 修改成绩
- 学生查询自己成绩
- 成绩等级自动计算
- 成绩统计功能

### 8. 系统管理 ✅
- 用户管理（新增用户、权限分配）
- 操作日志（审计追踪）
- 数据完整性维护

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask 3.0.3 |
| 数据库 | SQLite + SQLAlchemy ORM |
| 前端 | Bootstrap 5 + Jinja2 |
| 认证 | Werkzeug Security（密码哈希） |
| 数据导出 | OpenPyXL（Excel） |

## 快速开始

### 系统要求
- Python 3.10+
- Windows/Linux/Mac

### 1. 克隆或下载项目
```bash
cd c:\Users\<username>\Desktop\jystudent
```

### 2. 创建虚拟环境并安装依赖
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 初始化数据库
```bash
python -c "from app import app, init_db; init_db()"
```

### 4. 启动应用
```bash
python app.py
```

### 5. 浏览器访问
```
http://127.0.0.1:5000
```

## 默认登录账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | weichuy1 |

## 项目结构

```
jystudent/
├── app.py                          # Flask 应用主文件
├── requirements.txt                # Python 依赖
├── README.md                       # 项目文档
├── build_exe.py                    # PyInstaller 打包脚本
├── students.db                     # SQLite 数据库文件
├── templates/                      # 前端模板
│   ├── base.html                   # 基础布局模板
│   ├── dashboard.html              # 仪表板
│   ├── auth/                       # 认证相关
│   │   ├── login.html              # 登录页
│   │   └── change_password.html    # 修改密码
│   ├── students/                   # 学生管理
│   │   ├── list.html               # 列表
│   │   └── form.html               # 新增/编辑
│   ├── classes/                    # 班级管理
│   ├── courses/                    # 课程管理
│   ├── enrollments/                # 选课管理
│   ├── scores/                     # 成绩管理
│   └── admin/                      # 系统管理
│       ├── users.html              # 用户管理
│       └── logs.html               # 操作日志
└── static/                         # 静态文件
    └── style.css                   # 样式表
```

## 功能演示

### 登录流程
1. 访问 http://127.0.0.1:5000，自动跳转到登录页
2. 输入用户名和密码
3. 登录成功后进入仪表板

### 学生管理流程
1. 点击"学生"菜单 → "学生列表"
2. 可按班级、状态、学号/姓名筛选
3. 点击"新增学生"添加新学生
4. 点击编辑或删除按钮进行操作

### 选课流程（学生角色）
1. 登录后点击"选课"菜单
2. 查看可选课程
3. 点击"选课"按钮选择课程
4. 点击"成绩"查看已选课程和成绩

## 打包为可执行文件（.exe）

### 方法一：使用 PyInstaller（推荐）

1. 安装 PyInstaller
```bash
pip install pyinstaller
```

2. 运行打包脚本
```bash
python build_exe.py
```

3. 生成的 .exe 文件在 `dist/` 目录下

### 方法二：直接使用 PyInstaller 命令

```bash
pyinstaller --onefile --windowed --icon=icon.ico ^
  --add-data "templates:templates" ^
  --add-data "static:static" ^
  app.py
```

## 部署指南

### 局域网部署
修改 `app.py` 的启动命令：
```python
if __name__ == "__main__":
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)  # 允许所有机器访问
```

### 生产部署
建议使用 Gunicorn + Nginx：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 扩展计划

- [ ] 导入导出 Excel
- [ ] 分页和排序优化
- [ ] 数据统计报表
- [ ] 成绩曲线图
- [ ] 移动端适配
- [ ] 用户头像上传

## 常见问题

### Q: 如何修改默认管理员密码？
A: 登录后点击右上角"修改密码"进行变更

### Q: 如何备份数据？
A: 直接复制 `students.db` 文件进行备份

### Q: 支持多用户同时使用吗？
A: 是的，使用 Session 进行用户隔离，支持并发访问

## 许可证

MIT License

## 联系与支持

如有任何问题，欢迎提出 Issue 或联系开发人员。

---

**开发日期**：2026年  
**最后更新**：2026年3月22日
