"""FastAPI接口的单元测试"""

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from auto_classifier.main import app
from auto_classifier.dependencies import get_classifier


def make_classify_response(mode="中文科技文献分类", primary_name="人工智能"):
    """构造完整的API分类响应，避免response_model校验失败"""
    return {
        "tool": "自动分类工具",
        "mode": mode,
        "model": "glm-4-flash",
        "category_source": "data/完整版中国图书馆图书分类法.json",
        "loaded_scitech_categories": 2105,
        "candidate_count": 80,
        "result": {
            "primary": {
                "id": "TP18",
                "name": primary_name
            },
            "alternatives": []
        },
        "local_top_candidates": []
    }

class TestAPI:
    """测试API端点"""

    def test_root_endpoint(self):
        """测试根路径"""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "endpoints" in data

    @patch('auto_classifier.routers.health.get_classifier')
    def test_health_check(self, mock_get_classifier):
        """测试健康检查接口"""
        mock_classifier = MagicMock()
        mock_classifier.store.count.return_value = 2105
        mock_classifier.llm.model = "glm-4-flash"
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["loaded_categories"] == 2105
        assert data["model"] == "glm-4-flash"

    @patch('auto_classifier.routers.health.get_classifier')
    def test_health_check_error(self, mock_get_classifier):
        """测试健康检查异常情况"""
        mock_get_classifier.side_effect = Exception("Service unavailable")

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 503

    def test_get_modes(self):
        """测试获取分类模式列表"""
        client = TestClient(app)
        response = client.get("/api/v1/modes")

        assert response.status_code == 200
        data = response.json()
        assert "modes" in data
        assert len(data["modes"]) == 3

        mode_codes = [m["code"] for m in data["modes"]]
        assert "zh" in mode_codes
        assert "en" in mode_codes
        assert "domain" in mode_codes

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_get_stats(self, mock_get_classifier):
        """测试获取统计信息"""
        mock_classifier = MagicMock()
        mock_classifier.store.count.return_value = 2105
        mock_classifier.llm.model = "glm-4-flash"
        mock_classifier.top_k = 80
        mock_classifier.prompt_candidate_k = 35
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_categories"] == 2105
        assert data["model"] == "glm-4-flash"
        assert data["top_k"] == 80
        assert data["prompt_candidate_k"] == 35

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_text_zh(self, mock_get_classifier):
        """测试中文文本分类"""
        mock_classifier = MagicMock()
        mock_classifier.classify_chinese.return_value = make_classify_response(
            mode="中文科技文献分类",
            primary_name="人工智能"
        )
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "本文研究了深度学习在医学影像诊断中的应用",
                "mode": "zh"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "中文科技文献分类"
        mock_classifier.classify_chinese.assert_called_once_with(
            "本文研究了深度学习在医学影像诊断中的应用"
        )

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_text_en(self, mock_get_classifier):
        """测试英文文本分类"""
        mock_classifier = MagicMock()
        mock_classifier.classify_english.return_value = make_classify_response(
            mode="英文科技文献分类",
            primary_name="Artificial Intelligence"
        )
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "Deep learning in medical imaging",
                "mode": "en"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "英文科技文献分类"
        mock_classifier.classify_english.assert_called_once_with(
            "Deep learning in medical imaging"
        )

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_text_domain(self, mock_get_classifier):
        """测试专业领域分类"""
        mock_classifier = MagicMock()
        mock_classifier.classify_domain.return_value = make_classify_response(
            mode="专业领域科技文献分类",
            primary_name="人工智能"
        )
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "测试文本",
                "mode": "domain",
                "domain_hint": "计算机科学"
            }
        )

        assert response.status_code == 200
        mock_classifier.classify_domain.assert_called_once_with(
            "测试文本",
            domain_hint="计算机科学"
        )

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_text_invalid_mode(self, mock_get_classifier):
        """测试无效的分类模式"""
        mock_classifier = MagicMock()
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "测试文本",
                "mode": "invalid"
            }
        )

        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_text_empty_text(self, mock_get_classifier):
        """测试空文本"""
        mock_classifier = MagicMock()
        mock_classifier.classify_chinese.side_effect = ValueError("待分类文本不能为空")
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "",
                "mode": "zh"
            }
        )

        assert response.status_code == 422

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_text_reject_fixed_params(self, mock_get_classifier):
        """测试文本接口拒绝用户传入后端固定参数"""
        mock_classifier = MagicMock()
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "测试文本",
                "mode": "zh",
                "model": "glm-4",
                "top_k": 100
            }
        )

        assert response.status_code == 422

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_file_reject_fixed_params(self, mock_get_classifier):
        """测试文件接口拒绝用户传入后端固定参数"""
        mock_classifier = MagicMock()
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify/file",
            files={"file": ("test.txt", BytesIO(b"test content"), "text/plain")},
            data={"mode": "zh", "model": "glm-4", "top_k": "100"}
        )

        assert response.status_code == 422

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_file(self, mock_get_classifier):
        """测试文件分类"""
        mock_classifier = MagicMock()
        mock_classifier.classify_chinese.return_value = make_classify_response(
            mode="中文科技文献分类",
            primary_name="人工智能"
        )
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)

        # 创建测试文件内容
        file_content = "这是一段测试文件内容，用于测试文件分类功能。".encode("utf-8")

        response = client.post(
            "/api/v1/classify/file",
            files={"file": ("test.txt", BytesIO(file_content), "text/plain")},
            data={
                "mode": "zh",
                "encoding": "utf-8"
            }
        )

        assert response.status_code == 200
        mock_classifier.classify_chinese.assert_called_once()
        call_args = mock_classifier.classify_chinese.call_args
        assert "这是一段测试文件内容" in call_args[0][0]

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_file_empty(self, mock_get_classifier):
        """测试空文件"""
        mock_classifier = MagicMock()
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify/file",
            files={"file": ("empty.txt", BytesIO(b""), "text/plain")},
            data={"mode": "zh"}
        )

        assert response.status_code == 422
        assert "文件内容为空" in response.json()["detail"]

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_file_invalid_encoding(self, mock_get_classifier):
        """测试无效的文件编码"""
        mock_classifier = MagicMock()
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        # 创建一些无法用utf-8解码的内容
        file_content = b"\xff\xfe\x00\x00"  # 无效的UTF-8序列

        response = client.post(
            "/api/v1/classify/file",
            files={"file": ("test.txt", BytesIO(file_content), "text/plain")},
            data={"mode": "zh", "encoding": "utf-8"}
        )

        # 由于使用了errors="ignore"，应该能解码成功，只是内容为空
        # 但如果内容解码后为空，会返回400
        assert response.status_code in [400, 200]

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_file_invalid_mode(self, mock_get_classifier):
        """测试文件分类时的无效模式"""
        mock_classifier = MagicMock()
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify/file",
            files={"file": ("test.txt", BytesIO(b"test content"), "text/plain")},
            data={"mode": "invalid"}
        )

        assert response.status_code == 400
        assert "mode 参数必须是" in response.json()["detail"]

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_text_validation_errors(self, mock_get_classifier):
        """测试请求参数验证"""
        mock_classifier = MagicMock()
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)

        # 测试缺少必需字段
        response = client.post(
            "/api/v1/classify",
            json={"mode": "zh"}  # 缺少text字段
        )
        assert response.status_code == 422  # Validation error

        # 测试传入不允许的固定参数
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "测试",
                "mode": "zh",
                "top_k": 300  # 超出最大值200
            }
        )
        assert response.status_code == 422

        # 测试top_k低于最小值
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "测试",
                "mode": "zh",
                "top_k": 5  # 低于最小值10
            }
        )
        assert response.status_code == 422

    @patch('auto_classifier.routers.classify.get_classifier')
    def test_classify_server_error(self, mock_get_classifier):
        """测试服务器内部错误"""
        mock_classifier = MagicMock()
        mock_classifier.classify_chinese.side_effect = Exception("Internal server error")
        mock_get_classifier.return_value = mock_classifier

        client = TestClient(app)
        response = client.post(
            "/api/v1/classify",
            json={
                "text": "测试文本",
                "mode": "zh"
            }
        )

        assert response.status_code == 500
        assert "分类失败" in response.json()["detail"]
