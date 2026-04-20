"""
诉讼策略推演引擎（对方律师视角）
Litigation Strategy Engine - Opposing Counsel Perspective
"""
import os
from typing import Dict, Any, List
from utils.hunyuan_client import HunyuanClient


SYSTEM_PROMPT_OPPONENT = """你是一位经验丰富的辩护律师，代表诉讼中的对方当事人。
你的任务是：
1. 仔细阅读原告/申请人提交的起诉状或案情材料
2. 站在**对方律师**的视角，找出材料中的漏洞、矛盾和薄弱环节
3. 生成专业的质证意见清单
4. 提供风险提示和诉讼策略建议
5. 输出结构化的诉讼策略报告

请保持专业、客观，重点关注：
- 事实认定的争议点
- 证据链的完整性
- 法律适用的准确性
- 程序合规性问题
- 可能的反诉或抗辩策略"""


class StrategyEngine:
    """诉讼策略推演引擎"""

    def __init__(self):
        self.hunyuan = HunyuanClient(
            app_id=os.getenv("YUANQI_APP_ID", ""),
            app_key=os.getenv("YUANQI_APP_KEY", ""),
        )

    def analyze(self, complaint_text: str, case_type: str = "civil") -> Dict[str, Any]:
        """
        分析起诉状，从对方律师视角生成策略报告

        Args:
            complaint_text: 起诉状或案情描述文本
            case_type: 案件类型 civil(民事) | criminal(刑事) | administrative(行政)

        Returns:
            包含质证意见、风险提示和诉讼策略的报告
        """
        case_type_map = {
            "civil": "民事",
            "criminal": "刑事",
            "administrative": "行政",
        }
        case_type_cn = case_type_map.get(case_type, "民事")

        query = f"""以下是一份{case_type_cn}案件的起诉状/案情材料：

---
{complaint_text}
---

请站在对方律师的角度，生成以下内容：

## 一、案情要素提炼
（提取当事人、争议标的、主要事实、诉讼请求）

## 二、质证意见清单
（逐条列举可质疑的证据和事实陈述）

## 三、法律适用分析
（分析原告/申请人援引法律条文是否准确，有无不当之处）

## 四、风险提示
（本方可能面临的主要法律风险）

## 五、诉讼策略建议
（抗辩策略、反诉可能性、和解建议等）"""

        messages = [
            {"role": "user", "content": [{"type": "text", "text": query}]}
        ]

        try:
            resp = self.hunyuan.chat(messages, user_id="strategy_engine")
            report_content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            report_content = f"策略推演暂时不可用（{str(e)}），请检查腾讯元器配置。"

        return {
            "case_type": case_type,
            "report": report_content,
            "complaint_length": len(complaint_text),
            "export_ready": True,
        }

    def generate_risk_matrix(self, issues: List[str]) -> List[Dict]:
        """
        生成风险矩阵

        Args:
            issues: 争议点列表

        Returns:
            风险矩阵，包含严重程度和应对建议
        """
        matrix = []
        for issue in issues:
            matrix.append({
                "issue": issue,
                "severity": "high",  # 实际应通过LLM评估
                "probability": "medium",
                "strategy": "待AI评估",
            })
        return matrix
