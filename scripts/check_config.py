#!/usr/bin/env python
"""配置验证脚本 - 检查环境配置是否正确"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_env_file():
    """检查 .env 文件"""
    print("\n" + "=" * 80)
    print("📋 检查环境变量配置")
    print("=" * 80)

    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if not env_file.exists():
        print("❌ .env 文件不存在")
        if env_example.exists():
            print("💡 提示: 请复制 .env.example 为 .env 并填写配置")
            print(f"   cp {env_example} {env_file}")
        return False

    print("✓ .env 文件存在")

    # 检查必需的环境变量
    from dotenv import load_dotenv
    load_dotenv(env_file)

    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key（用于嵌入和 LLM）',
    }

    optional_vars = {
        'MYSQL_HOST': 'MySQL 主机地址',
        'MYSQL_USER': 'MySQL 用户名',
        'MYSQL_PASSWORD': 'MySQL 密码',
        'MYSQL_DATABASE': 'MySQL 数据库名',
        'POSTGRES_HOST': 'PostgreSQL 主机地址',
        'MONGODB_URI': 'MongoDB 连接 URI',
    }

    print("\n必需的环境变量:")
    all_required_set = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value and value != f'your_{var.lower()}_here':
            print(f"  ✓ {var}: 已设置")
        else:
            print(f"  ❌ {var}: 未设置 ({desc})")
            all_required_set = False

    print("\n可选的环境变量:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value and not value.startswith('your_'):
            print(f"  ✓ {var}: 已设置")
        else:
            print(f"  ⚠️  {var}: 未设置 ({desc})")

    return all_required_set


def check_datasource_config():
    """检查数据源配置文件"""
    print("\n" + "=" * 80)
    print("📊 检查数据源配置")
    print("=" * 80)

    config_file = project_root / "config" / "datasources.yaml"

    if not config_file.exists():
        print("❌ config/datasources.yaml 文件不存在")
        return False

    print("✓ datasources.yaml 文件存在")

    try:
        from src.utils.datasource_config import DataSourceManager

        manager = DataSourceManager()
        datasources = manager.get_all_datasources()

        print(f"\n找到 {len(datasources)} 个数据源配置:")

        for ds in datasources:
            status = "✓ 启用" if ds.enabled else "✗ 禁用"
            print(f"  {status} {ds.display_name} ({ds.type})")

        enabled_count = len(manager.get_enabled_datasources())
        print(f"\n启用的数据源: {enabled_count} 个")

        return enabled_count > 0

    except Exception as e:
        print(f"❌ 加载配置失败: {str(e)}")
        return False


def check_database_connections():
    """检查数据库连接"""
    print("\n" + "=" * 80)
    print("🔌 检查数据库连接")
    print("=" * 80)

    try:
        from src.utils.datasource_config import get_datasource_manager
        from src.database.factory import DatabaseFactory

        manager = get_datasource_manager()
        enabled_datasources = manager.get_enabled_datasources()

        if not enabled_datasources:
            print("⚠️  没有启用的数据源")
            return True

        success_count = 0

        for ds in enabled_datasources:
            print(f"\n测试连接: {ds.display_name} ({ds.type})")
            try:
                db = DatabaseFactory.create_database(ds.type, ds.connection)
                with db:
                    schema = db.get_schema()
                    print(f"  ✓ 连接成功，找到 {len(schema)} 个表/集合")
                    success_count += 1
            except Exception as e:
                print(f"  ❌ 连接失败: {str(e)}")

        print(f"\n成功连接: {success_count}/{len(enabled_datasources)}")
        return success_count == len(enabled_datasources)

    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n" + "=" * 80)
    print("📦 检查依赖包")
    print("=" * 80)

    required_packages = {
        'langchain': 'LangChain 框架',
        'openai': 'OpenAI SDK',
        'chromadb': 'Chroma 向量数据库',
        'pydantic': 'Pydantic 数据验证',
        'fastapi': 'FastAPI 框架',
        'uvicorn': 'ASGI 服务器',
        'pyyaml': 'YAML 解析',
        'python-dotenv': '环境变量加载',
    }

    optional_packages = {
        'pymysql': 'MySQL 支持',
        'psycopg2': 'PostgreSQL 支持',
        'pymongo': 'MongoDB 支持',
        'faiss-cpu': 'FAISS 向量数据库',
    }

    print("\n必需的依赖包:")
    all_installed = True
    for package, desc in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package}: 已安装")
        except ImportError:
            print(f"  ❌ {package}: 未安装 ({desc})")
            all_installed = False

    print("\n可选的依赖包:")
    for package, desc in optional_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package}: 已安装")
        except ImportError:
            print(f"  ⚠️  {package}: 未安装 ({desc})")

    return all_installed


def check_directories():
    """检查必要的目录"""
    print("\n" + "=" * 80)
    print("📁 检查目录结构")
    print("=" * 80)

    required_dirs = [
        'config',
        'data',
        'data/chroma',
        'logs',
        'scripts',
        'examples',
    ]

    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ (不存在)")
            all_exist = False
            # 尝试创建
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"     已自动创建")
            except Exception as e:
                print(f"     创建失败: {str(e)}")

    return all_exist


def check_vector_store():
    """检查向量数据库"""
    print("\n" + "=" * 80)
    print("🔍 检查向量数据库")
    print("=" * 80)

    chroma_dir = project_root / "data" / "chroma"

    if not chroma_dir.exists():
        print("⚠️  向量数据库目录不存在")
        print("💡 提示: 请先运行导入脚本创建知识库")
        print("   python scripts/import_datasources.py --all")
        return False

    # 检查是否有集合
    collections = list(chroma_dir.glob("*"))
    if collections:
        print(f"✓ 找到 {len(collections)} 个向量集合:")
        for col in collections[:5]:  # 只显示前5个
            print(f"  - {col.name}")
        if len(collections) > 5:
            print(f"  ... 还有 {len(collections) - 5} 个")
    else:
        print("⚠️  没有找到向量集合")
        print("💡 提示: 请先运行导入脚本创建知识库")

    return len(collections) > 0


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🔍 AI 数据助手 - 配置检查工具")
    print("=" * 80)

    results = {
        '依赖包': check_dependencies(),
        '目录结构': check_directories(),
        '环境变量': check_env_file(),
        '数据源配置': check_datasource_config(),
        '数据库连接': check_database_connections(),
        '向量数据库': check_vector_store(),
    }

    # 总结
    print("\n" + "=" * 80)
    print("📊 检查结果汇总")
    print("=" * 80)

    for check_name, result in results.items():
        status = "✓ 通过" if result else "❌ 失败"
        print(f"  {status} {check_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有检查通过！系统已准备就绪")
        print("=" * 80)
        print("\n下一步:")
        print("1. 运行导入脚本: python scripts/import_datasources.py --all")
        print("2. 启动 API 服务: python -m src.api.main")
        print("3. 访问文档: http://localhost:8000/docs")
    else:
        print("⚠️  部分检查未通过，请根据上述提示修复问题")
        print("=" * 80)
        print("\n常见问题:")
        print("1. 缺少 .env 文件: cp .env.example .env")
        print("2. 缺少依赖包: pip install -r requirements.txt")
        print("3. 数据库连接失败: 检查数据库配置和网络连接")
        print("4. 没有向量数据: python scripts/import_datasources.py --all")

    print("=" * 80 + "\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

