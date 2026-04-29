"""Basic functionality test without API key."""

from semantic_toolkit.keyword_recognition import (
    extract_chinese_keywords,
    extract_english_keywords,
    extract_keywords,
    Language,
)


def test_chinese_keywords_without_api():
    """Test Chinese keyword extraction using fallback mechanism."""
    print("=" * 60)
    print("中文关键词提取测试 (使用分词回退机制)")
    print("=" * 60)

    chinese_text = """
    深度学习是机器学习的一个分支，它模仿人脑的神经网络结构。
    卷积神经网络在图像识别领域表现出色，而循环神经网络
    则在自然语言处理中有广泛应用。这些算法通过大量的
    数据训练，能够自动学习特征表示。
    """

    print(f"\n测试文本: {chinese_text[:50]}...")

    # 这个测试会失败，因为需要jieba，但我们可以在测试环境中演示
    try:
        result = extract_chinese_keywords(
            chinese_text,
            num_keywords=5,
            use_segmentation=True
        )

        print(f"\n提取结果:")
        print(f"  语言: {result.language}")
        print(f"  关键词数量: {result.summary['total_keywords']}")
        print(f"  平均置信度: {result.summary['average_confidence']:.2f}")

        print(f"\n前5个关键词:")
        for kw in result.get_top_keywords(5):
            print(f"  - {kw.text:15} (置信度: {kw.confidence:.2f}, 分类: {kw.category})")

    except Exception as e:
        print(f"\n预期错误 (需要jieba包): {e}")
        print("提示: 这是正常的，因为LLM回退需要jieba分词工具")


def test_english_keywords_without_api():
    """Test English keyword extraction using fallback mechanism."""
    print("\n" + "=" * 60)
    print("英文关键词提取测试 (使用NLTK回退机制)")
    print("=" * 60)

    english_text = """
    Deep learning is a subset of machine learning that mimics the structure
    of the human brain's neural networks. Convolutional neural networks excel
    in image recognition, while recurrent neural networks are widely used
    in natural language processing. These algorithms learn feature
    representations automatically through extensive data training.
    """

    print(f"\n测试文本: {english_text[:50]}...")

    try:
        result = extract_english_keywords(
            english_text,
            num_keywords=5,
            use_pos_tagging=True
        )

        print(f"\n提取结果:")
        print(f"  语言: {result.language}")
        print(f"  关键词数量: {result.summary['total_keywords']}")
        print(f"  平均置信度: {result.summary['average_confidence']:.2f}")

        print(f"\n前5个关键词:")
        for kw in result.get_top_keywords(5):
            print(f"  - {kw.text:20} (置信度: {kw.confidence:.2f}, 分类: {kw.category})")

        print(f"\n分类统计:")
        for category, count in result.summary['categories'].items():
            print(f"  - {category}: {count}")

    except Exception as e:
        print(f"\n错误: {e}")


def test_unified_interface():
    """Test unified interface."""
    print("\n" + "=" * 60)
    print("统一接口测试")
    print("=" * 60)

    # 中文测试
    print("\n1. 中文文本测试:")
    try:
        result = extract_keywords(
            "机器学习算法研究",
            language=Language.CHINESE
        )
        print(f"   关键词: {[kw.text for kw in result.keywords[:3]]}")
    except Exception as e:
        print(f"   错误: {e}")

    # 英文测试
    print("\n2. 英文文本测试:")
    try:
        result = extract_keywords(
            "machine learning research",
            language=Language.ENGLISH
        )
        print(f"   关键词: {[kw.text for kw in result.keywords[:3]]}")
    except Exception as e:
        print(f"   错误: {e}")


def main():
    """Run basic functionality tests."""
    print("科技文献关键词识别工具 - 基本功能测试")
    print("注意: 此测试使用回退机制，不需要API密钥")
    print("=" * 60)

    try:
        test_chinese_keywords_without_api()
        test_english_keywords_without_api()
        test_unified_interface()

        print("\n" + "=" * 60)
        print("基本功能测试完成!")
        print("=" * 60)
        print("\n提示: 如需使用LLM增强功能，请:")
        print("1. 在 .env 文件中设置 ZHIPU_API_KEY")
        print("2. 运行: python example_keyword.py")

    except Exception as e:
        print(f"\n测试失败: {e}")


if __name__ == "__main__":
    main()
