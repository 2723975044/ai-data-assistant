#!/usr/bin/env python
"""API 客户端使用示例 - 演示如何调用 API 接口"""
import requests

# API 基础地址
BASE_URL = "http://localhost:8000"


def example_1_health_check():
    """示例 1: 健康检查"""
    print("\n" + "=" * 80)
    print("示例 1: 健康检查")
    print("=" * 80)

    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def example_2_list_knowledge_bases():
    """示例 2: 获取知识库列表"""
    print("\n" + "=" * 80)
    print("示例 2: 获取知识库列表")
    print("=" * 80)

    response = requests.get(f"{BASE_URL}/knowledge-bases")

    if response.status_code == 200:
        data = response.json()
        print(f"找到 {data['total']} 个知识库:\n")

        for kb in data['knowledge_bases']:
            print(f"名称: {kb['display_name']}")
            print(f"  数据源: {kb['name']}")
            print(f"  类型: {kb['db_type']}")
            print(f"  集合: {kb['collection_name']}")
            print(f"  状态: {'已初始化' if kb['is_initialized'] else '未初始化'}")
            print()
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text)


def example_3_search_all_knowledge_bases():
    """示例 3: 搜索所有知识库"""
    print("\n" + "=" * 80)
    print("示例 3: 搜索所有知识库")
    print("=" * 80)

    query = "用户表有哪些字段"

    payload = {
        "query": query,
        "top_k": 3
    }

    print(f"查询: {query}\n")

    response = requests.post(
        f"{BASE_URL}/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"找到 {data['total_results']} 个结果\n")

        for kb_name, results in data['results'].items():
            print(f"知识库: {kb_name}")
            print("-" * 60)

            for i, result in enumerate(results, 1):
                print(f"\n结果 {i}:")
                print(f"内容: {result['content'][:150]}...")
                print(f"元数据: {result['metadata']}")
            print()
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text)


def example_4_search_specific_knowledge_base():
    """示例 4: 搜索指定知识库"""
    print("\n" + "=" * 80)
    print("示例 4: 搜索指定知识库")
    print("=" * 80)

    # 先获取知识库列表
    kb_response = requests.get(f"{BASE_URL}/knowledge-bases")
    if kb_response.status_code != 200:
        print("❌ 无法获取知识库列表")
        return

    kb_data = kb_response.json()
    if not kb_data['knowledge_bases']:
        print("⚠️  没有可用的知识库")
        return

    # 使用第一个知识库
    kb_name = kb_data['knowledge_bases'][0]['name']
    query = "订单相关的表"

    payload = {
        "query": query,
        "knowledge_base": kb_name,
        "top_k": 2
    }

    print(f"知识库: {kb_name}")
    print(f"查询: {query}\n")

    response = requests.post(
        f"{BASE_URL}/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()

        for kb_name, results in data['results'].items():
            print(f"找到 {len(results)} 个结果:\n")

            for i, result in enumerate(results, 1):
                print(f"结果 {i}:")
                print(f"  {result['content'][:100]}...")
                print()
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text)


def example_5_intelligent_qa():
    """示例 5: 智能问答"""
    print("\n" + "=" * 80)
    print("示例 5: 智能问答")
    print("=" * 80)

    questions = [
        "数据库中有哪些表？请列出主要的表名。",
        "用户表的结构是什么？包含哪些字段？",
        "订单表和用户表有什么关系？",
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 60)

        payload = {
            "query": question,
            "top_k": 5
        }

        response = requests.post(
            f"{BASE_URL}/query-kb",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"回答: {data['answer']}\n")

            if data.get('sources'):
                print("参考来源:")
                for i, source in enumerate(data['sources'][:2], 1):
                    table_name = source['metadata'].get('table_name', 'N/A')
                    print(f"  {i}. 表: {table_name}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)

        print()


def example_6_query_specific_kb():
    """示例 6: 查询指定知识库"""
    print("\n" + "=" * 80)
    print("示例 6: 查询指定知识库")
    print("=" * 80)

    # 先获取知识库列表
    kb_response = requests.get(f"{BASE_URL}/knowledge-bases")
    if kb_response.status_code != 200:
        print("❌ 无法获取知识库列表")
        return

    kb_data = kb_response.json()
    if not kb_data['knowledge_bases']:
        print("⚠️  没有可用的知识库")
        return

    # 使用第一个知识库
    kb_name = kb_data['knowledge_bases'][0]['name']
    question = "这个数据库的主要功能是什么？有哪些核心表？"

    payload = {
        "query": question,
        "knowledge_base": kb_name,
        "top_k": 5
    }

    print(f"知识库: {kb_name}")
    print(f"问题: {question}\n")

    response = requests.post(
        f"{BASE_URL}/query-kb",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"回答:\n{data['answer']}\n")
        print(f"使用的知识库: {data['knowledge_base']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(response.text)


def example_7_batch_queries():
    """示例 7: 批量查询"""
    print("\n" + "=" * 80)
    print("示例 7: 批量查询")
    print("=" * 80)

    queries = [
        "用户表",
        "订单表",
        "商品表",
        "支付表",
    ]

    print("批量搜索多个关键词:\n")

    for query in queries:
        payload = {
            "query": query,
            "top_k": 1
        }

        response = requests.post(
            f"{BASE_URL}/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✓ {query}: 找到 {data['total_results']} 个结果")
        else:
            print(f"❌ {query}: 查询失败")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🚀 API 客户端使用示例")
    print("=" * 80)
    print("\n⚠️  请确保 API 服务已启动: python -m src.api.main")
    print("   访问 http://localhost:8000/docs 查看完整 API 文档\n")

    try:
        # 运行示例
        example_1_health_check()
        example_2_list_knowledge_bases()
        example_3_search_all_knowledge_bases()
        example_4_search_specific_knowledge_base()
        example_5_intelligent_qa()
        example_6_query_specific_kb()
        example_7_batch_queries()

        print("\n" + "=" * 80)
        print("✅ 所有示例运行完成！")
        print("=" * 80 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到 API 服务")
        print("请确保 API 服务已启动: python -m src.api.main\n")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

