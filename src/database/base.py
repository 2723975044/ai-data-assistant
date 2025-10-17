"""数据库基类"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional


class BaseDatabase(ABC):
    """数据库基类"""
    
    def __init__(self, connection_params: Dict[str, Any]):
        """
        初始化数据库连接
        
        Args:
            connection_params: 数据库连接参数
        """
        self.connection_params = connection_params
        self.connection = None
    
    @abstractmethod
    def connect(self) -> None:
        """建立数据库连接"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        执行查询
        
        Args:
            query: SQL 查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        获取数据库 schema
        
        Returns:
            数据库结构信息
        """
        pass
    
    @abstractmethod
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表信息
        
        Args:
            table_name: 表名
            
        Returns:
            表结构信息
        """
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()
