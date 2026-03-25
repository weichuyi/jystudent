"""
认证路由 - 登录、登出、密码管理
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.forms import LoginForm, ChangePasswordForm
from app.models import User, db
from app.services import UserService
from app.utils import (
    login_required, log_audit, AuthenticationError, ValidationError,
    AccountLockedError
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        try:
            user = UserService.authenticate(username, password)
            
            # 设置session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            session['avatar'] = user.avatar
            session.permanent = True
            
            # 记录日志
            log_audit(user.id, "login", "auth", user.id, f"用户登录")
            
            flash(f"欢迎 {user.full_name}", "success")
            return redirect(url_for('dashboard.index'))
        
        except AccountLockedError as e:
            flash(str(e), "danger")
        except AuthenticationError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"登录失败: {str(e)}", "danger")
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    user_id = session.get('user_id')
    username = session.get('username')
    
    log_audit(user_id, "logout", "auth", user_id)
    
    session.clear()
    flash("已退出登录", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()
    user_id = session.get('user_id')
    
    if form.validate_on_submit():
        try:
            UserService.change_password(
                user_id,
                form.old_password.data,
                form.new_password.data
            )
            flash("密码修改成功", "success")
            return redirect(url_for('dashboard.index'))
        except ValidationError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"修改失败: {str(e)}", "danger")
    
    return render_template('auth/change_password.html', form=form)


@auth_bp.before_request
def before_request():
    """请求前处理"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user or not user.is_active:
            session.clear()
            flash("您的账户已被禁用或不存在", "warning")
            return redirect(url_for('auth.login'))
