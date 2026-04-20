"""
瀹℃€濇槑杈ㄢ€斺€旀櫤鍒ゆ硶妗堝弻鎿庣郴缁?涓诲簲鐢ㄥ叆鍙?/ Main Application Entry
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from core.qa_engine import QAEngine
from core.case_retrieval import CaseRetrievalEngine
from core.law_retrieval import LawRetrievalEngine
from core.strategy_engine import StrategyEngine
from utils.deli_client import DeliClient

load_dotenv()

app = Flask(__name__)
CORS(app)

# 鍒濆鍖栧悇寮曟搸
deli_client = DeliClient(
    app_id=os.getenv("DELI_APP_ID", "QthdBErlyaYvyXul"),
    secret=os.getenv("DELI_SECRET", "EC5D455E6BD348CE8E18BE05926D2EBE")
)
qa_engine = QAEngine()
case_engine = CaseRetrievalEngine(deli_client)
law_engine = LawRetrievalEngine(deli_client)
strategy_engine = StrategyEngine()


@app.route("/api/health", methods=["GET"])
def health():
    """鍋ュ悍妫€鏌?""
    return jsonify({"status": "ok", "service": "瀹℃€濇槑杈?鏅哄垽娉曟鍙屾搸绯荤粺"})


@app.route("/api/chat", methods=["POST"])
def chat():
    """瀵硅瘽寮忔硶寰嬮棶绛旀帴鍙?""
    data = request.get_json()
    user_query = data.get("query", "")
    session_id = data.get("session_id", "default")

    if not user_query:
        return jsonify({"error": "鏌ヨ鍐呭涓嶈兘涓虹┖"}), 400

    try:
        result = qa_engine.query(user_query, session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/case/search", methods=["POST"])
def search_cases():
    """鐩镐技妗堜緥妫€绱㈡帴鍙?""
    data = request.get_json()
    keywords = data.get("keywords", [])
    long_text = data.get("long_text", "")
    page_no = data.get("page_no", 1)
    page_size = data.get("page_size", 5)
    court_level = data.get("court_level", [])

    if not keywords and not long_text:
        return jsonify({"error": "璇锋彁渚涘叧閿瘝鎴栨鎯呮弿杩?}), 400

    try:
        result = case_engine.search(
            keywords=keywords,
            long_text=long_text,
            page_no=page_no,
            page_size=page_size,
            court_level=court_level
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/law/search", methods=["POST"])
def search_laws():
    """娉曟潯绮惧噯妫€绱㈡帴鍙?""
    data = request.get_json()
    keywords = data.get("keywords", [])
    field_name = data.get("field_name", "semantic")  # title 鎴?semantic
    page_no = data.get("page_no", 1)
    page_size = data.get("page_size", 5)

    if not keywords:
        return jsonify({"error": "璇锋彁渚涙绱㈠叧閿瘝"}), 400

    try:
        result = law_engine.search(
            keywords=keywords,
            field_name=field_name,
            page_no=page_no,
            page_size=page_size
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/law/detail", methods=["GET"])
def law_detail():
    """娉曡璇︽儏鎺ュ彛"""
    law_id = request.args.get("law_id")
    if not law_id:
        return jsonify({"error": "璇锋彁渚涙硶瑙処D"}), 400

    try:
        result = law_engine.get_detail(law_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/strategy/analyze", methods=["POST"])
def analyze_strategy():
    """璇夎绛栫暐鎺ㄦ紨鎺ュ彛锛堝鏂瑰緥甯堣瑙掞級"""
    data = request.get_json()
    complaint_text = data.get("complaint_text", "")
    case_type = data.get("case_type", "civil")  # civil/criminal/administrative

    if not complaint_text:
        return jsonify({"error": "璇蜂笂浼犺捣璇夌姸鎴栨鎯呮弿杩?}), 400

    try:
        result = strategy_engine.analyze(complaint_text, case_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/export/doc", methods=["POST"])
def export_to_doc():
    """瀵煎嚭鑷宠吘璁枃妗?""
    data = request.get_json()
    content = data.get("content", "")
    title = data.get("title", "娉曞緥鍒嗘瀽鎶ュ憡")

    try:
        from utils.export import TencentDocExporter
        exporter = TencentDocExporter()
        doc_url = exporter.export(title=title, content=content)
        return jsonify({"doc_url": doc_url, "message": "瀵煎嚭鎴愬姛"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"馃殌 瀹℃€濇槑杈ㄧ郴缁熷惎鍔ㄤ腑锛岀鍙ｏ細{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)