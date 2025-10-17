"""PostgreSQL 数据库连接"""
from typing import Any, List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from .base import BaseDatabase


class PostgreSQLDatabase(BaseDatabase):
    """PostgreSQL 数据库连接类"""
    
    def connect(self) -> None:
        """建立 PostgreSQL 连接"""
        try:
            self.connection = psycopg2.connect(
                host=self.connection_params.get('host', 'localhost'),
                port=self.connection_params.get('port', 5432),
                user=self.connection_params.get('user'),
                password=self.connection_params.get('password'),
                database=self.connection_params.get('database')
            )
            print(f"✓ 成功连接到 PostgreSQL 数据库: {self.connection_params.get('database')}")
        except Exception as e:
            raise ConnectionError(f"PostgreSQL 连接失败: {str(e)}")
    
    def disconnect(self) -> None:
        """关闭 PostgreSQL 连接"""
        if self.connection:
            self.connection.close()
            print("✓ PostgreSQL 连接已关闭")
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """执行 PostgreSQL 查询"""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or {})
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            raise RuntimeError(f"查询执行失败: {str(e)}")
    
    def get_schema(self) -> Dict[str, Any]:
        """获取数据库 schema"""
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        
        results = self.execute_query(query)
        
        schema = {}
        for row in results:
            table_name = row['table_name']
            schema[table_name] = {
                'columns': self.get_table_info(table_name)
            }
        
        return schema
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表结构信息"""
        query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %(table_name)s
            ORDER BY ordinal_position
        """
        
        results = self.execute_query(query, {'table_name': table_name})
        
        columns = {}
        for row in results:
            columns[row['column_name']] = {
                'type': row['data_type'],
                'nullable': row['is_nullable'] == 'YES',
                'default': row['column_default']
            }
        
        return columns


class MongoDBDatabase(BaseDatabase):
    """MongoDB 数据库连接类"""
    
    def connect(self) -> None:
        """建立 MongoDB 连接"""
        try:
            from pymongo import MongoClient
            
            self.client = MongoClient(self.connection_params.get('uri'))
            self.connection = self.client[self.connection_params.get('database')]
            print(f"✓ 成功连接到 MongoDB 数据库: {self.connection_params.get('database')}")
        except Exception as e:
            raise ConnectionError(f"MongoDB 连接失败: {str(e)}")
    
    def disconnect(self) -> None:
        """关闭 MongoDB 连接"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
            print("✓ MongoDB 连接已关闭")
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """执行 MongoDB 查询（这里使用集合名和过滤器）"""
        # MongoDB 查询方式不同，这里简化处理
        return []
    
    def get_schema(self) -> Dict[str, Any]:
        """获取 MongoDB collections 信息"""
        if not self.connection:
            self.connect()
        
        collections = self.connection.list_collection_names()
        
        schema = {}
        for collection_name in collections:
            schema[collection_name] = self.get_table_info(collection_name)
        
        return schema
    
    def get_table_info(self, collection_name: str) -> Dict[str, Any]:
        """获取集合信息（采样获取字段）"""
        if not self.connection:
            self.connect()
        
        collection = self.connection[collection_name]
        sample_doc = collection.find_one()
        
        if sample_doc:
            fields = {key: type(value).__name__ for key, value in sample_doc.items()}
            return {'fields': fields, 'sample_count': collection.count_documents({})}
        
        return {'fields': {}, 'sample_count': 0}
