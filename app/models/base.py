"""
数据库初始化和基础模型
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    """SQLAlchemy 基础类"""
    pass

# 创建数据库实例
db = SQLAlchemy(model_class=Base)


class TimestampMixin:
    """时间戳混入类"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )


class BaseModel(db.Model, TimestampMixin):
    """基础模型"""
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    
    def to_dict(self, include_relationships=False):
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def to_json(self):
        """转换为JSON友好的格式"""
        return self.to_dict()
