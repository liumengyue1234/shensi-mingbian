"""
相似案例匹配引擎
Case Retrieval Engine
"""
from typing import List, Dict, Any, Optional
from utils.deli_client import DeliClient


class CaseRetrievalEngine:
    """相似案例智能检索与分析引擎"""

    def __init__(self, deli_client: DeliClient):
        self.client = deli_client

    def search(
        self,
        keywords: Optional[List[str]] = None,
        long_text: Optional[str] = None,
        page_no: int = 1,
        page_size: int = 5,
        court_level: Optional[List[str]] = None,
        case_year_start: Optional[str] = None,
        case_year_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        检索类似案例

        Args:
            keywords: 关键词列表（关键词检索模式）
            long_text: 案情描述（语义检索模式，优先级高于 keywords）
            page_no: 页码
            page_size: 每页数量
            court_level: 法院层级过滤
            case_year_start: 裁判年份区间起始
            case_year_end: 裁判年份区间截止

        Returns:
            包含 cases 列表和 total 数量的字典
        """
        raw = self.client.search_cases(
            keyword_arr=keywords if not long_text else None,
            long_text=long_text,
            page_no=page_no,
            page_size=page_size,
            court_level_arr=court_level,
            case_year_start=case_year_start,
            case_year_end=case_year_end,
        )

        cases = self._parse_cases(raw)
        return {
            "total": raw.get("body", {}).get("total", 0),
            "page_no": page_no,
            "page_size": page_size,
            "cases": cases,
        }

    def _parse_cases(self, raw: Dict) -> List[Dict]:
        """解析案例列表，提取关键信息"""
        data = raw.get("body", {}).get("data", [])
        if not data:
            return []

        parsed = []
        for item in data:
            parsed.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "court": item.get("courtName", ""),
                "court_level": item.get("courtLevel", ""),
                "judgement_date": item.get("judgementDate", ""),
                "case_number": item.get("caseNo", ""),
                "case_type": item.get("caseType", ""),
                "cause": item.get("cause", ""),
                "summary": item.get("summary", ""),
                "keywords": item.get("keywords", []),
                "score": item.get("score", 0),
            })
        return parsed

    def generate_report(self, query: str, cases: List[Dict]) -> str:
        """
        基于检索结果生成类案分析报告（模板）

        Args:
            query: 用户查询
            cases: 类案列表

        Returns:
            Markdown格式分析报告
        """
        if not cases:
            return "未检索到相关类案，建议调整检索关键词。"

        lines = [
            f"## 类案检索报告",
            f"",
            f"**检索问题**：{query}",
            f"**检索结果**：共找到 {len(cases)} 个相关案例",
            f"",
            f"---",
            f"",
        ]

        for i, case in enumerate(cases, 1):
            lines.extend([
                f"### 案例 {i}：{case.get('title', '未知案例')}",
                f"",
                f"- **法院**：{case.get('court', '-')}（{case.get('court_level', '-')}）",
                f"- **案号**：{case.get('case_number', '-')}",
                f"- **裁判日期**：{case.get('judgement_date', '-')}",
                f"- **案由**：{case.get('cause', '-')}",
                f"",
                f"**裁判摘要**：",
                f"{case.get('summary', '暂无摘要')}",
                f"",
                f"---",
                f"",
            ])

        return "\n".join(lines)
