"""
表单模块
"""
from .forms import (
    BaseForm, LoginForm, ChangePasswordForm, StudentForm, TeacherForm,
    ClassForm, CourseForm, ScoreForm, UserForm, SearchForm
)

__all__ = [
    'BaseForm', 'LoginForm', 'ChangePasswordForm', 'StudentForm', 'TeacherForm',
    'ClassForm', 'CourseForm', 'ScoreForm', 'UserForm', 'SearchForm'
]
