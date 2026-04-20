"""
语步识别服务模块

提供三种语步识别功能：
1. 中文摘要语步识别
2. 英文摘要语步识别
3. 中文基金项目语步识别
"""

import json
import re
from typing import Dict, List, Any
from api_client import ZhipuClient


# ==================== 示例文本 ====================

# 中文摘要示例
EXAMPLE_ZH_ABSTRACT = """近年来，随着科研文献数量的快速增长，研究人员面临信息过载和知识获取效率低下的问题。现有文献分析方法大多侧重于关键词提取或主题分类，难以准确揭示科技文献中不同句子的语义功能。为解决这一问题，本文提出一种基于本地部署大语言模型和提示词工程的科技文献语步识别方法，用于自动识别摘要中的研究背景、研究目的、研究方法、研究结果和研究结论。该方法首先对输入摘要进行句子切分，然后结合面向学术文本设计的提示模板，引导模型对每个句子的语义角色进行判定，并通过规则约束对输出结果进行结构化整理。实验选取1200篇中英文科技论文摘要作为测试数据，与传统机器学习方法和通用文本分类模型进行对比。结果表明，本文方法在语步识别任务上的整体准确率达到91.3%，Macro-F1达到0.89，尤其在研究目的和研究结论两类句子的识别上表现更优。研究表明，基于本地大模型的提示词工程方法能够在保证数据安全性的同时，有效提升科技文献语义分析的自动化水平，为智能综述生成和知识发现提供了有力支持。"""

# 英文摘要示例
EXAMPLE_EN_ABSTRACT = """With the rapid development of deep learning technology, image recognition accuracy has been significantly improved. However, in low-light environments, the recognition performance of existing models still has a large gap. This paper proposes a low-light image enhancement method based on attention mechanism, aiming to improve image recognition accuracy in dark environments. The method adopts multi-scale feature fusion technology, combined with adaptive histogram equalization for preprocessing. Experimental results show that the recognition accuracy of this method on low-light datasets is improved by 15.3%, and the processing speed meets real-time requirements. This study validates the effectiveness of attention mechanism in the field of image enhancement, providing a new solution for low-light image processing."""

# 中文基金项目示例
EXAMPLE_ZH_PROJECT = """人工智能技术在医疗健康领域的应用日益广泛，但在罕见病诊断方面仍存在准确率低、误诊率高等问题。目前我国罕见病患者超过2000万人，平均确诊时间长达5年，严重影响患者治疗和预后。本项目针对罕见病诊断难题，研究基于多模态数据融合的智能诊断方法。主要研究内容包括：构建罕见病多模态知识图谱，开发基于深度学习的医学影像分析算法，设计临床决策支持系统。采用自然语言处理技术提取病历特征，结合计算机视觉技术分析医学影像，通过多模态融合模型实现综合诊断。预期发表高水平论文3-5篇，申请发明专利2项，形成一套完整的罕见病智能诊断系统原型。研究成果将为提高罕见病诊断效率提供技术支撑，具有重要的临床应用价值和社会效益。"""


# ==================== 中文摘要语步识别 ====================

ZH_ABSTRACT_MOVE_LABELS = {
    "background": "研究背景",
    "purpose": "研究目的",
    "method": "研究方法",
    "result": "研究结果",
    "conclusion": "研究结论"
}

ZH_ABSTRACT_PROMPT = """请分析以下中文科技论文摘要，识别其中的语步结构。

【待分析摘要】
{text}

【任务要求】
从原文中识别出分别属于以下五类语步的句子：
1. 研究背景(background)：介绍研究领域现状、存在问题、研究重要性
2. 研究目的(purpose)：说明本研究要解决的问题、目标、创新点
3. 研究方法(method)：描述采用的方法、技术、实验设计
4. 研究结果(result)：展示研究发现、实验结果、性能指标
5. 研究结论(conclusion)：总结研究贡献、意义、未来展望

【输出格式】
请严格按照以下JSON格式输出，不要输出任何其他内容：
{{"background": ["句子1", "句子2"], "purpose": ["句子1"], "method": ["句子1", "句子2"], "result": ["句子1"], "conclusion": ["句子1"]}}

【注意事项】
1. 尽量直接抽取原文句子，保持原句完整
2. 如果某类语步不存在，使用空数组 []
3. 每个句子只归类到一个主要语步
4. 只输出JSON，不要输出其他任何文字"""


# ==================== 英文摘要语步识别 ====================

EN_ABSTRACT_MOVE_LABELS = {
    "background": "Research Background",
    "purpose": "Research Purpose",
    "method": "Research Method",
    "result": "Research Result",
    "conclusion": "Research Conclusion"
}

EN_ABSTRACT_PROMPT = """Please analyze the following English scientific abstract and identify its move structure.

【Abstract to Analyze】
{text}

【Task Requirements】
Identify sentences belonging to each of the following five move types:
1. background: Introduces research field status, existing problems, research importance
2. purpose: States the problems to solve, objectives, innovations
3. method: Describes methods, techniques, experimental design
4. result: Shows research findings, experimental results, performance metrics
5. conclusion: Summarizes contributions, significance, future outlook

【Output Format】
Please strictly output in the following JSON format, do not output any other content:
{{"background": ["sentence1", "sentence2"], "purpose": ["sentence1"], "method": ["sentence1", "sentence2"], "result": ["sentence1"], "conclusion": ["sentence1"]}}

【Notes】
1. Extract original sentences directly, keep them complete
2. If a move type does not exist, use empty array []
3. Each sentence should be classified into only one primary move
4. Output JSON only, do not output any other text"""


# ==================== 中文基金项目语步识别 ====================

ZH_PROJECT_MOVE_LABELS = {
    "basis": "立项依据",
    "objective": "研究目标",
    "content": "研究内容",
    "approach": "技术路线/实施方案",
    "expected_result": "预期成果",
    "application_value": "应用价值"
}

ZH_PROJECT_PROMPT = """请分析以下中文基金项目文本，识别其中的语步结构。

【待分析文本】
{text}

【任务要求】
从原文中识别出分别属于以下六类语步的句子：
1. 立项依据(basis)：项目背景、必要性、研究现状
2. 研究目标(objective)：项目目标、预期效果
3. 研究内容(content)：研究任务、工作分解
4. 技路线(approach)：技术方案、实施路径
5. 预期成果(expected_result)：成果形式、数量指标
6. 应用价值(application_value)：应用前景、社会效益

【输出格式】
请严格按照以下JSON格式输出，不要输出任何其他内容：
{{"basis": ["句子1", "句子2"], "objective": ["句子1"], "content": ["句子1"], "approach": ["句子1"], "expected_result": ["句子1"], "application_value": ["句子1"]}}

【注意事项】
1. 尽量直接抽取原文句子，保持原句完整
2. 如果某类语步不存在，使用空数组 []
3. 每个句子只归类到一个主要语步
4. 只输出JSON，不要输出其他任何文字"""


class MoveRecognitionService:
    """语步识别服务"""

    def __init__(self):
        """初始化服务"""
        self.client = ZhipuClient()

    def _analyze_generic(self, text: str, prompt_template: str, default_result: dict) -> Dict[str, Any]:
        """
        通用分析方法

        Args:
            text: 待分析文本
            prompt_template: 提示词模板
            default_result: 默认结果结构

        Returns:
            分析结果
        """
        if not text or not text.strip():
            return {
                "code": 400,
                "message": "输入文本不能为空",
                "data": None
            }

        try:
            prompt = prompt_template.format(text=text.strip())

            response = self.client.chat(
                system_prompt="你是一位专业的科技文献分析专家。请严格按照要求输出JSON格式，不要输出任何其他内容。",
                user_prompt=prompt,
                model="glm-4-flash",
                temperature=0.3,
                max_tokens=2048
            )

            parsed_data = self._parse_response(response, default_result)

            return {
                "code": 200,
                "message": "success",
                "data": parsed_data
            }

        except Exception as e:
            return {
                "code": 500,
                "message": f"分析失败: {str(e)}",
                "data": None
            }

    def analyze_zh_abstract(self, text: str) -> Dict[str, Any]:
        """
        分析中文摘要语步

        Args:
            text: 中文摘要文本

        Returns:
            分析结果
        """
        default_result = {
            "background": [],
            "purpose": [],
            "method": [],
            "result": [],
            "conclusion": []
        }
        return self._analyze_generic(text, ZH_ABSTRACT_PROMPT, default_result)

    def analyze_en_abstract(self, text: str) -> Dict[str, Any]:
        """
        分析英文摘要语步

        Args:
            text: 英文摘要文本

        Returns:
            分析结果
        """
        default_result = {
            "background": [],
            "purpose": [],
            "method": [],
            "result": [],
            "conclusion": []
        }
        return self._analyze_generic(text, EN_ABSTRACT_PROMPT, default_result)

    def analyze_zh_project(self, text: str) -> Dict[str, Any]:
        """
        分析中文基金项目语步

        Args:
            text: 基金项目文本

        Returns:
            分析结果
        """
        default_result = {
            "basis": [],
            "objective": [],
            "content": [],
            "approach": [],
            "expected_result": [],
            "application_value": []
        }
        return self._analyze_generic(text, ZH_PROJECT_PROMPT, default_result)

    def _parse_response(self, raw_response: str, default_result: dict) -> Dict[str, List[str]]:
        """
        解析模型响应，提取结构化数据（使用正则表达式直接提取，避免JSON解析问题）

        Args:
            raw_response: 模型原始响应
            default_result: 默认结果结构

        Returns:
            结构化的语步数据
        """
        if not raw_response:
            return default_result

        result = self._extract_arrays_by_regex(raw_response, default_result)
        return result

    def _extract_arrays_by_regex(self, text: str, default_result: dict) -> Dict[str, List[str]]:
        """
        使用正则表达式从响应中提取数组内容（避免JSON解析错误）

        Args:
            text: 模型响应文本
            default_result: 默认结果结构

        Returns:
            提取的结构化数据
        """
        # 移除markdown代码块标记
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)

        # 对每个标签，使用正则提取对应的数组内容
        for key in default_result.keys():
            # 匹配 "key": ["句子1", "句子2", ...] 格式
            pattern = rf'"{key}"\s*:\s*\[(.*?)\]'
            match = re.search(pattern, text, re.DOTALL)

            if match:
                array_content = match.group(1)
                # 提取所有引号包围的字符串
                sentences = re.findall(r'"([^"]*)"', array_content)
                default_result[key] = [s.strip() for s in sentences if s.strip()]

        return default_result


# 创建全局服务实例
_service_instance = None


def get_move_recognition_service() -> MoveRecognitionService:
    """获取语步识别服务实例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = MoveRecognitionService()
    return _service_instance


# 便捷函数
def analyze_zh_abstract(text: str) -> Dict[str, Any]:
    """分析中文摘要语步"""
    return get_move_recognition_service().analyze_zh_abstract(text)


def analyze_en_abstract(text: str) -> Dict[str, Any]:
    """分析英文摘要语步"""
    return get_move_recognition_service().analyze_en_abstract(text)


def analyze_zh_project(text: str) -> Dict[str, Any]:
    """分析中文基金项目语步"""
    return get_move_recognition_service().analyze_zh_project(text)


if __name__ == "__main__":
    # 测试中文摘要
    print("=" * 50)
    print("中文摘要语步识别测试：")
    result = analyze_zh_abstract(EXAMPLE_ZH_ABSTRACT)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 测试英文摘要
    print("\n" + "=" * 50)
    print("英文摘要语步识别测试：")
    result = analyze_en_abstract(EXAMPLE_EN_ABSTRACT)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 测试基金项目
    print("\n" + "=" * 50)
    print("中文基金项目语步识别测试：")
    result = analyze_zh_project(EXAMPLE_ZH_PROJECT)
    print(json.dumps(result, ensure_ascii=False, indent=2))
