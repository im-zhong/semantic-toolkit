"""
API 调用模块
支持智谱AI GLM系列模型的API调用
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ZhipuClient:
    """智谱AI API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: API密钥，如未提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError(
                "未找到API密钥，请设置环境变量 ZHIPU_API_KEY 或传入 api_key 参数"
            )

        # 延迟导入，避免未安装时报错
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "请先安装 zhipuai: pip install zhipuai"
            )

        # 可用模型列表
        self.models = {
            "glm-4-flash": "快速版本，性价比高",
            "glm-4": "标准版本，性能更强",
            "glm-4-plus": "增强版本，能力最强",
        }

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "glm-4-flash",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        发送对话请求

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大输出token数

        Returns:
            模型回复内容
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"API调用失败: {str(e)}")

    def analyze_move(
        self,
        abstract: str,
        model: str = "glm-4-flash",
        structured: bool = False
    ) -> str:
        """
        分析摘要语步

        Args:
            abstract: 待分析的摘要文本
            model: 模型名称
            structured: 是否使用结构化输出

        Returns:
            分析结果
        """
        from prompts import get_prompt

        system_prompt, user_prompt = get_prompt(abstract, structured=structured)
        return self.chat(system_prompt, user_prompt, model=model)


def test_api():
    """测试API连接"""
    client = ZhipuClient()

    # 简单测试
    response = client.chat(
        system_prompt="你是一个友好的助手",
        user_prompt="请用一句话介绍自己"
    )
    print("API连接成功！")
    print(f"测试回复: {response}")
    return response


if __name__ == "__main__":
    test_api()
