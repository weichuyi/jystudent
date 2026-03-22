"""
路由模块 - 注册所有蓝图
"""
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.admin import admin_bp


def register_blueprints(app):
    """注册所有蓝图"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    
    # 后续可添加更多蓝图：
    # from app.routes.student import student_bp
    # from app.routes.teacher import teacher_bp
    # from app.routes.course import course_bp
    # from app.routes.score import score_bp
    # app.register_blueprint(student_bp)
    # app.register_blueprint(teacher_bp)
    # app.register_blueprint(course_bp)
    # app.register_blueprint(score_bp)


__all__ = ['register_blueprints']
