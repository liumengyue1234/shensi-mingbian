"""
得理开放平台 API 客户端封装
Deli Legal Open Platform API Client
"""
import requests
from typing import List, Dict, Any, Optional


class DeliClient:
    """得理开放平台统一客户端"""

    BASE_URL = "https://openapi.delilegal.com/api/qa/v3/search"

    def __init__(self, app_id: str, secret: str):
        self.app_id = app_id
        self.secret = secret
        self.headers = {
            "Content-Type": "application/json",
            "appid": app_id,
            "secret": secret,
        }

    def search_cases(
        self,
        keyword_arr: Optional[List[str]] = None,
        long_text: Optional[str] = None,
        page_no: int = 1,
        page_size: int = 5,
        sort_field: str = "correlation",
        sort_order: str = "desc",
        court_level_arr: Optional[List[str]] = None,
        judgement_type_arr: Optional[List[str]] = None,
        case_year_start: Optional[str] = None,
        case_year_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        类案检索

        Args:
            keyword_arr: 关键词数组，如 ["上班途中车祸工伤"]
            long_text: 长文本语义检索，与 keyword_arr 二选一
            page_no: 页码，默认 1
            page_size: 每页数量，默认 5
            sort_field: 排序字段 correlation(相关性) | time(裁判时间)
            sort_order: 排序方向 asc | desc
            court_level_arr: 法院层级 ["0"最高法, "1"高级, "2"中级, "3"基层]
            judgement_type_arr: 文书类型 ["30"判决, "31"裁决, "32"调解...]
            case_year_start: 案例裁判年份起始
            case_year_end: 案例裁判年份截止
        """
        condition: Dict[str, Any] = {}
        if keyword_arr:
            condition["keywordArr"] = keyword_arr
        if long_text:
            condition["longText"] = long_text
        if court_level_arr:
            condition["courtLevelArr"] = court_level_arr
        if judgement_type_arr:
            condition["judgementTypeArr"] = judgement_type_arr
        if case_year_start:
            condition["caseYearStart"] = case_year_start
        if case_year_end:
            condition["caseYearEnd"] = case_year_end

        payload = {
            "pageNo": page_no,
            "pageSize": page_size,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "condition": condition,
        }
        r = requests.post(
            f"{self.BASE_URL}/queryListCase",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def search_laws(
        self,
        keywords: List[str],
        field_name: str = "semantic",
        page_no: int = 1,
        page_size: int = 5,
        sort_field: str = "correlation",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        法规检索

        Args:
            keywords: 检索关键词列表
            field_name: 检索方式 "title"(关键词) | "semantic"(语义)
        """
        payload = {
            "pageNo": page_no,
            "pageSize": page_size,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "condition": {"keywords": keywords, "fieldName": field_name},
        }
        r = requests.post(
            f"{self.BASE_URL}/queryListLaw",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_law_detail(self, law_id: str, merge: bool = True) -> Dict[str, Any]:
        """获取法规全文详情"""
        r = requests.get(
            f"{self.BASE_URL}/lawInfo",
            headers=self.headers,
            params={"lawId": law_id, "merge": "true" if merge else "false"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_laws_detail_batch(self, laws: List[Dict]) -> List[Dict]:
        """批量获取法规详情"""
        results = []
        for law in laws:
            law_id = law.get("id")
            if not law_id:
                continue
            try:
                detail = self.get_law_detail(law_id)
                results.append({"id": law_id, "body": detail})
            except Exception as e:
                results.append({"id": law_id, "body": {}, "error": str(e)})
        return results
