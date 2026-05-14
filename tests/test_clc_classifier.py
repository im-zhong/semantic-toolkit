"""CLC分类器核心模块的单元测试"""

import json
from unittest.mock import MagicMock, patch

import pytest

from auto_classifier.algorithms.clc_classifier import (
    normalize_clc_id,
    top_letter,
    clamp,
    truncate_text,
    Category,
    Candidate,
    CategoryStore,
    TfidfCandidateRetriever,
    parse_json_from_llm,
    expand_query_by_rules,
    CLCAutoClassifier,
)


class TestUtilityFunctions:
    """测试工具函数"""

    def test_normalize_clc_id(self):
        """测试分类号标准化"""
        assert normalize_clc_id("TP18") == "TP18"
        assert normalize_clc_id("[TP18]") == "TP18"
        assert normalize_clc_id("{TP18}") == "TP18"
        assert normalize_clc_id("  TP18  ") == "TP18"
        assert normalize_clc_id("") == ""

    def test_top_letter(self):
        """测试提取首字母"""
        assert top_letter("TP18") == "T"
        assert top_letter("N94") == "N"
        assert top_letter("O41") == "O"
        assert top_letter("123") == ""

    def test_clamp(self):
        """测试数值范围限制"""
        assert clamp(0.5) == 0.5
        assert clamp(1.5) == 1.0
        assert clamp(-0.5) == 0.0
        assert clamp(0.5, low=0.2, high=0.8) == 0.5
        assert clamp(1.0, low=0.2, high=0.8) == 0.8
        assert clamp(0.1, low=0.2, high=0.8) == 0.2
        assert clamp("invalid", default=0.5) == 0.5
        assert clamp(None, default=0.5) == 0.5

    def test_truncate_text(self):
        """测试文本截断"""
        short_text = "短文本"
        assert truncate_text(short_text) == "短文本"

        long_text = "A" * 7000
        truncated = truncate_text(long_text, max_chars=6000)
        assert len(truncated) <= 6000 + 50  # 允许一些缓冲
        assert "……【中间内容已截断】……" in truncated

        assert truncate_text("", max_chars=100) == ""
        assert truncate_text(None, max_chars=100) == ""


class TestCategory:
    """测试Category数据类"""

    def test_category_creation(self):
        """测试Category对象创建"""
        cat = Category(
            id="TP18",
            original_id="TP18",
            name="人工智能",
            path_ids=("T", "TP", "TP18"),
            path_names=("工业技术", "自动化技术、计算机技术", "人工智能"),
            top="T",
            depth=3,
            is_leaf=True
        )

        assert cat.id == "TP18"
        assert cat.name == "人工智能"
        assert cat.top == "T"
        assert cat.depth == 3
        assert cat.is_leaf is True

    def test_category_path(self):
        """测试Category路径生成"""
        cat = Category(
            id="TP18",
            original_id="TP18",
            name="人工智能",
            path_ids=("T", "TP", "TP18"),
            path_names=("工业技术", "自动化技术、计算机技术", "人工智能"),
            top="T",
            depth=3,
            is_leaf=True
        )

        path = cat.path
        assert "T 工业技术" in path
        assert "TP 自动化技术、计算机技术" in path
        assert "TP18 人工智能" in path

    def test_category_retrieval_text(self):
        """测试检索文本生成"""
        cat = Category(
            id="TP18",
            original_id="TP18",
            name="人工智能",
            path_ids=("T", "TP", "TP18"),
            path_names=("工业技术", "自动化技术、计算机技术", "人工智能"),
            top="T",
            depth=3,
            is_leaf=True
        )

        retrieval_text = cat.retrieval_text()
        assert "TP18" in retrieval_text
        assert "人工智能" in retrieval_text
        assert "计算机" in retrieval_text


class TestCandidate:
    """测试Candidate数据类"""

    def test_candidate_creation(self):
        """测试Candidate对象创建"""
        cat = Category(
            id="TP18",
            original_id="TP18",
            name="人工智能",
            path_ids=("T", "TP", "TP18"),
            path_names=("工业技术", "自动化技术、计算机技术", "人工智能"),
            top="T",
            depth=3,
            is_leaf=True
        )
        candidate = Candidate(category=cat, score=0.85)

        assert candidate.category.id == "TP18"
        assert candidate.score == 0.85

    def test_candidate_to_prompt_dict(self):
        """测试转换为提示词字典"""
        cat = Category(
            id="TP18",
            original_id="TP18",
            name="人工智能",
            path_ids=("T", "TP", "TP18"),
            path_names=("工业技术", "自动化技术、计算机技术", "人工智能"),
            top="T",
            depth=3,
            is_leaf=True
        )
        candidate = Candidate(category=cat, score=0.85)

        prompt_dict = candidate.to_prompt_dict()
        assert prompt_dict["id"] == "TP18"
        assert prompt_dict["name"] == "人工智能"
        assert prompt_dict["local_score"] == 0.85
        assert "path" in prompt_dict

    def test_candidate_to_result_dict(self):
        """测试转换为结果字典"""
        cat = Category(
            id="TP18",
            original_id="TP18",
            name="人工智能",
            path_ids=("T", "TP", "TP18"),
            path_names=("工业技术", "自动化技术、计算机技术", "人工智能"),
            top="T",
            depth=3,
            is_leaf=True
        )
        candidate = Candidate(category=cat, score=0.85)

        result_dict = candidate.to_result_dict()
        assert result_dict["id"] == "TP18"
        assert result_dict["name"] == "人工智能"
        assert result_dict["local_score"] == 0.85
        assert "path" in result_dict


class TestCategoryStore:
    """测试CategoryStore类"""

    def test_category_store_init_valid_json(self, tmp_path):
        """测试使用有效JSON初始化CategoryStore"""
        json_data = [
            {
                "id": "TP",
                "desc": "自动化技术、计算机技术",
                "children": [
                    {
                        "id": "TP18",
                        "desc": "人工智能",
                        "children": []
                    }
                ]
            }
        ]

        json_file = tmp_path / "test_clc.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False)

        store = CategoryStore(json_path=json_file, scitech_only=False, min_scitech_categories=1)
        assert store.count() >= 1
        assert store.get("TP18") is not None
        assert store.get("TP18").name == "人工智能"

    def test_category_store_file_not_found(self):
        """测试文件不存在时抛出异常"""
        with pytest.raises(FileNotFoundError, match="未找到分类法 JSON"):
            CategoryStore(json_path="nonexistent.json", scitech_only=False, min_scitech_categories=1)

    def test_category_store_invalid_json_structure(self, tmp_path):
        """测试无效的JSON结构"""
        json_file = tmp_path / "test_clc.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({"invalid": "structure"}, f)

        with pytest.raises(ValueError, match="分类法 JSON 顶层应为 list"):
            CategoryStore(json_path=json_file, scitech_only=False, min_scitech_categories=1)

    def test_category_store_get(self, tmp_path):
        """测试获取分类"""
        json_data = [
            {
                "id": "TP",
                "desc": "自动化技术、计算机技术",
                "children": [
                    {
                        "id": "TP18",
                        "desc": "人工智能",
                        "children": []
                    }
                ]
            }
        ]

        json_file = tmp_path / "test_clc.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False)

        store = CategoryStore(json_path=json_file, scitech_only=False, min_scitech_categories=1)

        cat = store.get("TP18")
        assert cat is not None
        assert cat.id == "TP18"

        non_existent = store.get("X999")
        assert non_existent is None


class TestParseJsonFromLlm:
    """测试LLM返回的JSON解析"""

    def test_parse_json_clean(self):
        """测试解析干净的JSON"""
        json_str = '{"key": "value"}'
        result = parse_json_from_llm(json_str)
        assert result == {"key": "value"}

    def test_parse_json_with_code_block(self):
        """测试解析带代码块的JSON"""
        json_str = '''```json
{
  "key": "value"
}
```'''
        result = parse_json_from_llm(json_str)
        assert result == {"key": "value"}

    def test_parse_json_with_text(self):
        """测试解析带前后文本的JSON"""
        json_str = '这是前面的文本 {"key": "value"} 这是后面的文本'
        result = parse_json_from_llm(json_str)
        assert result == {"key": "value"}

    def test_parse_json_invalid(self):
        """测试解析无效的JSON"""
        json_str = '这不是有效的JSON {invalid}'
        with pytest.raises(ValueError, match="智谱模型未返回合法 JSON"):
            parse_json_from_llm(json_str)

    def test_parse_json_empty(self):
        """测试解析空字符串"""
        with pytest.raises(ValueError, match="智谱模型未返回合法 JSON"):
            parse_json_from_llm("")


class TestExpandQueryByRules:
    """测试查询扩展规则"""

    def test_expand_query_with_ai_keywords(self):
        """测试AI关键词扩展"""
        text = "深度学习在图像识别中的应用"
        expanded = expand_query_by_rules(text)
        assert "人工智能" in expanded or "机器学习" in expanded
        assert "TP18" in expanded or "TP391" in expanded

    def test_expand_query_with_medical_keywords(self):
        """测试医学关键词扩展"""
        text = "肺结节的CT影像诊断"
        expanded = expand_query_by_rules(text)
        assert "影像诊断学" in expanded or "呼吸系统疾病" in expanded
        assert "R445" in expanded or "R56" in expanded

    def test_expand_query_no_match(self):
        """测试无匹配规则"""
        text = "一些普通的文本内容"
        expanded = expand_query_by_rules(text)
        assert expanded == text

    def test_expand_query_case_insensitive(self):
        """测试大小写不敏感"""
        text = "Deep Learning and Neural Networks"
        expanded = expand_query_by_rules(text)
        assert "人工智能" in expanded or "机器学习" in expanded


class TestCLCAutoClassifier:
    """测试CLCAutoClassifier类"""

    @patch("auto_classifier.algorithms.clc_classifier.ZhipuClient")
    @patch("auto_classifier.algorithms.clc_classifier.CategoryStore")
    def test_classifier_init(self, mock_store, mock_client):
        """测试分类器初始化"""
        mock_store.return_value.count.return_value = 2500

        classifier = CLCAutoClassifier(
            json_path="test.json",
            model="glm-4",
            top_k=100
        )

        assert classifier.top_k == 100
        mock_store.assert_called_once()
        mock_client.assert_called_once_with(model="glm-4")

    @patch("auto_classifier.algorithms.clc_classifier.ZhipuClient")
    @patch("auto_classifier.algorithms.clc_classifier.CategoryStore")
    def test_classify_chinese(self, mock_store, mock_client):
        """测试中文分类"""
        mock_store.return_value.count.return_value = 2500
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        classifier = CLCAutoClassifier(json_path="test.json")

        # Mock内部方法
        classifier.classify = MagicMock(return_value={"mode": "中文科技文献分类"})

        result = classifier.classify_chinese("测试文本")
        classifier.classify.assert_called_once_with(text="测试文本", mode="zh")

    @patch("auto_classifier.algorithms.clc_classifier.ZhipuClient")
    @patch("auto_classifier.algorithms.clc_classifier.CategoryStore")
    def test_classify_english(self, mock_store, mock_client):
        """测试英文分类"""
        mock_store.return_value.count.return_value = 2500
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        classifier = CLCAutoClassifier(json_path="test.json")

        # Mock内部方法
        classifier.classify = MagicMock(return_value={"mode": "英文科技文献分类"})

        result = classifier.classify_english("Test text")
        classifier.classify.assert_called_once_with(text="Test text", mode="en")

    @patch("auto_classifier.algorithms.clc_classifier.ZhipuClient")
    @patch("auto_classifier.algorithms.clc_classifier.CategoryStore")
    def test_classify_domain(self, mock_store, mock_client):
        """测试专业领域分类"""
        mock_store.return_value.count.return_value = 2500
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        classifier = CLCAutoClassifier(json_path="test.json")

        # Mock内部方法
        classifier.classify = MagicMock(return_value={"mode": "专业领域科技文献分类"})

        result = classifier.classify_domain("测试文本", domain_hint="计算机科学")
        classifier.classify.assert_called_once_with(text="测试文本", mode="domain", domain_hint="计算机科学")

    @patch("auto_classifier.algorithms.clc_classifier.ZhipuClient")
    @patch("auto_classifier.algorithms.clc_classifier.CategoryStore")
    def test_classify_invalid_mode(self, mock_store, mock_client):
        """测试无效的分类模式"""
        mock_store.return_value.count.return_value = 2500
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        classifier = CLCAutoClassifier(json_path="test.json")

        with pytest.raises(ValueError, match="mode 只能是"):
            classifier.classify("测试文本", mode="invalid")

    @patch("auto_classifier.algorithms.clc_classifier.ZhipuClient")
    @patch("auto_classifier.algorithms.clc_classifier.CategoryStore")
    def test_classify_empty_text(self, mock_store, mock_client):
        """测试空文本分类"""
        mock_store.return_value.count.return_value = 2500
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        classifier = CLCAutoClassifier(json_path="test.json")

        with pytest.raises(ValueError, match="待分类文本不能为空"):
            classifier.classify("", mode="zh")
