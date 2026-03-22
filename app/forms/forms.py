"""
WTForms 表单定义 - 统一的数据验证
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, SelectField, \
                     SubmitField, TextAreaField, DateField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, \
                              Optional, NumberRange, Regexp
from email_validator import validate_email, EmailNotValidError


class BaseForm(FlaskForm):
    """表单基础类 - 自定义错误消息"""
    class Meta:
        # 禁用 CSRF 令牌超时限制
        csrf = True


class LoginForm(BaseForm):
    """登录表单"""
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='用户名不能为空'),
            Length(min=3, max=20, message='用户名长度3-20个字符')
        ],
        render_kw={'placeholder': '请输入用户名', 'autocomplete': 'username'}
    )
    password = PasswordField(
        '密码',
        validators=[DataRequired(message='密码不能为空')],
        render_kw={'placeholder': '请输入密码', 'autocomplete': 'current-password'}
    )
    submit = SubmitField('登录')


class ChangePasswordForm(BaseForm):
    """修改密码表单"""
    old_password = PasswordField(
        '原密码',
        validators=[DataRequired(message='原密码不能为空')],
        render_kw={'placeholder': '请输入原密码'}
    )
    new_password = PasswordField(
        '新密码',
        validators=[
            DataRequired(message='新密码不能为空'),
            Length(min=8, message='密码必须至少8个字符'),
            Regexp(
                r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*])',
                message='密码必须包含大小写字母、数字和特殊字符'
            )
        ],
        render_kw={'placeholder': '大小写字母、数字、特殊字符'}
    )
    confirm_password = PasswordField(
        '确认新密码',
        validators=[
            DataRequired(message='确认密码不能为空'),
            EqualTo('new_password', message='两次输入密码不一致')
        ],
        render_kw={'placeholder': '请再输入一次新密码'}
    )
    submit = SubmitField('修改密码')


class StudentForm(BaseForm):
    """学生表单"""
    student_no = StringField(
        '学号 *',
        validators=[
            DataRequired(message='学号不能为空'),
            Regexp(r'^\d{10}$', message='学号必须是10位数字')
        ]
    )
    name = StringField(
        '姓名 *',
        validators=[DataRequired(message='姓名不能为空'), Length(max=100)]
    )
    gender = SelectField(
        '性别',
        choices=[('', '请选择'), ('男', '男'), ('女', '女')],
        validators=[Optional()]
    )
    age = IntegerField(
        '年龄',
        validators=[
            Optional(),
            NumberRange(min=15, max=100, message='年龄必须在15-100之间')
        ]
    )
    class_no = StringField('班级编号', validators=[Optional()])
    phone = StringField(
        '手机',
        validators=[
            Optional(),
            Regexp(r'^1[3-9]\d{9}$', message='手机号码格式不正确')
        ]
    )
    email = EmailField(
        '邮箱',
        validators=[
            Optional(),
            Email(message='邮箱格式不正确')
        ]
    )
    major = StringField('专业', validators=[Optional(), Length(max=100)])
    id_number = StringField(
        '身份证号',
        validators=[
            Optional(),
            Regexp(r'^\d{18}$|^\d{17}X$', message='身份证号格式不正确')
        ]
    )
    status = SelectField(
        '学籍状态',
        choices=[
            ('enrolled', '在读'),
            ('leave', '休学'),
            ('return', '复学'),
            ('dropout', '退学')
        ]
    )
    submit = SubmitField('提交')


class TeacherForm(BaseForm):
    """教师表单"""
    teacher_no = StringField(
        '教工号 *',
        validators=[
            DataRequired(message='教工号不能为空'),
            Regexp(r'^[A-Z]\d{8}$', message='教工号格式：1个大写字母+8位数字')
        ]
    )
    name = StringField(
        '姓名 *',
        validators=[DataRequired(message='姓名不能为空'), Length(max=100)]
    )
    gender = SelectField(
        '性别',
        choices=[('', '请选择'), ('男', '男'), ('女', '女')],
        validators=[Optional()]
    )
    department = StringField('部门', validators=[Optional(), Length(max=100)])
    phone = StringField(
        '手机',
        validators=[
            Optional(),
            Regexp(r'^1[3-9]\d{9}$', message='手机号码格式不正确')
        ]
    )
    email = EmailField(
        '邮箱',
        validators=[Optional(), Email(message='邮箱格式不正确')]
    )
    qualification = StringField('学位', validators=[Optional(), Length(max=100)])
    submit = SubmitField('提交')


class ClassForm(BaseForm):
    """班级表单"""
    class_no = StringField(
        '班级编号 *',
        validators=[DataRequired(message='班级编号不能为空'), Length(max=50)]
    )
    class_name = StringField(
        '班级名称 *',
        validators=[DataRequired(message='班级名称不能为空'), Length(max=100)]
    )
    grade = StringField('年级', validators=[Optional(), Length(max=20)])
    major = StringField('专业', validators=[Optional(), Length(max=100)])
    headteacher_id = SelectField(
        '班主任',
        coerce=int,
        validators=[Optional()]
    )
    submit = SubmitField('提交')


class CourseForm(BaseForm):
    """课程表单"""
    course_no = StringField(
        '课程号 *',
        validators=[DataRequired(message='课程号不能为空'), Length(max=50)]
    )
    course_name = StringField(
        '课程名称 *',
        validators=[DataRequired(message='课程名称不能为空'), Length(max=100)]
    )
    credits = FloatField(
        '学分',
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message='学分必须在0-100之间')
        ]
    )
    hours = IntegerField(
        '学时',
        validators=[Optional(), NumberRange(min=0, max=200)]
    )
    teacher_id = SelectField(
        '教师',
        coerce=int,
        validators=[Optional()]
    )
    max_capacity = IntegerField(
        '最大容量',
        default=50,
        validators=[
            Optional(),
            NumberRange(min=1, max=1000, message='容量必须在1-1000之间')
        ]
    )
    semester = StringField('学期', validators=[Optional(), Length(max=20)])
    status = SelectField(
        '状态',
        choices=[('open', '开放'), ('closed', '关闭')],
        validators=[Optional()]
    )
    enrollment_start = DateField('选课开始时间', validators=[Optional()])
    enrollment_end = DateField('选课结束时间', validators=[Optional()])
    submit = SubmitField('提交')


class ScoreForm(BaseForm):
    """成绩表单"""
    score_value = FloatField(
        '成绩 *',
        validators=[
            DataRequired(message='成绩不能为空'),
            NumberRange(min=0, max=100, message='成绩必须在0-100之间')
        ]
    )
    grade = SelectField(
        '等级',
        choices=[
            ('A', 'A (90-100)'),
            ('B', 'B (80-89)'),
            ('C', 'C (70-79)'),
            ('D', 'D (60-69)'),
            ('F', 'F (0-59)')
        ],
        validators=[Optional()]
    )
    submit = SubmitField('提交')


class UserForm(BaseForm):
    """用户管理表单"""
    username = StringField(
        '用户名 *',
        validators=[
            DataRequired(message='用户名不能为空'),
            Length(min=3, max=20, message='用户名长度3-20个字符'),
            Regexp(r'^[a-zA-Z0-9_]+$', message='用户名只能包含字母、数字和下划线')
        ]
    )
    full_name = StringField(
        '姓名 *',
        validators=[DataRequired(message='姓名不能为空'), Length(max=100)]
    )
    email = EmailField(
        '邮箱',
        validators=[Optional(), Email(message='邮箱格式不正确')]
    )
    phone = StringField(
        '手机',
        validators=[
            Optional(),
            Regexp(r'^1[3-9]\d{9}$|^$', message='手机号码格式不正确')
        ]
    )
    role = SelectField(
        '角色 *',
        choices=[
            ('admin', '管理员'),
            ('teacher', '教师'),
            ('student', '学生')
        ],
        validators=[DataRequired(message='角色不能为空')]
    )
    is_active = SelectField(
        '是否激活',
        choices=[('True', '是'), ('False', '否')],
        validators=[Optional()]
    )
    submit = SubmitField('提交')


class SearchForm(BaseForm):
    """通用搜索表单"""
    keyword = StringField(
        '搜索',
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': '输入关键词搜索...'}
    )
    status = SelectField('状态', choices=[('', '全部')], validators=[Optional()])
    submit = SubmitField('搜索')
