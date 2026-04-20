"""
腾讯混元大模型客户端封装
Tencent Hunyuan LLM Client
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional, Generator


class HunyuanClient:
    """腾讯元器智能体 API 客户端"""

    API_URL = "https://yuanqi.tencent.com/openapi/v1/agent/chat/completions"

    def __init__(self, app_id: str, app_key: str):
        self.app_id = app_id
        self.app_key = app_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {app_key}",
        }

    def chat(
        self,
        messages: List[Dict],
        user_id: str = "user_001",
        stream: bool = False,
        custom_variables: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        与智能体对话（非流式）

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": [{"type": "text", "text": "..."}]}]
            user_id: 用户标识
            stream: 是否流式
            custom_variables: 自定义参数（工作流场景）

        Returns:
            API 响应数据
        """
        payload: Dict[str, Any] = {
            "assistant_id": self.app_id,
            "user_id": user_id,
            "stream": stream,
            "messages": messages,
        }
        if custom_variables:
            payload["custom_variables"] = custom_variables

        r = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()

    def chat_stream(
        self,
        messages: List[Dict],
        user_id: str = "user_001",
    ) -> Generator[str, None, None]:
        """流式对话，逐步返回内容片段"""
        payload = {
            "assistant_id": self.app_id,
            "user_id": user_id,
            "stream": True,
            "messages": messages,
        }
        with requests.post(
            self.API_URL, headers=self.headers, json=payload, stream=True, timeout=60
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                line_str = line.decode("utf-8")
                if line_str.startswith("data:"):
                    data_str = line_str[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        choices = data.get("choices", [])
                        for choice in choices:
                            delta = choice.get("delta", {})
                            if delta.get("role") == "assistant":
                                content = delta.get("content", "")
                                if content:
                                    yield content
                    except json.JSONDecodeError:
                        continue

    def simple_query(self, text: str, user_id: str = "user_001") -> str:
        """简单文本查询，返回助手回复文本"""
        messages = [
            {"role": "user", "content": [{"type": "text", "text": text}]}
        ]
        resp = self.chat(messages, user_id=user_id)
        try:
            return resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return ""

    @staticmethod
    def build_messages(history: List[Dict], user_input: str) -> List[Dict]:
        """
        构建对话消息列表（支持多轮对话历史）

        Args:
            history: 历史消息 [{"role": "user/assistant", "text": "..."}]
            user_input: 当前用户输入

        Returns:
            符合API格式的messages列表
        """
        messages = []
        for item in history:
            messages.append({
                "role": item["role"],
                "content": [{"type": "text", "text": item["text"]}],
            })
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": user_input}],
        })
        return messages
