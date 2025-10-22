#!/usr/bin/env python
"""数据源导入脚本 - 批量导入多个数据源到知识库"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.datasource_config import get_datasource_manager
from src.vectorstore.knowledge_base_manager import get_knowledge_base_manager
from src.utils.logger import log
from langchain.embeddings import OpenAIEmbeddings
from src.utils.config import settings


def import_all_datasources(force: bool = False):
    """
    导入所有启用的数据源

    Args:
        force: 是否强制重新导入
    """
    print("\n" + "=" * 80)
    print("🚀 批量导入数据源到知识库")
    print("=" * 80)

    try:
        # 1. 加载数据源配置
        print("\n📋 步骤 1: 加载数据源配置")
        print("-" * 80)
        datasource_manager = get_datasource_manager()
        datasource_manager.list_datasources()

        # 2. 创建嵌入模型
        print("\n🤖 步骤 2: 初始化嵌入模型")
        print("-" * 80)
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        print(f"✓ 使用嵌入模型: {settings.embedding_model}")

        # 3. 创建知识库管理器
        print("\n📚 步骤 3: 创建知识库管理器")
        print("-" * 80)
        kb_manager = get_knowledge_base_manager(
            datasource_manager=datasource_manager,
            embedding_model=embeddings
        )
        print("✓ 知识库管理器已创建")

        # 4. 初始化所有知识库
        print("\n🔧 步骤 4: 初始化知识库")
        print("-" * 80)
        kb_manager.initialize_all(force=force)

        # 5. 显示结果
        kb_manager.list_knowledge_bases()

        print("\n" + "=" * 80)
        print("✅ 所有数据源导入完成！")
        print("=" * 80 + "\n")

    except Exception as e:
        log.error(f"导入失败: {str(e)}")
        print(f"\n❌ 错误: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def import_single_datasource(datasource_name: str, force: bool = False):
    """
    导入单个数据源

    Args:
        datasource_name: 数据源名称
        force: 是否强制重新导入
    """
    print("\n" + "=" * 80)
    print(f"🚀 导入数据源: {datasource_name}")
    print("=" * 80)

    try:
        # 1. 加载数据源配置
        datasource_manager = get_datasource_manager()

        # 检查数据源是否存在
        datasource = datasource_manager.get_datasource_by_name(datasource_name)
        if not datasource:
            print(f"\n❌ 错误: 数据源 '{datasource_name}' 不存在\n")
            print("可用的数据源:")
            datasource_manager.list_datasources()
            sys.exit(1)

        if not datasource.enabled:
            print(f"\n⚠️  警告: 数据源 '{datasource_name}' 未启用")
            response = input("是否继续导入？(y/n): ")
            if response.lower() != 'y':
                print("已取消")
                sys.exit(0)

        # 2. 创建嵌入模型
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )

        # 3. 创建知识库管理器
        kb_manager = get_knowledge_base_manager(
            datasource_manager=datasource_manager,
            embedding_model=embeddings
        )

        # 4. 初始化知识库
        kb_manager.initialize_knowledge_base(datasource_name, force=force)

        print("\n" + "=" * 80)
        print(f"✅ 数据源 '{datasource_name}' 导入完成！")
        print("=" * 80 + "\n")

    except Exception as e:
        log.error(f"导入失败: {str(e)}")
        print(f"\n❌ 错误: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def list_datasources():
    """列出所有数据源"""
    try:
        datasource_manager = get_datasource_manager()
        datasource_manager.list_datasources()
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}\n")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="数据源导入工具 - 将数据库导入到知识库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 导入所有启用的数据源
  python scripts/import_datasources.py --all

  # 导入指定数据源
  python scripts/import_datasources.py --datasource company_main_db

  # 强制重新导入（覆盖已有数据）
  python scripts/import_datasources.py --all --force

  # 列出所有数据源
  python scripts/import_datasources.py --list
        """
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='导入所有启用的数据源'
    )

    parser.add_argument(
        '--datasource',
        type=str,
        help='指定要导入的数据源名称'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新导入（覆盖已有数据）'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有数据源'
    )

    args = parser.parse_args()

    # 检查参数
    if args.list:
        list_datasources()
    elif args.all:
        import_all_datasources(force=args.force)
    elif args.datasource:
        import_single_datasource(args.datasource, force=args.force)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

