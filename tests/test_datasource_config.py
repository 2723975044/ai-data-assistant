"""测试数据源配置管理模块"""
import os
import tempfile

import pytest
import yaml

from src.utils.datasource_config import DataSourceConfig, DataSourceManager


class TestDataSourceConfig:
    """测试 DataSourceConfig 类"""

    def test_get_collection_name(self):
        """测试获取集合名称"""
        config = DataSourceConfig(
            name="test_db",
            display_name="测试数据库",
            description="测试",
            type="mysql",
            enabled=True,
            connection={},
            knowledge_base={"collection_name": "kb_test"}
        )

        assert config.get_collection_name() == "kb_test"

    def test_get_collection_name_default(self):
        """测试默认集合名称"""
        config = DataSourceConfig(
            name="test_db",
            display_name="测试数据库",
            description="测试",
            type="mysql",
            enabled=True,
            connection={},
            knowledge_base={}
        )

        assert config.get_collection_name() == "kb_test_db"

    def test_should_include_sample_data(self):
        """测试是否包含示例数据"""
        config = DataSourceConfig(
            name="test_db",
            display_name="测试数据库",
            description="测试",
            type="mysql",
            enabled=True,
            connection={},
            knowledge_base={"include_sample_data": False}
        )

        assert config.should_include_sample_data() is False

    def test_get_sample_data_limit(self):
        """测试获取示例数据限制"""
        config = DataSourceConfig(
            name="test_db",
            display_name="测试数据库",
            description="测试",
            type="mysql",
            enabled=True,
            connection={},
            knowledge_base={"sample_data_limit": 10}
        )

        assert config.get_sample_data_limit() == 10


class TestDataSourceManager:
    """测试 DataSourceManager 类"""

    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件"""
        config_data = {
            'datasources': [
                {
                    'name': 'test_db_1',
                    'display_name': '测试数据库1',
                    'description': '测试描述1',
                    'type': 'mysql',
                    'enabled': True,
                    'connection': {
                        'host': 'localhost',
                        'port': 3306,
                        'user': 'root',
                        'password': 'password',
                        'database': 'test_db'
                    },
                    'knowledge_base': {
                        'collection_name': 'kb_test_1'
                    }
                },
                {
                    'name': 'test_db_2',
                    'display_name': '测试数据库2',
                    'description': '测试描述2',
                    'type': 'postgres',
                    'enabled': False,
                    'connection': {
                        'host': 'localhost',
                        'port': 5432,
                        'user': 'postgres',
                        'password': 'password',
                        'database': 'test_db'
                    },
                    'knowledge_base': {
                        'collection_name': 'kb_test_2'
                    }
                }
            ],
            'vector_store': {
                'type': 'chroma',
                'persist_directory': './data/chroma'
            },
            'embedding': {
                'provider': 'openai',
                'model': 'text-embedding-ada-002'
            },
            'rag': {
                'chunk_size': 1000,
                'chunk_overlap': 200
            }
        }

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f, allow_unicode=True)
            temp_file = f.name

        yield temp_file

        # 清理
        os.unlink(temp_file)

    def test_load_config(self, temp_config_file):
        """测试加载配置"""
        manager = DataSourceManager(temp_config_file)

        assert len(manager.datasources) == 2
        assert manager.config_data is not None

    def test_get_all_datasources(self, temp_config_file):
        """测试获取所有数据源"""
        manager = DataSourceManager(temp_config_file)
        datasources = manager.get_all_datasources()

        assert len(datasources) == 2
        assert datasources[0].name == 'test_db_1'
        assert datasources[1].name == 'test_db_2'

    def test_get_enabled_datasources(self, temp_config_file):
        """测试获取启用的数据源"""
        manager = DataSourceManager(temp_config_file)
        enabled = manager.get_enabled_datasources()

        assert len(enabled) == 1
        assert enabled[0].name == 'test_db_1'
        assert enabled[0].enabled is True

    def test_get_datasource_by_name(self, temp_config_file):
        """测试根据名称获取数据源"""
        manager = DataSourceManager(temp_config_file)

        ds = manager.get_datasource_by_name('test_db_1')
        assert ds is not None
        assert ds.name == 'test_db_1'
        assert ds.display_name == '测试数据库1'

        ds_not_exist = manager.get_datasource_by_name('not_exist')
        assert ds_not_exist is None

    def test_get_datasources_by_type(self, temp_config_file):
        """测试根据类型获取数据源"""
        manager = DataSourceManager(temp_config_file)

        mysql_datasources = manager.get_datasources_by_type('mysql')
        assert len(mysql_datasources) == 1
        assert mysql_datasources[0].type == 'mysql'

        postgres_datasources = manager.get_datasources_by_type('postgres')
        assert len(postgres_datasources) == 1
        assert postgres_datasources[0].type == 'postgres'

    def test_get_vector_store_config(self, temp_config_file):
        """测试获取向量数据库配置"""
        manager = DataSourceManager(temp_config_file)
        config = manager.get_vector_store_config()

        assert config['type'] == 'chroma'
        assert config['persist_directory'] == './data/chroma'

    def test_get_embedding_config(self, temp_config_file):
        """测试获取嵌入模型配置"""
        manager = DataSourceManager(temp_config_file)
        config = manager.get_embedding_config()

        assert config['provider'] == 'openai'
        assert config['model'] == 'text-embedding-ada-002'

    def test_get_rag_config(self, temp_config_file):
        """测试获取 RAG 配置"""
        manager = DataSourceManager(temp_config_file)
        config = manager.get_rag_config()

        assert config['chunk_size'] == 1000
        assert config['chunk_overlap'] == 200

    def test_replace_env_vars(self, temp_config_file):
        """测试环境变量替换"""
        # 设置测试环境变量
        os.environ['TEST_HOST'] = 'test.example.com'
        os.environ['TEST_PORT'] = '3306'

        manager = DataSourceManager(temp_config_file)

        config = {
            'host': '${TEST_HOST}',
            'port': '${TEST_PORT}',
            'user': 'root'
        }

        result = manager._replace_env_vars(config)

        assert result['host'] == 'test.example.com'
        assert result['port'] == '3306'
        assert result['user'] == 'root'

        # 清理环境变量
        del os.environ['TEST_HOST']
        del os.environ['TEST_PORT']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

