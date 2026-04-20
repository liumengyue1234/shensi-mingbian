"""
案例检索引擎测试
"""
import pytest
from unittest.mock import MagicMock
from core.case_retrieval import CaseRetrievalEngine


@pytest.fixture
def engine():
    mock_client = MagicMock()
    mock_client.search_cases.return_value = {
        "success": True,
        "body": {
            "total": 1,
            "data": [{
                "id": "case001",
                "title": "张某劳动合同纠纷案",
                "courtName": "上海市浦东新区人民法院",
                "courtLevel": "基层法院",
                "judgementDate": "2023-06-20",
                "caseNo": "(2023)沪0115民初1234号",
                "cause": "劳动合同纠纷",
                "summary": "用人单位违法解除劳动合同，应支付赔偿金。",
                "score": 0.95
            }]
        }
    }
    return CaseRetrievalEngine(mock_client)


def test_search_returns_parsed_cases(engine):
    result = engine.search(keywords=["劳动合同", "违法解除"])
    assert result["total"] == 1
    assert len(result["cases"]) == 1
    assert result["cases"][0]["title"] == "张某劳动合同纠纷案"
    assert result["cases"][0]["cause"] == "劳动合同纠纷"


def test_generate_report_not_empty(engine):
    cases = engine.search(keywords=["工伤"])["cases"]
    report = engine.generate_report("工伤认定纠纷", cases)
    assert "类案检索报告" in report
    assert "张某劳动合同纠纷案" in report


def test_search_empty_result():
    mock_client = MagicMock()
    mock_client.search_cases.return_value = {"success": True, "body": {"total": 0, "data": []}}
    engine = CaseRetrievalEngine(mock_client)
    result = engine.search(keywords=["极其罕见的案例关键词xyz"])
    assert result["total"] == 0
    assert result["cases"] == []
