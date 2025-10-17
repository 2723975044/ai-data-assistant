"""文档处理模块"""
from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def process_database_schema(self, schema: Dict[str, Any]) -> List[Document]:
        """
        处理数据库 schema，转换为文档
        
        Args:
            schema: 数据库结构信息
            
        Returns:
            文档列表
        """
        documents = []
        
        for table_name, table_info in schema.items():
            # 构建表信息文本
            text = f"表名: {table_name}\n\n"
            
            if 'comment' in table_info:
                text += f"说明: {table_info['comment']}\n\n"
            
            text += "字段信息:\n"
            
            columns = table_info.get('columns', {})
            for col_name, col_info in columns.items():
                col_type = col_info.get('type', '')
                col_comment = col_info.get('comment', '')
                col_nullable = col_info.get('nullable', False)
                col_key = col_info.get('key', '')
                
                text += f"  - {col_name} ({col_type})"
                
                if col_key:
                    text += f" [{col_key}]"
                if not col_nullable:
                    text += " [NOT NULL]"
                if col_comment:
                    text += f": {col_comment}"
                
                text += "\n"
            
            # 创建文档
            doc = Document(
                page_content=text,
                metadata={
                    "source": "database_schema",
                    "table_name": table_name,
                    "type": "schema"
                }
            )
            
            documents.append(doc)
        
        return documents
    
    def process_sample_data(
        self,
        table_name: str,
        sample_data: List[Dict[str, Any]]
    ) -> List[Document]:
        """
        处理示例数据
        
        Args:
            table_name: 表名
            sample_data: 示例数据
            
        Returns:
            文档列表
        """
        if not sample_data:
            return []
        
        # 构建示例数据文本
        text = f"表 {table_name} 的示例数据:\n\n"
        
        for i, row in enumerate(sample_data, 1):
            text += f"记录 {i}:\n"
            for key, value in row.items():
                text += f"  {key}: {value}\n"
            text += "\n"
        
        doc = Document(
            page_content=text,
            metadata={
                "source": "sample_data",
                "table_name": table_name,
                "type": "data"
            }
        )
        
        return [doc]
    
    def process_text_documents(self, texts: List[str]) -> List[Document]:
        """
        处理文本文档
        
        Args:
            texts: 文本列表
            
        Returns:
            分块后的文档列表
        """
        documents = []
        
        for i, text in enumerate(texts):
            doc = Document(
                page_content=text,
                metadata={"source": f"text_{i}"}
            )
            documents.append(doc)
        
        # 分块
        split_docs = self.text_splitter.split_documents(documents)
        
        return split_docs
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分割文档
        
        Args:
            documents: 文档列表
            
        Returns:
            分块后的文档列表
        """
        return self.text_splitter.split_documents(documents)
