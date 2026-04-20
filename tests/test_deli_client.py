"""
得理API客户端单元测试
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from utils.deli_client import DeliClient


@pytest.fixture
def client():
    return DeliClient(app_id="QthdBErlyaYvyXul", secret="EC5D455E6BD348CE8E18BE05926D2EBE")


def test_search_cases_with_keywords(client):
    mock_resp = {
        "success": True,
        "body": {
            "total": 1,
            "data": [{
                "id": "case001",
                "title": "王某工伤认定案",
                "courtName": "北京市中级人民法院",
                "judgementDate": "2023-01-15",
                "cause": "工伤认定",
                "summary": "上班途中发生车祸，认定为工伤。"
            }]
        }
    }
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_resp
        result = client.search_cases(keyword_arr=["工伤认定"])
        assert result["success"] is True
        assert len(result["body"]["data"]) == 1


def test_search_laws_semantic(client):
    mock_resp = {
        "success": True,
        "body": {
            "total": 2,
            "data": [
                {"id": "law001", "title": "工伤保险条例", "publisherName": "国务院"},
                {"id": "law002", "title": "工伤认定办法", "publisherName": "人力资源社会保障部"},
            ]
        }
    }
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_resp
        result = client.search_laws(keywords=["工伤认定"], field_name="semantic")
        assert result["success"] is True
        assert result["body"]["total"] == 2


def test_get_law_detail(client):
    mock_resp = {
        "success": True,
        "body": {
            "title": "工伤保险条例",
            "publisherName": "国务院",
            "publishDate": "2003-04-27",
            "lawDetailContent": "第一条 为了保障因工作遭受事故伤害..."
        }
    }
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_resp
        result = client.get_law_detail("law001")
        assert result["body"]["title"] == "工伤保险条例"
