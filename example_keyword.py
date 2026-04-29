"""Example usage of keyword recognition functionality."""

from semantic_toolkit.keyword_recognition import (
    extract_chinese_keywords,
    extract_english_keywords,
    extract_keywords,
    Language,
)


def example_chinese_keyword_extraction():
    """Example: Extract keywords from Chinese scientific literature."""
    print("=" * 60)
    print("Chinese Keyword Extraction Example")
    print("=" * 60)

    # Sample Chinese scientific abstract
    chinese_text = """
    本研究提出了一种基于深度学习的图像识别算法。
    该算法采用卷积神经网络作为基础架构，通过改进的激活函数
    和优化策略，显著提升了图像分类的准确率。实验结果表明，
    该方法在多个公开数据集上都取得了优于现有方法的性能。
    此外，我们还研究了算法在边缘计算设备上的部署问题，
    并提出了一系列轻量化优化方案。
    """

    # Extract keywords
    result = extract_chinese_keywords(
        text=chinese_text,
        num_keywords=10,
        use_segmentation=True
    )

    # Print summary
    print(f"\nSummary:")
    print(f"  Total Keywords: {result.summary['total_keywords']}")
    print(f"  Average Confidence: {result.summary['average_confidence']:.2f}")
    print(f"  Categories: {result.summary['categories']}")

    # Print top keywords
    print(f"\nTop Keywords:")
    for kw in result.get_top_keywords(10):
        print(f"  - {kw.text:20} (confidence: {kw.confidence:.2f}, "
              f"frequency: {kw.frequency}, category: {kw.category})")

    # Get keywords by category
    print(f"\nTechnical Keywords:")
    technical_kws = result.get_keywords_by_category("technical")
    for kw in technical_kws:
        print(f"  - {kw.text} (confidence: {kw.confidence:.2f})")


def example_english_keyword_extraction():
    """Example: Extract keywords from English scientific literature."""
    print("\n" + "=" * 60)
    print("English Keyword Extraction Example")
    print("=" * 60)

    # Sample English scientific abstract
    english_text = """
    This paper presents a novel deep learning approach for image recognition.
    The proposed algorithm utilizes convolutional neural networks with an improved
    activation function and optimization strategy, significantly improving
    classification accuracy. Experimental results demonstrate that our method
    achieves superior performance on multiple public datasets compared to
    existing approaches. Furthermore, we investigate the deployment of the
    algorithm on edge computing devices and propose several lightweight
    optimization schemes.
    """

    # Extract keywords
    result = extract_english_keywords(
        text=english_text,
        num_keywords=10,
        use_pos_tagging=True
    )

    # Print summary
    print(f"\nSummary:")
    print(f"  Total Keywords: {result.summary['total_keywords']}")
    print(f"  Average Confidence: {result.summary['average_confidence']:.2f}")
    print(f"  Categories: {result.summary['categories']}")

    # Print top keywords
    print(f"\nTop Keywords:")
    for kw in result.get_top_keywords(10):
        print(f"  - {kw.text:30} (confidence: {kw.confidence:.2f}, "
              f"frequency: {kw.frequency}, category: {kw.category})")

    # Print abbreviations if any
    print(f"\nAbbreviations:")
    abbreviations = result.get_keywords_by_category("abbreviation")
    for kw in abbreviations:
        print(f"  - {kw.text} (confidence: {kw.confidence:.2f})")


def example_unified_interface():
    """Example: Use unified interface for keyword extraction."""
    print("\n" + "=" * 60)
    print("Unified Interface Example")
    print("=" * 60)

    # Chinese text
    chinese_text = "机器学习算法在医疗诊断中的应用研究"
    print(f"\nChinese text: {chinese_text}")

    result_cn = extract_keywords(
        text=chinese_text,
        language=Language.CHINESE,
        num_keywords=5
    )

    print(f"Extracted keywords: {[kw.text for kw in result_cn.keywords]}")

    # English text
    english_text = "Machine learning algorithms for medical diagnosis"
    print(f"\nEnglish text: {english_text}")

    result_en = extract_keywords(
        text=english_text,
        language=Language.ENGLISH,
        num_keywords=5
    )

    print(f"Extracted keywords: {[kw.text for kw in result_en.keywords]}")


def example_batch_processing():
    """Example: Batch process multiple texts."""
    print("\n" + "=" * 60)
    print("Batch Processing Example")
    print("=" * 60)

    # Multiple texts to process
    texts = [
        "深度学习在自然语言处理中的应用研究",
        "卷积神经网络用于图像分类的方法",
        "强化学习算法在机器人控制中的应用",
    ]

    print("\nProcessing multiple Chinese texts:")
    for idx, text in enumerate(texts, 1):
        print(f"\nText {idx}: {text[:30]}...")

        result = extract_chinese_keywords(text, num_keywords=5)

        print(f"Keywords: {', '.join([kw.text for kw in result.keywords])}")
        top_cat = max(result.summary['categories'].items(), key=lambda x: x[1])[0] if result.summary['categories'] else 'N/A'
        print(f"Top category: {top_cat}")


def example_custom_configuration():
    """Example: Custom configuration for keyword extraction."""
    print("\n" + "=" * 60)
    print("Custom Configuration Example")
    print("=" * 60)

    # Configure extraction with custom parameters
    custom_text = """
    Artificial Intelligence and Machine Learning are transforming
    healthcare through advanced neural networks and deep learning algorithms.
    CNN, RNN, and transformer models enable breakthrough applications
    in medical imaging, drug discovery, and personalized medicine.
    """

    print("\nExtracting with custom configuration:")
    print(f"  Text length: {len(custom_text)} characters")
    print(f"  Target keywords: 8")

    result = extract_english_keywords(
        text=custom_text,
        num_keywords=8,
        use_pos_tagging=True
    )

    print(f"\nResults:")
    print(f"  Extracted: {result.summary['total_keywords']} keywords")
    print(f"  Average confidence: {result.summary['average_confidence']:.2f}")

    print(f"\nCategory breakdown:")
    for category, count in result.summary['categories'].items():
        print(f"  {category}: {count}")


def main():
    """Run all examples."""
    try:
        example_chinese_keyword_extraction()
        example_english_keyword_extraction()
        example_unified_interface()
        example_batch_processing()
        example_custom_configuration()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nNote: Make sure to set up your .env file with ZHIPU_API_KEY")
        print("      and have the required dependencies installed.")


if __name__ == "__main__":
    main()
