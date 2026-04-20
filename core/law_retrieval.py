"""
精准法条检索引擎
Law Retrieval Engine
"""
from typing import List, Dict, Any, Optional
from utils.deli_client import DeliClient


class LawRetrievalEngine:
    """法条精准检索引擎，支持关键词和语义双模式"""

    def __init__(self, deli_client: DeliClient):
        self.client = deli_client

    def search(
        self,
        keywords: List[str],
        field_name: str = "semantic",
        page_no: int = 1,
        page_size: int = 5,
        fetch_detail: bool = False,
    ) -> Dict[str, Any]:
        """
        检索相关法规

        Args:
            keywords: 检索关键词或问题描述
            field_name: 检索模式 "semantic"（语义）| "title"（关键词）
            page_no: 页码
            page_size: 每页数量
            fetch_detail: 是否获取法规全文（会产生额外API调用）

        Returns:
            法规检索结果
        """
        raw = self.client.search_laws(
            keywords=keywords,
            field_name=field_name,
            page_no=page_no,
            page_size=page_size,
        )

        laws = self._parse_laws(raw)

        if fetch_detail and laws:
            laws = self._enrich_with_detail(laws)

        return {
            "total": raw.get("body", {}).get("total", 0),
            "page_no": page_no,
            "page_size": page_size,
            "laws": laws,
        }

    def get_detail(self, law_id: str) -> Dict[str, Any]:
        """获取法规全文详情"""
        raw = self.client.get_law_detail(law_id)
        body = raw.get("body", {})
        return {
            "id": law_id,
            "title": body.get("title", ""),
            "publisher": body.get("publisherName", ""),
            "publish_date": body.get("publishDate", ""),
            "active_date": body.get("activeDate", ""),
            "level": body.get("levelName", ""),
            "timeliness": body.get("timelinessName", ""),
            "content": body.get("lawDetailContent", ""),
        }

    def _parse_laws(self, raw: Dict) -> List[Dict]:
        """解析法规列表"""
        data = raw.get("body", {}).get("data", [])
        if not data:
            return []

        return [
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "publisher": item.get("publisherName", ""),
                "publish_date": item.get("publishDate", ""),
                "level": item.get("levelName", ""),
                "timeliness": item.get("timelinessName", ""),
                "score": item.get("score", 0),
            }
            for item in data
        ]

    def _enrich_with_detail(self, laws: List[Dict]) -> List[Dict]:
        """批量补充法规全文"""
        enriched = []
        for law in laws:
            try:
                detail = self.get_detail(law["id"])
                law["content"] = detail.get("content", "")
            except Exception:
                law["content"] = ""
            enriched.append(law)
        return enriched
