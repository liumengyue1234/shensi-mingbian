"""
API 路由定义
"""
from flask import Blueprint, request, jsonify
from core.qa_engine import QAEngine
from core.case_retrieval import CaseRetrievalEngine
from core.law_retrieval import LawRetrievalEngine
from core.strategy_engine import StrategyEngine
from utils.deli_client import DeliClient
import os

api_bp = Blueprint("api", __name__, url_prefix="/api")

# 懒初始化
_deli = None
_qa = None
_case_engine = None
_law_engine = None
_strategy = None


def get_engines():
    global _deli, _qa, _case_engine, _law_engine, _strategy
    if _deli is None:
        _deli = DeliClient(
            app_id=os.getenv("DELI_APP_ID", "QthdBErlyaYvyXul"),
            secret=os.getenv("DELI_SECRET", "EC5D455E6BD348CE8E18BE05926D2EBE"),
        )
        _qa = QAEngine()
        _case_engine = CaseRetrievalEngine(_deli)
        _law_engine = LawRetrievalEngine(_deli)
        _strategy = StrategyEngine()
    return _deli, _qa, _case_engine, _law_engine, _strategy


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "审思明辨-智判法案双擎系统"})


@api_bp.route("/chat", methods=["POST"])
def chat():
    """对话式法律问答"""
    data = request.get_json() or {}
    user_query = data.get("query", "").strip()
    session_id = data.get("session_id", "default")
    if not user_query:
        return jsonify({"error": "查询内容不能为空"}), 400
    _, qa, _, _, _ = get_engines()
    try:
        result = qa.query(user_query, session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/case/search", methods=["POST"])
def search_cases():
    """类案检索"""
    data = request.get_json() or {}
    _, _, case_engine, _, _ = get_engines()
    try:
        result = case_engine.search(
            keywords=data.get("keywords"),
            long_text=data.get("long_text"),
            page_no=data.get("page_no", 1),
            page_size=data.get("page_size", 5),
            court_level=data.get("court_level"),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/law/search", methods=["POST"])
def search_laws():
    """法条检索"""
    data = request.get_json() or {}
    keywords = data.get("keywords", [])
    if not keywords:
        return jsonify({"error": "请提供检索关键词"}), 400
    _, _, _, law_engine, _ = get_engines()
    try:
        result = law_engine.search(
            keywords=keywords,
            field_name=data.get("field_name", "semantic"),
            page_no=data.get("page_no", 1),
            page_size=data.get("page_size", 5),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/law/detail", methods=["GET"])
def law_detail():
    """法规详情"""
    law_id = request.args.get("law_id", "").strip()
    if not law_id:
        return jsonify({"error": "请提供法规ID"}), 400
    _, _, _, law_engine, _ = get_engines()
    try:
        result = law_engine.get_detail(law_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/strategy/analyze", methods=["POST"])
def analyze_strategy():
    """诉讼策略推演（对方律师视角）"""
    data = request.get_json() or {}
    complaint_text = data.get("complaint_text", "").strip()
    if not complaint_text:
        return jsonify({"error": "请提供起诉状或案情描述"}), 400
    _, _, _, _, strategy = get_engines()
    try:
        result = strategy.analyze(complaint_text, data.get("case_type", "civil"))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
