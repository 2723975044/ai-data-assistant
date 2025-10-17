"""数据库工厂类"""
from typing import Dict, Any
from .base import BaseDatabase
from .mysql_db import MySQLDatabase
from .postgres_db import PostgreSQLDatabase, MongoDBDatabase


class DatabaseFactory:
    """数据库工厂类"""
    
    @staticmethod
    def create_database(db_type: str, connection_params: Dict[str, Any]) -> BaseDatabase:
        """
        创建数据库连接实例
        
        Args:
            db_type: 数据库类型 (mysql, postgres, mongodb)
            connection_params: 连接参数
            
        Returns:
            数据库实例
        """
        db_type = db_type.lower()
        
        if db_type == 'mysql':
            return MySQLDatabase(connection_params)
        elif db_type in ('postgres', 'postgresql'):
            return PostgreSQLDatabase(connection_params)
        elif db_type == 'mongodb':
            return MongoDBDatabase(connection_params)
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")


def get_database_from_config(config) -> BaseDatabase:
    """
    从配置创建数据库连接
    
    Args:
        config: 配置对象
        
    Returns:
        数据库实例
    """
    # 默认使用 MySQL
    db_params = {
        'host': config.mysql_host,
        'port': config.mysql_port,
        'user': config.mysql_user,
        'password': config.mysql_password,
        'database': config.mysql_database,
    }
    
    return DatabaseFactory.create_database('mysql', db_params)
