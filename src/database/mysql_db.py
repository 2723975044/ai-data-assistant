"""MySQL 数据库连接"""
from typing import Any, List, Dict, Optional
import pymysql
from pymysql.cursors import DictCursor
from .base import BaseDatabase


class MySQLDatabase(BaseDatabase):
    """MySQL 数据库连接类"""
    
    def connect(self) -> None:
        """建立 MySQL 连接"""
        try:
            self.connection = pymysql.connect(
                host=self.connection_params.get('host', 'localhost'),
                port=self.connection_params.get('port', 3306),
                user=self.connection_params.get('user'),
                password=self.connection_params.get('password'),
                database=self.connection_params.get('database'),
                charset='utf8mb4',
                cursorclass=DictCursor
            )
            print(f"✓ 成功连接到 MySQL 数据库: {self.connection_params.get('database')}")
        except Exception as e:
            raise ConnectionError(f"MySQL 连接失败: {str(e)}")
    
    def disconnect(self) -> None:
        """关闭 MySQL 连接"""
        if self.connection:
            self.connection.close()
            print("✓ MySQL 连接已关闭")
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        执行 MySQL 查询
        
        Args:
            query: SQL 查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or {})
                results = cursor.fetchall()
                return results
        except Exception as e:
            raise RuntimeError(f"查询执行失败: {str(e)}")
    
    def get_schema(self) -> Dict[str, Any]:
        """获取数据库 schema"""
        query = """
            SELECT TABLE_NAME, TABLE_COMMENT
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
        """
        
        results = self.execute_query(
            query,
            {'TABLE_SCHEMA': self.connection_params.get('database')}
        )
        
        schema = {}
        for row in results:
            table_name = row['TABLE_NAME']
            schema[table_name] = {
                'comment': row['TABLE_COMMENT'],
                'columns': self.get_table_info(table_name)
            }
        
        return schema
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表结构信息"""
        query = """
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT, IS_NULLABLE, COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """
        
        results = self.execute_query(
            query,
            {
                'TABLE_SCHEMA': self.connection_params.get('database'),
                'TABLE_NAME': table_name
            }
        )
        
        columns = {}
        for row in results:
            columns[row['COLUMN_NAME']] = {
                'type': row['DATA_TYPE'],
                'comment': row['COLUMN_COMMENT'],
                'nullable': row['IS_NULLABLE'] == 'YES',
                'key': row['COLUMN_KEY']
            }
        
        return columns
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取表的示例数据
        
        Args:
            table_name: 表名
            limit: 返回记录数
            
        Returns:
            示例数据
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)
