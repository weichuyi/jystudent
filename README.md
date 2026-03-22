# 智慧校园管理平台 (Smart Campus Platform)

🎓 一个企业级的智慧校园管理平台，基于 **Flask + SQLAlchemy** 开发，支持多角色权限管理、完整的教育管理功能。

**最新更新**: 🔄 全面重构升级 (2026年3月22日)
- ✅ 模块化架构 (models/services/routes/forms)
- ✅ 企业级安全 (密码强度、账户锁定、2FA)
- ✅ 完善的日志系统 (分级、轮转、自动清理)
- ✅ 数据备份恢复
- ✅ 高级数据验证 (WTForms)

---

## 📋 核心功能清单

### 1. 用户认证与安全 🔐 ✅
- **多角色登录**：管理员、教师、学生三种角色
- **密码安全**：强度检查、修改管理、bcrypt加密
- **登录保护**：失败锁定 (5次失败→15分钟锁定)
- **双因素认证**：2FA框架 (TOTP令牌)
- **权限控制**：基于角色的访问控制 (RBAC)
- **CSRF保护**：Flask-WTF防护
- **审计日志**：所有操作追踪记录

### 2. 学生信息管理 ✅
- **增删改查**：学号、姓名、性别、班级、电话、邮箱、身份证等
- **高级搜索**：按学号、姓名、班级、学籍状态过滤
- **学籍管理**：记录休学、复学、退学等状态变化
- **绩点计算**：自动计算学生GPA
- **数据导入导出**：支持Excel批量导入

### 3. 教师信息管理 ✅
- 教师信息维护（工号、姓名、部门、学位等）
- 教师课程分配
- 教师搜索与筛选
- Excel批量导入

### 4. 班级管理 ✅
- 班级创建、编辑、删除
- 班主任分配
- 班级成员统计
- 班级信息维护

### 5. 课程管理 ✅
- 课程信息维护（课程号、名称、学分、学时）
- 教师分配
- 学期管理
- 课程容量管理
- 选课时间限制

### 6. 选课管理 ✅
- 学生在线选课
- 课程容量控制
- 重复选课防止
- 选课时间窗口控制
- 选课记录查询
- **新增**: 完整的退课功能

### 7. 成绩管理 ✅
- 教师录入/修改成绩
- 学生查询自己成绩
- 成绩等级自动计算
- **新增**: 成绩分布统计
- **新增**: 班级排名功能

### 8. 系统管理 ✅
- 用户管理（新增、编辑、启用/禁用）
- **新增**: 密码重置与管理
- **新增**: 数据库备份恢复
- 操作日志查询
- 日志审计追踪
- **新增**: 日志分级和清理

---

## 🏗️ 项目架构

### 新的模块化结构 (重构后)
```
app/
├── models/              # 数据模型层
│   ├── base.py         # 基类和db实例
│   └── models.py       # ORM模型定义
├── services/           # 业务逻辑层 (4个核心service)
│   ├── user_service.py      # 用户认证、密码、2FA
│   ├── student_service.py   # 学生CRUD、搜索、学籍
│   ├── course_service.py    # 课程和选课管理
│   └── data_service.py      # 备份、导出、导入
├── routes/            # 路由层
│   ├── auth.py        # 认证路由
│   └── dashboard.py   # 仪表板路由
├── forms/             # 表单验证层 (WTForms)
│   └── forms.py      # 10+验证表单
└── utils/            # 工具函数层
    ├── errors.py     # 11个自定义异常
    ├── logger.py     # 分级日志系统
    └── validators.py # 数据验证和防护
```

**代码质量**: 单文件 2000+行 → 模块化 <500行/文件

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端框架** | Flask 3.0.3 | Web框架 |
| **数据库** | SQLite + SQLAlchemy 2.0 | ORM和数据持久化 |
| **前端** | Bootstrap 5 + Jinja2 | 响应式UI |
| **表单验证** | WTForms 3.1 | 表单验证和CSRF保护 |
| **认证** | Werkzeug Security + bcrypt | 密码加密 |
| **2FA** | pyotp 2.9 | TOTP令牌生成 |
| **数据导出** | OpenPyXL 3.1 | Excel操作 |
| **日志** | Python logging | 分级日志系统 |

---

## 🚀 快速开始

### 系统要求
- Python 3.10+
- Windows/Linux/Mac

### 1. 进入项目目录
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

### 3. 启动应用 (推荐使用新代码)
```bash
python main.py
```

**提示**: 
- 浏览器自动打开: http://127.0.0.1:5000
- 日志自动保存到: logs/ 目录
- 备份自动保存到: backups/ 目录

### 4. 浏览器访问
```
http://127.0.0.1:5000
```


**用户名**: admin  
**密码**: weichuy1

> ⚠️ **首次登录强烈建议修改默认密码！** 进入系统后点击 "修改密码"

---

## 📁 项目结构

### 新的模块化架构 (重构后)
```
jystudent/
├── app/                            # 应用包 (新)
│   ├── __init__.py                 # 应用工厂
│   ├── models/
│   │   ├── base.py                 # 数据库基类
│   │   └── models.py               # ORM模型
│   ├── routes/
│   │   ├── auth.py                 # 认证路由
│   │   └── dashboard.py            # 仪表板路由
│   ├── services/
│   │   ├── user_service.py         # 用户服务
│   │   ├── student_service.py      # 学生服务
│   │   ├── course_service.py       # 课程服务
│   │   └── data_service.py         # 备份/导出/导入
│   ├── forms/
│   │   └── forms.py                # WTForms验证表单
│   └── utils/
│       ├── errors.py               # 异常定义
│       ├── logger.py               # 日志系统
│       └── validators.py           # 数据验证
├── config.py                       # 应用配置 (新)
├── main.py                         # 应用入口 (推荐使用)
├── app.py                          # 原应用 (保留)
├── requirements.txt                # 依赖列表 (已更新)
├── templates/                      # 前端模板
├── static/                         # CSS等静态资源
├── logs/                           # 日志目录 (自动创建)
├── backups/                        # 备份目录 (自动创建)
├── students.db                     # SQLite数据库
└── README.md                       # 项目文档 (已更新)
```

### 核心目录说明

| 目录 | 说明 |
|------|------|
| `app/` | 应用主体，包含所有业务逻辑 |
| `app/models/` | 数据模型定义 (ORM) |
| `app/services/` | 业务逻辑层 (4个核心Service) |
| `app/routes/` | 路由处理层 (MVC的C) |
| `app/forms/` | WTForms表单验证 |
| `app/utils/` | 工具函数和异常定义 |
| `templates/` | HTML前端模板 |
| `static/` | CSS、JavaScript等静态资源 |
| `logs/` | 分级日志文件 (自动创建) |
| `backups/` | 数据库备份 (自动创建) |

---

## 🔐 安全特性

### 密码管理
- ✅ **强度检查**: 至少8个字符，包含大小写、数字、特殊字符
- ✅ **加密存储**: 使用bcrypt哈希算法
- ✅ **修改历史**: 追踪密码最后修改时间
- ✅ **防暴力破解**: 5次失败后锁定15分钟

### 访问控制
- ✅ **CSRF防护**: Flask-WTF保护
- ✅ **会话管理**: 安全的Session处理
- ✅ **审计日志**: 记录所有用户操作
- ✅ **双因素认证**: 2FA框架支持 (TOTP)

### 数据保护
- ✅ **SQL注入防护**: SQLAlchemy ORM + 输入验证
- ✅ **XSS防护**: 输入清理和模板转义
- ✅ **数据备份**: 自动备份和恢复功能
- ✅ **日志清理**: 自动清理30天前的日志

---

## 📊 新增功能详解

### 1. 高级数据验证
```python
# WTForms集成，自动验证所有输入
from app.forms import StudentForm

form = StudentForm()
if form.validate_on_submit():
    # 所有字段已验证
    pass
```

### 2. 分级日志系统
```
logs/
├── app.log       # 应用日志 (INFO及以上)
├── error.log     # 错误日志 (ERROR及以上)  
└── audit.log     # 审计日志 (操作追踪)

特性: 
- 自动轮转 (10MB分割)
- 自动清理 (30天)
- 彩色输出 (控制台)
```

### 3. 数据备份恢复
```python
from app.services import BackupService

# 创建备份
BackupService.create_backup("backup_20260322")

# 列出备份
backups = BackupService.list_backups()

# 恢复备份
BackupService.restore_backup("backups/backup_20260322.db")
```

### 4. 统一异常处理
```python
from app.utils import (
    ValidationError,
    AuthenticationError,
    BusinessLogicError
)

# 统一的错误响应格式
# JSON格式, HTTP状态码自动映射
```

### 5. 业务逻辑服务层
```python
from app.services import (
    UserService,      # 用户认证
    StudentService,   # 学生管理
    CourseService,    # 课程管理
    EnrollmentService # 选课管理
)

# 清晰的业务接口
user = UserService.authenticate(username, password)
StudentService.create_student(student_no, name, ...)
```

---

## 📖 详细文档

项目包含4个详细的文档文件：

| 文档 | 说明 |
|------|------|
| **REFACTOR_GUIDE.md** | 详细重构指南和完整API文档 |
| **PROJECT_REFACTOR_SUMMARY.md** | 项目重构总结和技术指标 |
| **COMPLETION_SUMMARY.md** | 功能完成清单和亮点总结 |
| **FILE_MANIFEST.md** | 新建文件清单和结构说明 |

📌 **强烈推荐阅读 REFACTOR_GUIDE.md，了解所有新功能的使用方法**

---

## 🎯 使用工作流

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
# 基于新架构 main.py 打包
pyinstaller --onefile --windowed --icon=icon.ico ^
  --add-data "app:app" ^
  --add-data "templates:templates" ^
  --add-data "static:static" ^
  main.py

# 或使用旧架构 app.py 打包（兼容模式）
pyinstaller --onefile --windowed --icon=icon.ico ^
  --add-data "templates:templates" ^
  --add-data "static:static" ^
  app.py
```

## 部署指南

### 开发环境运行
```bash
# 使用新的应用入口 (推荐)
python main.py

# 或使用旧的应用入口
python app.py
```

### 局域网部署
```bash
# 方法1：使用Flask内置服务器 (小规模)
python main.py

# 方法2：允许外网访问 - 编辑 main.py 最后一行
# 将 app.run() 改为：
app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
```

### 生产部署
建议使用 Gunicorn + Nginx：
```bash
# 1. 安装Gunicorn
pip install gunicorn

# 2. 使用app factory指定配置 (推荐)
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('ProductionConfig')"

# 或简单方式
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Docker部署 (可选)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

## 扩展计划

- [x] 导入导出 Excel (已实现)
- [ ] 分页和排序优化
- [ ] 数据统计报表
- [ ] 成绩曲线图
- [ ] 移动端适配
- [ ] 用户头像上传

## 常见问题

### Q: 如何修改默认管理员密码？
A: 登录后点击右上角"修改密码"进行变更

### Q: 如何备份和恢复数据？
A: 有两种方式：
1. **快速备份**：直接复制 `students.db` 文件进行备份
2. **系统备份**：使用新的备份服务
   ```python
   from app.services import BackupService
   # 创建备份
   BackupService.create_backup("backup_name")
   # 恢复备份
   BackupService.restore_backup("backups/backup_name.db")
   ```

### Q: 如何导出数据为Excel？
A: 使用新的导出功能
   ```python
   from app.services import ExportService
   # 导出学生数据
   ExportService.export_students("output.xlsx")
   # 导出成绩数据
   ExportService.export_scores("output.xlsx")
   ```

### Q: 支持多用户同时使用吗？
A: 是的，使用 Session 进行用户隔离，支持并发访问。生产环境建议：
   - 使用 Gunicorn 多进程
   - 配置 Nginx 负载均衡
   - 使用专业数据库（如 PostgreSQL）替代 SQLite

## 许可证

MIT License

## 联系与支持

如有任何问题，欢迎提出 Issue 或联系开发人员。

---

**开发日期**：2026年  
**最后更新**：2026年3月22日
