"""Pytest配置和共享fixtures"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def sample_clc_json_data():
    """示例中图分类法JSON数据"""
    return [
        {
            "id": "T",
            "desc": "工业技术",
            "children": [
                {
                    "id": "TP",
                    "desc": "自动化技术、计算机技术",
                    "children": [
                        {
                            "id": "TP18",
                            "desc": "人工智能",
                            "children": [
                                {
                                    "id": "TP181",
                                    "desc": "人工智能理论",
                                    "children": []
                                },
                                {
                                    "id": "TP182",
                                    "desc": "机器学习",
                                    "children": []
                                }
                            ]
                        },
                        {
                            "id": "TP3",
                            "desc": "计算技术、计算机技术",
                            "children": []
                        }
                    ]
                },
                {
                    "id": "TH",
                    "desc": "机械、仪表工业",
                    "children": []
                }
            ]
        },
        {
            "id": "R",
            "desc": "医药、卫生",
            "children": [
                {
                    "id": "R4",
                    "desc": "临床医学",
                    "children": [
                        {
                            "id": "R445",
                            "desc": "影像诊断学",
                            "children": []
                        }
                    ]
                }
            ]
        },
        {
            "id": "N",
            "desc": "自然科学总论",
            "children": []
        }
    ]


@pytest.fixture
def temp_clc_json_file(tmp_path, sample_clc_json_data):
    """创建临时的中图分类法JSON文件"""
    json_file = tmp_path / "test_clc.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sample_clc_json_data, f, ensure_ascii=False, indent=2)
    return json_file


@pytest.fixture
def mock_zhipu_client():
    """Mock智谱AI客户端"""
    with patch('clc_classifier.ZhipuClient') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        mock_instance.model = "glm-4-flash"
        yield mock_instance


@pytest.fixture
def sample_classification_result():
    """示例分类结果"""
    return {
        "language_detected": "zh",
        "is_interdisciplinary": False,
        "primary": {
            "id": "TP18",
            "name": "人工智能",
            "path": "T 工业技术 > TP 自动化技术、计算机技术 > TP18 人工智能",
            "confidence": 0.92,
            "reason": "文献主题明确涉及深度学习，属于人工智能领域"
        },
        "alternatives": [
            {
                "id": "TP182",
                "name": "机器学习",
                "path": "T 工业技术 > TP 自动化技术、计算机技术 > TP18 人工智能 > TP182 机器学习",
                "confidence": 0.78,
                "reason": "涉及机器学习算法"
            }
        ],
        "keywords": ["深度学习", "人工智能", "机器学习"],
        "user_selection_note": "主分类用于默认归档；若文献同时强调方法、对象和应用场景，可从备选分类号中人工选择。"
    }


@pytest.fixture
def sample_texts():
    """示例测试文本"""
    return {
        "ai_zh": "本文研究了深度学习在医学影像诊断中的应用，提出了一种基于卷积神经网络的肺结节检测方法。",
        "ai_en": "This paper investigates the application of deep learning in medical image diagnosis, proposing a lung nodule detection method based on convolutional neural networks.",
        "medical": "肺癌是最常见的恶性肿瘤之一，早期诊断对提高患者生存率至关重要。CT影像诊断是肺癌筛查的主要手段。",
        "agriculture": "本研究探讨了不同施肥处理对水稻产量的影响，结果表明有机肥与化肥配施能显著提高水稻产量和品质。",
        "mixed": "结合了人工智能和医学的跨学科研究，探讨深度学习在医疗领域的应用。"
    }
