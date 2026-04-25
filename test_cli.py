"""CLI模块的单元测试"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cli import read_text, main


class TestReadText:
    """测试文本读取功能"""

    def test_read_text_from_args(self):
        """测试从args.text读取文本"""
        args = MagicMock()
        args.text = "测试文本内容"
        args.file = ""
        args.encoding = "utf-8"

        result = read_text(args)
        assert result == "测试文本内容"

    def test_read_text_from_file(self):
        """测试从文件读取文本"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write("文件内容测试")
            temp_path = f.name

        try:
            args = MagicMock()
            args.text = ""
            args.file = temp_path
            args.encoding = "utf-8"

            result = read_text(args)
            assert result == "文件内容测试"
        finally:
            Path(temp_path).unlink()

    def test_read_text_file_not_found(self):
        """测试文件不存在时抛出异常"""
        args = MagicMock()
        args.text = ""
        args.file = "不存在的文件.txt"
        args.encoding = "utf-8"

        with pytest.raises(FileNotFoundError, match="文件不存在"):
            read_text(args)

    def test_read_text_no_input(self):
        """测试没有提供输入时抛出异常"""
        args = MagicMock()
        args.text = ""
        args.file = ""
        args.encoding = "utf-8"

        with pytest.raises(ValueError, match="请使用 --text 输入文本"):
            read_text(args)

    def test_read_text_with_different_encoding(self):
        """测试使用不同编码读取文件"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='gbk', delete=False, suffix='.txt') as f:
            f.write("GBK编码测试")
            temp_path = f.name

        try:
            args = MagicMock()
            args.text = ""
            args.file = temp_path
            args.encoding = "gbk"

            result = read_text(args)
            assert result == "GBK编码测试"
        finally:
            Path(temp_path).unlink()


class TestMain:
    """测试main函数"""

    @patch('cli.CLCAutoClassifier')
    @patch('sys.stdout', new_callable=MagicMock)
    @patch('sys.argv', ['cli.py', '--mode', 'zh', '--text', '测试'])
    def test_main_chinese_mode(self, mock_stdout, mock_classifier):
        """测试中文分类模式"""
        mock_instance = MagicMock()
        mock_classifier.return_value = mock_instance
        mock_instance.classify_chinese.return_value = {
            "tool": "自动分类工具",
            "mode": "中文科技文献分类",
            "result": {
                "primary": {"id": "TP18", "name": "人工智能"},
                "alternatives": []
            }
        }

        main()

        mock_instance.classify_chinese.assert_called_once_with("测试")
        mock_classifier.assert_called_once_with(
            json_path="data/完整版中国图书馆图书分类法.json",
            model=None,
            top_k=80
        )

    @patch('cli.CLCAutoClassifier')
    @patch('sys.stdout', new_callable=MagicMock)
    @patch('sys.argv', ['cli.py', '--mode', 'en', '--text', 'AI test'])
    def test_main_english_mode(self, mock_stdout, mock_classifier):
        """测试英文分类模式"""
        mock_instance = MagicMock()
        mock_classifier.return_value = mock_instance
        mock_instance.classify_english.return_value = {
            "tool": "自动分类工具",
            "mode": "英文科技文献分类",
            "result": {
                "primary": {"id": "TP18", "name": "Artificial Intelligence"},
                "alternatives": []
            }
        }

        main()

        mock_instance.classify_english.assert_called_once_with("AI test")

    @patch('cli.CLCAutoClassifier')
    @patch('sys.stdout', new_callable=MagicMock)
    @patch('sys.argv', ['cli.py', '--mode', 'domain', '--text', '测试', '--domain-hint', '计算机科学'])
    def test_main_domain_mode(self, mock_stdout, mock_classifier):
        """测试专业领域分类模式"""
        mock_instance = MagicMock()
        mock_classifier.return_value = mock_instance
        mock_instance.classify_domain.return_value = {
            "tool": "自动分类工具",
            "mode": "专业领域科技文献分类",
            "result": {
                "primary": {"id": "TP18", "name": "人工智能"},
                "alternatives": []
            }
        }

        main()

        mock_instance.classify_domain.assert_called_once_with("测试", domain_hint="计算机科学")

    @patch('cli.CLCAutoClassifier')
    @patch('sys.stdout', new_callable=MagicMock)
    @patch('sys.argv', ['cli.py', '--mode', 'zh', '--text', '测试', '--json-path', 'custom.json', '--model', 'glm-4', '--top-k', '100'])
    def test_main_custom_parameters(self, mock_stdout, mock_classifier):
        """测试自定义参数"""
        mock_instance = MagicMock()
        mock_classifier.return_value = mock_instance
        mock_instance.classify_chinese.return_value = {"tool": "测试"}

        main()

        mock_classifier.assert_called_once_with(
            json_path="custom.json",
            model="glm-4",
            top_k=100
        )

    @patch('cli.CLCAutoClassifier')
    @patch('sys.stdout', new_callable=MagicMock)
    @patch('sys.argv', ['cli.py', '--mode', 'zh', '--file', 'test.txt', '--encoding', 'gbk'])
    def test_main_with_file(self, mock_stdout, mock_classifier):
        """测试从文件读取"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write("文件中的测试文本")
            temp_path = f.name

        try:
            mock_instance = MagicMock()
            mock_classifier.return_value = mock_instance
            mock_instance.classify_chinese.return_value = {"tool": "测试"}

            with patch('cli.read_text', return_value="文件中的测试文本"):
                main()

            mock_instance.classify_chinese.assert_called_once_with("文件中的测试文本")
        finally:
            Path(temp_path).unlink()

    @patch('cli.CLCAutoClassifier')
    @patch('sys.stdout', new_callable=MagicMock)
    @patch('sys.argv', ['cli.py', '--mode', 'zh', '--text', '测试'])
    def test_main_output_json(self, mock_stdout, mock_classifier):
        """测试输出JSON格式"""
        expected_result = {
            "tool": "自动分类工具",
            "mode": "中文科技文献分类",
            "result": {
                "primary": {"id": "TP18", "name": "人工智能"},
                "alternatives": []
            }
        }

        mock_instance = MagicMock()
        mock_classifier.return_value = mock_instance
        mock_instance.classify_chinese.return_value = expected_result

        main()

        output = mock_stdout.write.call_args_list
        output_text = ''.join(str(call) for call in output)

        assert "tool" in output_text
        assert "TP18" in output_text
        assert "人工智能" in output_text
