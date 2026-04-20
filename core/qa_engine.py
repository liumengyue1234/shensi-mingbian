"""
对话式法律问答引擎（双擎联动：法条+案例）
Conversational Legal QA Engine
"""
import os
from typing import Dict, Any, List, Optional
from utils.deli_client import DeliClient
from utils.hunyuan_client import HunyuanClient


class QAEngine:
    """
    对话式法律问答引擎

    工作流程：
    1. 接收用户自然语言问题
    2. 意图识别（法条检索 / 案例检索 / 综合问答）
    3. 并行调用得理法规和案例API获取相关内容
    4. 以混元大模型为认知引擎，综合生成回答
    """

    def __init__(self):
        self.deli = DeliClient(
            app_id=os.getenv("DELI_APP_ID", "QthdBErlyaYvyXul"),
            secret=os.getenv("DELI_SECRET", "EC5D455E6BD348CE8E18BE05926D2EBE"),
        )
        self.hunyuan = HunyuanClient(
            app_id=os.getenv("YUANQI_APP_ID", ""),
            app_key=os.getenv("YUANQI_APP_KEY", ""),
        )
        self.sessions: Dict[str, List[Dict]] = {}  # 简单会话存储

    def query(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """
        处理法律咨询请求（法条+案例双擎驱动）

        Args:
            user_input: 用户问题
            session_id: 会话ID（支持多轮对话）

        Returns:
            包含回答、相关法条、相关案例的综合结果
        """
        # 1. 并行检索法规和案例
        law_results = []
        case_results = []

        try:
            law_raw = self.deli.search_laws(keywords=[user_input], field_name="semantic", page_size=3)
            law_data = law_raw.get("body", {}).get("data", [])
            law_results = [
                {"title": d.get("title", ""), "publisher": d.get("publisherName", ""), "id": d.get("id", "")}
                for d in law_data[:3]
            ]
        except Exception:
            pass

        try:
            case_raw = self.deli.search_cases(long_text=user_input, page_size=3)
            case_data = case_raw.get("body", {}).get("data", [])
            case_results = [
                {
                    "title": d.get("title", ""),
                    "court": d.get("courtName", ""),
                    "date": d.get("judgementDate", ""),
                    "summary": d.get("summary", "")[:200] + "..." if d.get("summary", "") else "",
                }
                for d in case_data[:3]
            ]
        except Exception:
            pass

        # 2. 构造增强提示词
        context_parts = ["你是一位专业的法律顾问，请基于以下法律资料回答用户问题。"]
        if law_results:
            context_parts.append("\n【相关法规】")
            for law in law_results:
                context_parts.append(f"- {law['title']}（{law['publisher']}）")
        if case_results:
            context_parts.append("\n【参考案例】")
            for case in case_results:
                context_parts.append(f"- {case['title']}（{case['court']} {case['date']}）")
                if case["summary"]:
                    context_parts.append(f"  摘要：{case['summary']}")
        context_parts.append(f"\n【用户问题】\n{user_input}")
        full_query = "\n".join(context_parts)

        # 3. 获取会话历史
        history = self.sessions.get(session_id, [])
        messages = HunyuanClient.build_messages(history, full_query)

        # 4. 调用混元大模型生成回答
        answer = ""
        try:
            resp = self.hunyuan.chat(messages, user_id=session_id)
            answer = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            answer = f"（AI服务暂时不可用，请检查配置。错误：{e}）"
            if law_results:
                answer += f"\n\n相关法规：{', '.join(l['title'] for l in law_results)}"

        # 5. 更新会话历史
        history.append({"role": "user", "text": user_input})
        history.append({"role": "assistant", "text": answer})
        self.sessions[session_id] = history[-20:]  # 保留最近10轮

        return {
            "answer": answer,
            "related_laws": law_results,
            "related_cases": case_results,
            "session_id": session_id,
        }

    def clear_session(self, session_id: str):
        """清空会话历史"""
        self.sessions.pop(session_id, None)
