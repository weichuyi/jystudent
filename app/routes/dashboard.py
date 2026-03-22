"""
仪表板路由
"""
from flask import Blueprint, render_template, session
from app.utils import login_required
from app.models import Student, Teacher, Course, Class, db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """仪表板主页"""
    user_id = session.get('user_id')
    role = session.get('role')
    
    # 收集统计数据
    stats = {
        'total_students': Student.query.count(),
        'total_teachers': Teacher.query.count(),
        'total_courses': Course.query.count(),
        'total_classes': Class.query.count(),
    }
    
    recent_logs = None
    if role == 'admin':
        from app.models import OperationLog
        recent_logs = OperationLog.query.order_by(
            OperationLog.created_at.desc()
        ).limit(10).all()
    
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_logs=recent_logs
    )
