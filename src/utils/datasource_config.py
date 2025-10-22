"""数据源配置管理模块"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

import yaml


@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str
    display_name: str
    description: str
    type: str
    enabled: bool
    connection: Dict[str, Any]
    knowledge_base: Dict[str, Any]

    def get_collection_name(self) -> str:
        """获取知识库集合名称"""
        return self.knowledge_base.get('collection_name', f'kb_{self.name}')

    def should_include_sample_data(self) -> bool:
        """是否包含示例数据"""
        return self.knowledge_base.get('include_sample_data', True)

    def get_sample_data_limit(self) -> int:
        """获取示例数据限制"""
        return self.knowledge_base.get('sample_data_limit', 5)

    def get_include_tables(self) -> Optional[List[str]]:
        """获取要包含的表列表"""
        return self.knowledge_base.get('include_tables')

    def get_exclude_tables(self) -> Optional[List[str]]:
        """获取要排除的表列表"""
        return self.knowledge_base.get('exclude_tables')


class DataSourceManager:
    """数据源配置管理器"""

    def __init__(self, config_path: str = None):
        """
        初始化数据源管理器

        Args:
            config_path: 配置文件路径，默认为 config/datasources.yaml
        """
        if config_path is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "datasources.yaml"

        self.config_path = Path(config_path)
        self.config_data = None
        self.datasources: List[DataSourceConfig] = []

        # 加载配置
        self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config_data = yaml.safe_load(f)

        # 解析数据源配置
        self._parse_datasources()

        print(f"✓ 已加载配置文件: {self.config_path}")
        print(f"✓ 找到 {len(self.datasources)} 个数据源配置")

    def _parse_datasources(self) -> None:
        """解析数据源配置"""
        datasources_config = self.config_data.get('datasources', [])

        for ds_config in datasources_config:
            # 替换环境变量
            connection = self._replace_env_vars(ds_config.get('connection', {}))

            datasource = DataSourceConfig(
                name=ds_config['name'],
                display_name=ds_config.get('display_name', ds_config['name']),
                description=ds_config.get('description', ''),
                type=ds_config['type'],
                enabled=ds_config.get('enabled', True),
                connection=connection,
                knowledge_base=ds_config.get('knowledge_base', {})
            )

            self.datasources.append(datasource)

    def _replace_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        替换配置中的环境变量

        Args:
            config: 配置字典

        Returns:
            替换后的配置
        """
        result = {}
        for key, value in config.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # 提取环境变量名
                env_var = value[2:-1]
                result[key] = os.getenv(env_var, value)
            elif isinstance(value, dict):
                result[key] = self._replace_env_vars(value)
            else:
                result[key] = value
        return result

    def get_all_datasources(self) -> List[DataSourceConfig]:
        """获取所有数据源配置"""
        return self.datasources

    def get_enabled_datasources(self) -> List[DataSourceConfig]:
        """获取所有启用的数据源"""
        return [ds for ds in self.datasources if ds.enabled]

    def get_datasource_by_name(self, name: str) -> Optional[DataSourceConfig]:
        """
        根据名称获取数据源配置

        Args:
            name: 数据源名称

        Returns:
            数据源配置，如果不存在返回 None
        """
        for ds in self.datasources:
            if ds.name == name:
                return ds
        return None

    def get_datasources_by_type(self, db_type: str) -> List[DataSourceConfig]:
        """
        根据类型获取数据源列表

        Args:
            db_type: 数据库类型 (mysql, postgres, mongodb)

        Returns:
            数据源配置列表
        """
        return [ds for ds in self.datasources if ds.type.lower() == db_type.lower()]

    def get_vector_store_config(self) -> Dict[str, Any]:
        """获取向量数据库配置"""
        return self.config_data.get('vector_store', {})

    def get_embedding_config(self) -> Dict[str, Any]:
        """获取嵌入模型配置"""
        return self.config_data.get('embedding', {})

    def get_rag_config(self) -> Dict[str, Any]:
        """获取 RAG 配置"""
        return self.config_data.get('rag', {})

    def list_datasources(self) -> None:
        """打印所有数据源信息"""
        print("\n" + "=" * 80)
        print("📊 数据源配置列表")
        print("=" * 80)

        for i, ds in enumerate(self.datasources, 1):
            status = "✓ 启用" if ds.enabled else "✗ 禁用"
            print(f"\n{i}. {ds.display_name} ({ds.name})")
            print(f"   类型: {ds.type}")
            print(f"   状态: {status}")
            print(f"   描述: {ds.description}")
            print(f"   知识库: {ds.get_collection_name()}")

        print("\n" + "=" * 80)


# 全局数据源管理器实例
_datasource_manager = None


def get_datasource_manager(config_path: str = None) -> DataSourceManager:
    """
    获取全局数据源管理器实例

    Args:
        config_path: 配置文件路径

    Returns:
        数据源管理器实例
    """
    global _datasource_manager

    if _datasource_manager is None:
        _datasource_manager = DataSourceManager(config_path)

    return _datasource_manager

