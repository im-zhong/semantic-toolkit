"""Example usage of the Keyword Recognition API."""

import requests
import json


def example_chinese_keyword_extraction():
    """Example: Extract keywords from Chinese text."""
    print("=" * 60)
    print("中文关键词提取示例")
    print("=" * 60)

    url = "http://localhost:8000/api/v1/keywords/chinese"
    payload = {
        "text": "深度学习是机器学习的一个分支，它模仿人脑的神经网络结构。卷积神经网络在图像识别领域表现出色，而循环神经网络则在自然语言处理中有广泛应用。",
        "num_keywords": 5,
        "use_segmentation": True,
    }

    print(f"\n请求URL: {url}")
    print(f"请求数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        print(f"\n响应状态: {response.status_code}")
        print(f"\n提取结果:")
        print(f"  语言: {result['language']}")
        print(f"  关键词数量: {result['summary']['total_keywords']}")
        print(f"  平均置信度: {result['summary']['average_confidence']:.2f}")
        print(f"\n关键词列表:")
        for kw in result['keywords']:
            print(f"  - {kw['text']:15} (置信度: {kw['confidence']:.2f}, 分类: {kw['category']})")

    except requests.exceptions.RequestException as e:
        print(f"\n请求失败: {e}")


def example_english_keyword_extraction():
    """Example: Extract keywords from English text."""
    print("\n" + "=" * 60)
    print("英文关键词提取示例")
    print("=" * 60)

    url = "http://localhost:8000/api/v1/keywords/english"
    payload = {
        "text": "Deep learning is a subset of machine learning that mimics the structure of the human brain's neural networks. Convolutional neural networks excel in image recognition, while recurrent neural networks are widely used in natural language processing.",
        "num_keywords": 5,
        "use_pos_tagging": True,
    }

    print(f"\n请求URL: {url}")
    print(f"请求数据: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        print(f"\n响应状态: {response.status_code}")
        print(f"\n提取结果:")
        print(f"  语言: {result['language']}")
        print(f"  关键词数量: {result['summary']['total_keywords']}")
        print(f"  平均置信度: {result['summary']['average_confidence']:.2f}")
        print(f"\n关键词列表:")
        for kw in result['keywords']:
            print(f"  - {kw['text']:30} (置信度: {kw['confidence']:.2f}, 分类: {kw['category']})")

    except requests.exceptions.RequestException as e:
        print(f"\n请求失败: {e}")


def example_unified_interface():
    """Example: Use unified interface for keyword extraction."""
    print("\n" + "=" * 60)
    print("统一接口示例")
    print("=" * 60)

    # Chinese example
    url = "http://localhost:8000/api/v1/keywords"
    payload = {
        "text": "机器学习算法在医疗诊断中的应用研究",
        "language": "chinese",
        "num_keywords": 5,
    }

    print(f"\n中文文本示例:")
    print(f"  URL: {url}")
    print(f"  数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"  关键词: {[kw['text'] for kw in result['keywords']]}")
    except requests.exceptions.RequestException as e:
        print(f"  请求失败: {e}")

    # English example
    payload = {
        "text": "Machine learning algorithms for medical diagnosis",
        "language": "english",
        "num_keywords": 5,
    }

    print(f"\n英文文本示例:")
    print(f"  数据: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"  关键词: {[kw['text'] for kw in result['keywords']]}")
    except requests.exceptions.RequestException as e:
        print(f"  请求失败: {e}")


def example_get_system_info():
    """Example: Get system information."""
    print("\n" + "=" * 60)
    print("系统信息示例")
    print("=" * 60)

    # Get supported languages
    print("\n1. 支持的语言:")
    try:
        response = requests.get("http://localhost:8000/api/v1/languages")
        response.raise_for_status()
        languages = response.json()["languages"]
        for lang in languages:
            print(f"   - {lang['code']:8} ({lang['name']} - {lang['native_name']})")
    except requests.exceptions.RequestException as e:
        print(f"   请求失败: {e}")

    # Get keyword categories
    print("\n2. 关键词分类:")
    try:
        response = requests.get("http://localhost:8000/api/v1/categories")
        response.raise_for_status()
        categories = response.json()["categories"]
        for cat in categories:
            print(f"   - {cat['code']:12} {cat['description']}")
    except requests.exceptions.RequestException as e:
        print(f"   请求失败: {e}")


def example_health_check():
    """Example: Health check."""
    print("\n" + "=" * 60)
    print("健康检查示例")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:8000/health")
        response.raise_for_status()
        result = response.json()
        print(f"\nAPI状态: {result['status']}")
        print(f"服务名称: {result['service']}")
        print("\nAPI运行正常！")
    except requests.exceptions.RequestException as e:
        print(f"\nAPI可能未启动或不可用: {e}")


def main():
    """Run all API examples."""
    print("关键词识别API使用示例")
    print("注意: 请确保API服务已启动 (python -m semantic_toolkit.api)")
    print("=" * 60)

    try:
        example_health_check()
        example_chinese_keyword_extraction()
        example_english_keyword_extraction()
        example_unified_interface()
        example_get_system_info()

        print("\n" + "=" * 60)
        print("所有示例执行完成!")
        print("=" * 60)
        print("\nAPI文档地址: http://localhost:8000/docs")
        print("交互式文档: http://localhost:8000/redoc")

    except KeyboardInterrupt:
        print("\n\n示例执行被中断")


if __name__ == "__main__":
    main()
