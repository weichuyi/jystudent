"""
管理员专用路由 - 系统管理、备份恢复、数据导出导入
权限：仅管理员可访问
"""
import os
import shutil
import logging
from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for, session
from datetime import datetime

from app.utils.validators import role_required, login_required
from app.services import BackupService, ExportService, ImportService
from app.utils.logger import get_audit_logger

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()

@admin_bp.route('/')
@login_required
@role_required('admin')
def index():
    """管理员首页"""
    try:
        # 获取备份列表
        backups = BackupService.list_backups()
        backup_count = len(backups)
        latest_backup = backups[0] if backups else None
        
        # 获取日志统计
        log_dir = "logs"
        log_sizes = {}
        for log_file in ['app.log', 'error.log', 'audit.log']:
            log_path = os.path.join(log_dir, log_file)
            if os.path.exists(log_path):
                log_sizes[log_file] = os.path.getsize(log_path) / 1024  # KB
        
        stats = {
            'backup_count': backup_count,
            'latest_backup': latest_backup,
            'log_sizes': log_sizes
        }
        
        log_entry = f"USER={session.get('user_id')} | ACTION=访问管理员首页 | MODULE=admin_index"
        audit_logger.info(log_entry)
        return render_template('admin/index.html', stats=stats)
    except Exception as e:
        logger.error(f"管理员首页错误: {str(e)}", exc_info=True)
        flash("首页加载失败", "danger")
        return redirect(url_for('dashboard.index'))


@admin_bp.route('/backup')
@login_required
@role_required('admin')
def backup_list():
    """备份管理页面"""
    try:
        backups = BackupService.list_backups()
        backup_info = []
        
        for backup_file in backups:
            file_path = os.path.join('backups', backup_file)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            file_mtime = os.path.getmtime(file_path)
            backup_date = datetime.fromtimestamp(file_mtime)
            
            backup_info.append({
                'filename': backup_file,
                'size_mb': f"{file_size:.2f}",
                'date': backup_date.strftime("%Y-%m-%d %H:%M:%S"),
                'timestamp': file_mtime
            })
        
        # 按时间倒序排列
        backup_info.sort(key=lambda x: x['timestamp'], reverse=True)
        
        log_audit('浏览备份列表', 'backup_list', 'success')
        return render_template('admin/backup.html', backups=backup_info)
    except Exception as e:
        logger.error(f"备份列表错误: {str(e)}", exc_info=True)
        flash("备份列表加载失败", "danger")
        return redirect(url_for('admin.index'))


@admin_bp.route('/backup/create', methods=['POST'])
@login_required
@role_required('admin')
def create_backup():
    """创建新备份"""
    try:
        # 生成备份文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        
        BackupService.create_backup(backup_name)
        
        log_audit(f'创建备份: {backup_name}', 'backup_create', 'success')
        flash(f"备份创建成功: {backup_name}", "success")
        return redirect(url_for('admin.backup_list'))
    except Exception as e:
        logger.error(f"创建备份错误: {str(e)}", exc_info=True)
        log_audit('创建备份失败', 'backup_create', 'failed', extra=str(e))
        flash(f"备份创建失败: {str(e)}", "danger")
        return redirect(url_for('admin.backup_list'))


@admin_bp.route('/backup/restore/<backup_file>', methods=['POST'])
@login_required
@role_required('admin')
def restore_backup(backup_file):
    """恢复备份"""
    try:
        backup_path = os.path.join('backups', backup_file)
        
        # 安全检查：确认文件存在且在backups目录下
        if not os.path.exists(backup_path) or not backup_file.endswith('.db'):
            flash("备份文件不存在或格式无效", "danger")
            return redirect(url_for('admin.backup_list'))
        
        BackupService.restore_backup(backup_path)
        
        log_audit(f'恢复备份: {backup_file}', 'backup_restore', 'success')
        flash(f"备份已恢复: {backup_file}", "success")
        return redirect(url_for('admin.backup_list'))
    except Exception as e:
        logger.error(f"恢复备份错误: {str(e)}", exc_info=True)
        log_audit(f'恢复备份失败: {backup_file}', 'backup_restore', 'failed', extra=str(e))
        flash(f"恢复备份失败: {str(e)}", "danger")
        return redirect(url_for('admin.backup_list'))


@admin_bp.route('/backup/delete/<backup_file>', methods=['POST'])
@login_required
@role_required('admin')
def delete_backup(backup_file):
    """删除备份"""
    try:
        backup_path = os.path.join('backups', backup_file)
        
        # 安全检查
        if not os.path.exists(backup_path) or not backup_file.endswith('.db'):
            flash("备份文件不存在", "danger")
            return redirect(url_for('admin.backup_list'))
        
        os.remove(backup_path)
        
        log_audit(f'删除备份: {backup_file}', 'backup_delete', 'success')
        flash(f"备份已删除: {backup_file}", "success")
        return redirect(url_for('admin.backup_list'))
    except Exception as e:
        logger.error(f"删除备份错误: {str(e)}", exc_info=True)
        log_audit(f'删除备份失败: {backup_file}', 'backup_delete', 'failed', extra=str(e))
        flash(f"删除备份失败: {str(e)}", "danger")
        return redirect(url_for('admin.backup_list'))


@admin_bp.route('/backup/download/<backup_file>')
@login_required
@role_required('admin')
def download_backup(backup_file):
    """下载备份文件"""
    try:
        backup_path = os.path.join('backups', backup_file)
        
        if not os.path.exists(backup_path) or not backup_file.endswith('.db'):
            flash("备份文件不存在", "danger")
            return redirect(url_for('admin.backup_list'))
        
        log_audit(f'下载备份: {backup_file}', 'backup_download', 'success')
        return send_file(backup_path, as_attachment=True, download_name=backup_file)
    except Exception as e:
        logger.error(f"下载备份错误: {str(e)}", exc_info=True)
        log_audit(f'下载备份失败: {backup_file}', 'backup_download', 'failed', extra=str(e))
        flash(f"下载备份失败: {str(e)}", "danger")
        return redirect(url_for('admin.backup_list'))


@admin_bp.route('/data')
@login_required
@role_required('admin')
def data_management():
    """数据管理页面 - 导出导入"""
    try:
        log_audit('访问数据管理页面', 'data_management', 'success')
        return render_template('admin/data.html')
    except Exception as e:
        logger.error(f"数据管理页面错误: {str(e)}", exc_info=True)
        flash("数据管理页面加载失败", "danger")
        return redirect(url_for('admin.index'))


@admin_bp.route('/data/export/students', methods=['POST'])
@login_required
@role_required('admin')
def export_students():
    """导出学生数据为Excel"""
    try:
        output_file = f"export_students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join('backups', output_file)
        
        ExportService.export_students(output_path)
        
        log_audit('导出学生数据', 'export_students', 'success')
        return send_file(output_path, as_attachment=True, download_name=output_file)
    except Exception as e:
        logger.error(f"导出学生数据错误: {str(e)}", exc_info=True)
        log_audit('导出学生数据失败', 'export_students', 'failed', extra=str(e))
        flash(f"导出失败: {str(e)}", "danger")
        return redirect(url_for('admin.data_management'))


@admin_bp.route('/data/export/scores', methods=['POST'])
@login_required
@role_required('admin')
def export_scores():
    """导出成绩数据为Excel"""
    try:
        output_file = f"export_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join('backups', output_file)
        
        ExportService.export_scores(output_path)
        
        log_audit('导出成绩数据', 'export_scores', 'success')
        return send_file(output_path, as_attachment=True, download_name=output_file)
    except Exception as e:
        logger.error(f"导出成绩数据错误: {str(e)}", exc_info=True)
        log_audit('导出成绩数据失败', 'export_scores', 'failed', extra=str(e))
        flash(f"导出失败: {str(e)}", "danger")
        return redirect(url_for('admin.data_management'))


@admin_bp.route('/data/export/courses', methods=['POST'])
@login_required
@role_required('admin')
def export_courses():
    """导出课程数据为Excel"""
    try:
        output_file = f"export_courses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join('backups', output_file)
        
        ExportService.export_courses(output_path)
        
        log_audit('导出课程数据', 'export_courses', 'success')
        return send_file(output_path, as_attachment=True, download_name=output_file)
    except Exception as e:
        logger.error(f"导出课程数据错误: {str(e)}", exc_info=True)
        log_audit('导出课程数据失败', 'export_courses', 'failed', extra=str(e))
        flash(f"导出失败: {str(e)}", "danger")
        return redirect(url_for('admin.data_management'))


@admin_bp.route('/cleanup-logs', methods=['POST'])
@login_required
@role_required('admin')
def cleanup_logs():
    """清理旧日志"""
    try:
        from app.utils.logger import cleanup_old_logs
        cleanup_old_logs(days=30)
        
        log_audit('清理日志', 'cleanup_logs', 'success')
        flash("日志清理完成（30天前的日志已删除）", "success")
        return redirect(url_for('admin.index'))
    except Exception as e:
        logger.error(f"清理日志错误: {str(e)}", exc_info=True)
        log_audit('清理日志失败', 'cleanup_logs', 'failed', extra=str(e))
        flash(f"日志清理失败: {str(e)}", "danger")
        return redirect(url_for('admin.index'))


@admin_bp.route('/system-info')
@login_required
@role_required('admin')
def system_info():
    """系统信息页面"""
    try:
        import platform
        import sys
        
        info = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'processor': platform.processor(),
            'backup_dir_size': 0,
            'log_dir_size': 0
        }
        
        # 计算目录大小
        for root, dirs, files in os.walk('backups'):
            for file in files:
                file_path = os.path.join(root, file)
                info['backup_dir_size'] += os.path.getsize(file_path) / (1024 * 1024)
        
        for root, dirs, files in os.walk('logs'):
            for file in files:
                file_path = os.path.join(root, file)
                info['log_dir_size'] += os.path.getsize(file_path) / 1024
        
        log_audit('访问系统信息', 'system_info', 'success')
        return render_template('admin/system_info.html', info=info)
    except Exception as e:
        logger.error(f"系统信息错误: {str(e)}", exc_info=True)
        flash("系统信息获取失败", "danger")
        return redirect(url_for('admin.index'))
